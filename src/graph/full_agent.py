"""
Full Agent Graph - Complete deep research workflow.

This graph combines all components into the full research pipeline:
1. Clarify with user: Ensure sufficient information
2. Write research brief: Generate detailed research question
3. Supervisor subgraph: Coordinate multi-agent research
4. Final report generation: Synthesize comprehensive report

Supports checkpointing for conversation continuity.
"""

from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from src.states import AgentState, AgentInputState
from src.nodes.scope_nodes import clarify_with_user, write_research_brief
from src.nodes.report_nodes import final_report_generation
from src.graph.supervisor_graph import supervisor_agent


def build_full_agent() -> StateGraph:
    """
    Build the complete deep research agent graph.
    
    Creates a StateGraph with the following structure:
    - START -> clarify_with_user: Begin with user interaction
    - clarify_with_user -> write_research_brief: If info sufficient
    - clarify_with_user -> END: If clarification needed (returns question)
    - write_research_brief -> supervisor_subgraph: Delegate research
    - supervisor_subgraph -> final_report_generation: Synthesize findings
    - final_report_generation -> END: Complete with report
    
    Returns:
        Configured StateGraph ready for compilation
    """
    builder = StateGraph(AgentState, input=AgentInputState)
    
    # Add workflow nodes
    builder.add_node("clarify_with_user", clarify_with_user)
    builder.add_node("write_research_brief", write_research_brief)
    builder.add_node("supervisor_subgraph", supervisor_agent)
    builder.add_node("final_report_generation", final_report_generation)
    
    # Add workflow edges
    builder.add_edge(START, "clarify_with_user")
    # Note: clarify_with_user uses Command to route dynamically
    builder.add_edge("write_research_brief", "supervisor_subgraph")
    builder.add_edge("supervisor_subgraph", "final_report_generation")
    builder.add_edge("final_report_generation", END)
    
    return builder


def get_full_agent_with_checkpointer(
    checkpointer: Optional[BaseCheckpointSaver] = None
):
    """
    Get the full agent compiled with a checkpointer for conversation continuity.
    
    Args:
        checkpointer: Optional checkpoint saver. If None, uses MemorySaver.
        
    Returns:
        Compiled graph with checkpointing enabled
    """
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    return build_full_agent().compile(checkpointer=checkpointer)


# Compile the deep researcher agent (without checkpointer for basic use)
deep_researcher = build_full_agent().compile()