"""
Deep Research Agent - FastAPI Application

A production-ready REST API for the multi-agent deep research system.
Supports both single-turn and multi-turn conversational research with
checkpointing for conversation continuity.

Features:
- Async research endpoint with streaming support
- Conversation management with thread-based sessions
- Health check and status endpoints
- Configurable recursion limits and timeouts
"""

import os
import uuid
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Configure environment
os.environ.pop("LANGCHAIN_TRACING", None)
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")

# Import the deep research agent
from src.graph import get_full_agent_with_checkpointer


# Global checkpointer for conversation persistence
checkpointer = MemorySaver()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("🚀 Deep Research Agent API starting up...")
    print("✅ Agent initialized and ready")
    yield
    # Shutdown
    print("👋 Deep Research Agent API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Deep Research Agent API",
    description="""
    A multi-agent deep research system powered by LangGraph.
    
    ## Features
    - **Intelligent Clarification**: Asks follow-up questions when needed
    - **Parallel Research**: Spawns multiple research agents for complex topics
    - **Comprehensive Reports**: Generates well-structured markdown reports with citations
    - **Conversation Memory**: Maintains context across multiple interactions
    
    ## Usage
    1. Start a new research session with POST /research
    2. Continue the conversation using the same thread_id
    3. Retrieve the final report from the response
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    query: str = Field(
        ...,
        description="The research question or topic to investigate",
        min_length=1,
        max_length=10000,
        examples=["Compare OpenAI and Anthropic approaches to AI safety"]
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="Thread ID for conversation continuity. If not provided, a new thread is created."
    )
    recursion_limit: int = Field(
        default=50,
        ge=10,
        le=100,
        description="Maximum recursion depth for the research workflow"
    )


class MessageResponse(BaseModel):
    """Individual message in the conversation."""
    role: str = Field(description="Message role: 'human' or 'assistant'")
    content: str = Field(description="Message content")


class ResearchResponse(BaseModel):
    """Response model for research endpoint."""
    thread_id: str = Field(description="Thread ID for conversation continuity")
    messages: List[MessageResponse] = Field(description="Conversation messages")
    final_report: Optional[str] = Field(
        default=None,
        description="Final research report in markdown format (if research is complete)"
    )
    research_brief: Optional[str] = Field(
        default=None,
        description="Generated research brief (if available)"
    )
    status: str = Field(description="Current status: 'clarification_needed', 'researching', or 'complete'")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    services: Dict[str, str]


class ThreadInfo(BaseModel):
    """Thread information response model."""
    thread_id: str
    message_count: int
    has_final_report: bool


# ============================================================================
# Helper Functions
# ============================================================================

def serialize_messages(messages: List[BaseMessage]) -> List[MessageResponse]:
    """Convert LangChain messages to API response format."""
    serialized = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            serialized.append(MessageResponse(role="human", content=str(msg.content)))
        elif isinstance(msg, AIMessage):
            serialized.append(MessageResponse(role="assistant", content=str(msg.content)))
        elif isinstance(msg, str):
            serialized.append(MessageResponse(role="assistant", content=msg))
    return serialized


def determine_status(result: Dict[str, Any]) -> str:
    """Determine the current research status from result state."""
    if result.get("final_report"):
        return "complete"
    
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]
        content = str(last_message.content if hasattr(last_message, 'content') else last_message)
        # Check if the last message is a clarifying question
        if "?" in content and not result.get("research_brief"):
            return "clarification_needed"
    
    return "researching"


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Deep Research Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint for monitoring."""
    groq_configured = bool(os.getenv("GROQ_API_KEY"))
    tavily_configured = bool(os.getenv("TAVILY_API_KEY"))
    
    return HealthResponse(
        status="healthy" if groq_configured and tavily_configured else "degraded",
        version="1.0.0",
        services={
            "groq": "configured" if groq_configured else "missing API key",
            "tavily": "configured" if tavily_configured else "missing API key",
            "langgraph": "ready"
        }
    )


@app.post("/research", response_model=ResearchResponse, tags=["Research"])
async def conduct_research(request: ResearchRequest):
    """
    Conduct deep research on a given topic.
    
    This endpoint initiates or continues a research conversation. The agent will:
    1. Ask clarifying questions if needed
    2. Generate a research brief
    3. Delegate research to specialized sub-agents
    4. Synthesize findings into a comprehensive report
    
    Use the same thread_id to continue a conversation.
    """
    try:
        # Get or create thread ID
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Configure the agent run
        config = {
            "configurable": {
                "thread_id": thread_id,
                "recursion_limit": request.recursion_limit
            }
        }
        
        # Get the agent with checkpointer
        agent = get_full_agent_with_checkpointer(checkpointer)
        
        # Run the research
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=request.query)]},
            config=config
        )
        
        # Extract and serialize results
        messages = result.get("messages", [])
        final_report = result.get("final_report")
        research_brief = result.get("research_brief")
        
        return ResearchResponse(
            thread_id=thread_id,
            messages=serialize_messages(messages),
            final_report=final_report,
            research_brief=research_brief,
            status=determine_status(result)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )


@app.post("/research/new", response_model=ResearchResponse, tags=["Research"])
async def start_new_research(request: ResearchRequest):
    """
    Start a fresh research session (always creates new thread).
    
    Use this endpoint when you want to ensure a new conversation
    without any previous context.
    """
    # Force new thread
    request.thread_id = str(uuid.uuid4())
    return await conduct_research(request)


@app.get("/research/{thread_id}/status", tags=["Research"])
async def get_research_status(thread_id: str):
    """
    Get the current status of a research thread.
    
    Returns basic information about the thread's state.
    """
    try:
        agent = get_full_agent_with_checkpointer(checkpointer)
        
        config = {"configurable": {"thread_id": thread_id}}
        state = await agent.aget_state(config)
        
        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        messages = state.values.get("messages", [])
        final_report = state.values.get("final_report")
        
        return {
            "thread_id": thread_id,
            "message_count": len(messages),
            "has_final_report": bool(final_report),
            "status": determine_status(state.values)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/{thread_id}/report", tags=["Research"])
async def get_research_report(thread_id: str):
    """
    Retrieve the final report for a completed research thread.
    
    Returns the full markdown report if research is complete.
    """
    try:
        agent = get_full_agent_with_checkpointer(checkpointer)
        
        config = {"configurable": {"thread_id": thread_id}}
        state = await agent.aget_state(config)
        
        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        final_report = state.values.get("final_report")
        
        if not final_report:
            raise HTTPException(
                status_code=400,
                detail="Research not complete. Continue the conversation to generate a report."
            )
        
        return {
            "thread_id": thread_id,
            "report": final_report,
            "research_brief": state.values.get("research_brief")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/{thread_id}/messages", tags=["Research"])
async def get_conversation_history(thread_id: str):
    """
    Retrieve the full conversation history for a thread.
    """
    try:
        agent = get_full_agent_with_checkpointer(checkpointer)
        
        config = {"configurable": {"thread_id": thread_id}}
        state = await agent.aget_state(config)
        
        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        messages = state.values.get("messages", [])
        
        return {
            "thread_id": thread_id,
            "messages": serialize_messages(messages),
            "count": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )