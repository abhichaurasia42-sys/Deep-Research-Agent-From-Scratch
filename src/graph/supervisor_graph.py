"""
Supervisor Graph - Multi-agent research coordination.

This graph implements the research supervisor workflow:
1. Supervisor analyzes research brief and plans approach
2. Delegates research tasks to parallel sub-agents
3. Aggregates results and determines completion

The supervisor can spawn multiple researcher agents
concurrently for different sub-topics.
"""

from langgraph.graph import StateGraph, START

from src.states import SupervisorState
from src.nodes.supervisor_nodes import supervisor, supervisor_tools


def build_supervisor_graph() -> StateGraph:
    """
    Build the supervisor agent graph.
    
    Creates a StateGraph with the following structure:
    - START -> supervisor: Begin with supervisor planning
    - supervisor -> supervisor_tools: Execute decisions
    - supervisor_tools -> supervisor: Continue if more research needed
    - supervisor_tools -> END: Complete when research finished
    
    Returns:
        Configured StateGraph ready for compilation
    """
    builder = StateGraph(SupervisorState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor)
    builder.add_node("supervisor_tools", supervisor_tools)
    
    # Add edges
    builder.add_edge(START, "supervisor")
    # Note: supervisor_tools uses Command to route dynamically
    
    return builder


# Compile the supervisor agent
supervisor_agent = build_supervisor_graph().compile()