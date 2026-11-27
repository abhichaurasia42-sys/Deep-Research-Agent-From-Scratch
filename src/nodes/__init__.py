"""
Nodes module - Core workflow node functions.

This module contains all node implementations for the deep research agent:
- Scope nodes: User clarification and research brief generation
- Researcher nodes: LLM calls, tool execution, and research compression
- Supervisor nodes: Multi-agent coordination and research delegation
- Report nodes: Final report generation
"""

from src.nodes.scope_nodes import clarify_with_user, write_research_brief
from src.nodes.researcher_nodes import llm_call, tool_node, compress_research, should_continue
from src.nodes.supervisor_nodes import supervisor, supervisor_tools, get_notes_from_tool_calls
from src.nodes.report_nodes import final_report_generation

__all__ = [
    # Scope nodes
    "clarify_with_user",
    "write_research_brief",
    # Researcher nodes
    "llm_call",
    "tool_node",
    "compress_research",
    "should_continue",
    # Supervisor nodes
    "supervisor",
    "supervisor_tools",
    "get_notes_from_tool_calls",
    # Report nodes
    "final_report_generation",
]