"""
Supervisor nodes - Multi-agent research coordination.

These nodes handle the supervisor workflow:
1. Strategic research planning and delegation
2. Parallel research agent execution
3. Research result aggregation
"""

import asyncio
from typing import Literal, TYPE_CHECKING

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    ToolMessage,
    filter_messages
)
from langgraph.graph import END
from langgraph.types import Command

from src.states import SupervisorState
from src.prompts import LEAD_RESEARCHER_PROMPT
from src.llms import (
    get_supervisor_model,
    get_today_str,
    MAX_RESEARCHER_ITERATIONS,
    MAX_CONCURRENT_RESEARCHERS
)
from src.tools import ConductResearch, ResearchComplete, think_tool

# Handle circular import for researcher_agent
if TYPE_CHECKING:
    from src.graph import researcher_agent


def get_researcher_agent():
    """Lazy import of researcher_agent to avoid circular imports."""
    from src.graph import researcher_agent
    return researcher_agent


# Supervisor tools configuration
supervisor_tools = [ConductResearch, ResearchComplete, think_tool]


def get_supervisor_model_with_tools():
    """Get the supervisor model with tools bound."""
    model = get_supervisor_model()
    return model.bind_tools(supervisor_tools)


def get_notes_from_tool_calls(messages: list[BaseMessage]) -> list[str]:
    """
    Extract research notes from ToolMessage objects in supervisor message history.
    
    This function retrieves the compressed research findings that sub-agents
    return as ToolMessage content. When the supervisor delegates research to
    sub-agents via ConductResearch tool calls, each sub-agent returns its
    compressed findings as the content of a ToolMessage.
    
    Args:
        messages: List of messages from supervisor's conversation history
        
    Returns:
        List of research note strings extracted from ToolMessage objects
    """
    return [tool_msg.content for tool_msg in filter_messages(messages, include_types="tool")]


async def supervisor(state: SupervisorState) -> Command[Literal["supervisor_tools"]]:
    """
    Coordinate research activities.
    
    Analyzes the research brief and current progress to decide:
    - What research topics need investigation
    - Whether to conduct parallel research
    - When research is complete
    
    Args:
        state: Current supervisor state with messages and research progress
        
    Returns:
        Command to proceed to supervisor_tools node with updated state
    """
    supervisor_messages = state.get("supervisor_messages", [])
    supervisor_model_with_tools = get_supervisor_model_with_tools()
    
    # Prepare system message with current date and constraints
    system_message = LEAD_RESEARCHER_PROMPT.format(
        date=get_today_str(),
        max_concurrent_research_units=MAX_CONCURRENT_RESEARCHERS,
        max_researcher_iterations=MAX_RESEARCHER_ITERATIONS
    )
    messages = [SystemMessage(content=system_message)] + list(supervisor_messages)
    
    # Make decision about next research steps
    response = await supervisor_model_with_tools.ainvoke(messages)
    
    return Command(
        goto="supervisor_tools",
        update={
            "supervisor_messages": [response],
            "research_iterations": state.get("research_iterations", 0) + 1
        }
    )


async def supervisor_tools(state: SupervisorState) -> Command[Literal["supervisor", "__end__"]]:
    """
    Execute supervisor decisions - either conduct research or end the process.
    
    Handles:
    - Executing think_tool calls for strategic reflection
    - Launching parallel research agents for different topics
    - Aggregating research results
    - Determining when research is complete
    
    Args:
        state: Current supervisor state with messages and iteration count
        
    Returns:
        Command to continue supervision, end process, or handle errors
    """
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    most_recent_message = supervisor_messages[-1]
    
    # Initialize variables for single return pattern
    tool_messages = []
    all_raw_notes = []
    next_step = "supervisor"  # Default next step
    should_end = False
    
    # Check exit criteria first
    exceeded_iterations = research_iterations >= MAX_RESEARCHER_ITERATIONS
    no_tool_calls = not most_recent_message.tool_calls
    research_complete = any(
        tool_call["name"] == "ResearchComplete"
        for tool_call in (most_recent_message.tool_calls or [])
    )
    
    if exceeded_iterations or no_tool_calls or research_complete:
        should_end = True
        next_step = END
    else:
        try:
            # Separate think_tool calls from ConductResearch calls
            think_tool_calls = [
                tool_call for tool_call in most_recent_message.tool_calls
                if tool_call["name"] == "think_tool"
            ]
            
            conduct_research_calls = [
                tool_call for tool_call in most_recent_message.tool_calls
                if tool_call["name"] == "ConductResearch"
            ]
            
            # Handle think_tool calls (synchronous)
            for tool_call in think_tool_calls:
                observation = think_tool.invoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(
                        content=observation,
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    )
                )
            
            # Handle ConductResearch calls (asynchronous)
            if conduct_research_calls:
                researcher_agent = get_researcher_agent()
                
                # Launch parallel research agents
                coros = [
                    researcher_agent.ainvoke({
                        "researcher_messages": [
                            HumanMessage(content=tool_call["args"]["research_topic"])
                        ],
                        "research_topic": tool_call["args"]["research_topic"]
                    })
                    for tool_call in conduct_research_calls
                ]
                
                # Wait for all research to complete
                tool_results = await asyncio.gather(*coros)
                
                # Format research results as tool messages
                research_tool_messages = [
                    ToolMessage(
                        content=result.get("compressed_research", "Error synthesizing research report"),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    ) for result, tool_call in zip(tool_results, conduct_research_calls)
                ]
                
                tool_messages.extend(research_tool_messages)
                
                # Aggregate raw notes from all research
                all_raw_notes = [
                    "\n".join(result.get("raw_notes", []))
                    for result in tool_results
                ]
                
        except Exception as e:
            print(f"Error in supervisor tools: {e}")
            should_end = True
            next_step = END
    
    # Single return point with appropriate state updates
    if should_end:
        return Command(
            goto=next_step,
            update={
                "notes": get_notes_from_tool_calls(supervisor_messages),
                "research_brief": state.get("research_brief", "")
            }
        )
    else:
        return Command(
            goto=next_step,
            update={
                "supervisor_messages": tool_messages,
                "raw_notes": all_raw_notes
            }
        )