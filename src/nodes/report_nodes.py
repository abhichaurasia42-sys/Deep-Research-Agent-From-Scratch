"""
Report nodes - Final report generation.

This module handles the synthesis of research findings into
a comprehensive, well-structured final report.
"""

from langchain_core.messages import HumanMessage

from src.states import AgentState
from src.prompts import FINAL_REPORT_GENERATION_PROMPT
from src.llms import get_writer_model, get_today_str


async def final_report_generation(state: AgentState) -> dict:
    """
    Generate the final comprehensive research report.
    
    Synthesizes all research findings into a well-structured report
    with proper citations, headings, and source references.
    
    Args:
        state: Current agent state containing notes and research brief
        
    Returns:
        Dictionary with final_report and updated messages
    """
    writer_model = get_writer_model()
    notes = state.get("notes", [])
    
    # Combine all research findings
    findings = "\n".join(notes)
    
    # Build the report generation prompt
    final_report_prompt = FINAL_REPORT_GENERATION_PROMPT.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str()
    )
    
    # Generate the final report
    final_report = await writer_model.ainvoke([HumanMessage(content=final_report_prompt)])
    
    return {
        "final_report": final_report.content,
        "messages": [f"Here is the final report: {final_report.content}"],
    }