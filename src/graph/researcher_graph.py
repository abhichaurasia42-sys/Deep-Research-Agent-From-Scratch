"""
Researcher Graph - Iterative research agent workflow.

This graph implements the core research loop:
1. LLM analyzes current state and decides on tool calls
2. Tools execute web searches and gather information
3. Research is compressed when complete

The agent follows a ReAct-style pattern with explicit
reflection via think_tool after each search.
"""

from langgraph.graph import StateGraph, START, END

from src.states import ResearcherState, ResearcherOutputState
from src.nodes.researcher_nodes import (
    llm_call,
    tool_node,
    compress_research,
    should_continue
)


def build_researcher_graph() -> StateGraph:
    """
    Build the researcher agent graph.
    
    Creates a StateGraph with the following structure:
    - START -> llm_call: Begin with LLM decision
    - llm_call -> tool_node: If tool calls present
    - llm_call -> compress_research: If no tool calls (research complete)
    - tool_node -> llm_call: Continue research loop
    - compress_research -> END: Finish with compressed findings
    
    Returns:
        Configured StateGraph ready for compilation
    """
    builder = StateGraph(ResearcherState, output=ResearcherOutputState)
    
    # Add nodes
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)
    builder.add_node("compress_research", compress_research)
    
    # Add edges
    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges(
        "llm_call",
        should_continue,
        {
            "tool_node": "tool_node",
            "compress_research": "compress_research"
        }
    )
    builder.add_edge("tool_node", "llm_call")
    builder.add_edge("compress_research", END)
    
    return builder


# Compile the researcher agent for use in supervisor
researcher_agent = build_researcher_graph().compile()