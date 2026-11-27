"""
Deep Research Agent - A multi-agent research system powered by LangGraph.

This package provides a modular implementation of a deep research agent
that can conduct comprehensive research on any topic using:
- Intelligent clarification for ambiguous queries
- Parallel research agents for complex topics
- Web search with content summarization
- Comprehensive report generation with citations

Modules:
    states: State definitions for all workflow components
    prompts: Prompt templates for LLM interactions
    llms: Model configuration and factory functions
    tools: Research tools (search, reflection)
    nodes: Workflow node implementations
    graph: LangGraph workflow definitions

Usage:
    from src.graph import deep_researcher, get_full_agent_with_checkpointer
    
    # Simple usage
    result = await deep_researcher.ainvoke({"messages": [HumanMessage(content="...")]})
    
    # With checkpointing
    agent = get_full_agent_with_checkpointer()
    result = await agent.ainvoke({"messages": [...]}, config={"configurable": {"thread_id": "1"}})
"""

__version__ = "1.0.0"
__author__ = "Deep Research Agent"

from src.states import AgentState, AgentInputState, ResearcherState, SupervisorState
from src.graph import deep_researcher, get_full_agent_with_checkpointer

__all__ = [
    "AgentState",
    "AgentInputState", 
    "ResearcherState",
    "SupervisorState",
    "deep_researcher",
    "get_full_agent_with_checkpointer",
]