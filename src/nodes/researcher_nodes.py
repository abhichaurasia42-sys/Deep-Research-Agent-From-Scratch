"""
Researcher nodes - Core research agent node implementations.

These nodes handle the iterative research process:
1. LLM decision-making for tool calls
2. Tool execution for web searches
3. Research compression for context management
"""

from typing import Literal

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages

from src.states import ResearcherState
from src.prompts import (
    RESEARCH_AGENT_PROMPT,
    COMPRESS_RESEARCH_SYSTEM_PROMPT,
    COMPRESS_RESEARCH_HUMAN_MESSAGE
)
from src.llms import get_main_model, get_compress_model, get_today_str
from src.tools import tavily_search, think_tool


# Research tools configuration
tools = [tavily_search, think_tool]
tools_by_name = {tool.name: tool for tool in tools}


def get_model_with_tools():
    """Get the main model with research tools bound."""
    model = get_main_model()
    return model.bind_tools(tools=tools)


def llm_call(state: ResearcherState) -> dict:
    """
    Analyze current state and decide on next actions.
    
    The model analyzes the current conversation state and decides whether to:
    1. Call search tools to gather more information
    2. Provide a final answer based on gathered information
    
    Args:
        state: Current researcher state with message history
        
    Returns:
        Updated state with the model's response
    """
    model_with_tools = get_model_with_tools()
    
    return {
        "researcher_messages": [
            model_with_tools.invoke(
                [SystemMessage(content=RESEARCH_AGENT_PROMPT.format(date=get_today_str()))] 
                + list(state['researcher_messages'])
            )
        ]
    }


def tool_node(state: ResearcherState) -> dict:
    """
    Execute all tool calls from the previous LLM response.
    
    Processes each tool call from the last message and returns
    the results as ToolMessage objects.
    
    Args:
        state: Current researcher state with pending tool calls
        
    Returns:
        Updated state with tool execution results
    """
    tool_calls = state['researcher_messages'][-1].tool_calls
    
    observations = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call['name']]
        observation = tool.invoke(tool_call['args'])
        observations.append(observation)
    
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call['name'],
            tool_call_id=tool_call['id']
        ) for observation, tool_call in zip(observations, tool_calls)
    ]
    
    return {"researcher_messages": tool_outputs}


def compress_research(state: ResearcherState) -> dict:
    """
    Compress and synthesize research findings.
    
    This node takes the accumulated research messages and compresses them
    into a structured format while preserving all relevant information.
    
    Args:
        state: Current researcher state with research messages
        
    Returns:
        Dictionary with compressed_research and raw_notes
    """
    compress_model = get_compress_model()
    system_message = COMPRESS_RESEARCH_SYSTEM_PROMPT.format(date=get_today_str())
    
    # Cap messages to avoid oversized requests
    msgs = state.get("researcher_messages", [])
    max_ctx_messages = 12
    msgs = list(msgs[-max_ctx_messages:])
    
    # Build compression prompt
    human_message = COMPRESS_RESEARCH_HUMAN_MESSAGE.format(
        research_topic=state.get("research_topic", "")
    )
    
    messages = [SystemMessage(content=system_message)] + msgs + [HumanMessage(content=human_message)]
    response = compress_model.invoke(messages)
    
    # Extract raw notes from tool and AI messages
    raw_notes = [
        str(m.content) for m in filter_messages(
            state["researcher_messages"],
            include_types=["tool", "ai"]
        )
    ]
    
    return {
        "compressed_research": str(response.content),
        "raw_notes": ["\n".join(raw_notes)]
    }


def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """
    Determine whether to continue research or provide final answer.
    
    Routing function that checks if the LLM made tool calls to decide
    whether to continue the research loop or compress findings.
    
    Args:
        state: Current researcher state
        
    Returns:
        "tool_node": Continue to tool execution
        "compress_research": Stop and compress research
    """
    messages = state["researcher_messages"]
    last_message = messages[-1]
    
    # If the LLM makes a tool call, continue to tool execution
    if last_message.tool_calls:
        return "tool_node"
    
    # Otherwise, compress the research
    return "compress_research"