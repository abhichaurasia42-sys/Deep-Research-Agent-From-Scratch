"""State definitions for the Deep Research Agent system."""

import operator
from typing import Annotated, List, Sequence, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState


class AgentInputState(MessagesState):
    """Input state for the full agent - only contains messages from user input."""
    pass


class AgentState(MessagesState):
    """Main state for the multi-agent research system."""
    
    # Research brief generated from the user conversation history
    research_brief: Optional[str] = None
    # Messages exchanged with the supervisor agent for coordination
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages] = []
    # Raw unprocessed research notes collected during the research phase
    raw_notes: Annotated[List[str], operator.add] = []
    # Processed and structured notes ready for report generation
    notes: Annotated[List[str], operator.add] = []
    # Final formatted research report
    final_report: str = ""