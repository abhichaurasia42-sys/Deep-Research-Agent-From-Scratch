"""State definitions for the Research Supervisor Agent."""

import operator
from typing import Annotated, List, Sequence

from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SupervisorState(TypedDict):
    """State for the multi-agent research supervisor."""
    
    # Messages exchanged with supervisor for coordination and decision-making
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]
    # Detailed research brief that guides the overall research direction
    research_brief: str
    # Processed and structured notes ready for final report generation
    notes: Annotated[List[str], operator.add]
    # Counter tracking the number of research iterations performed
    research_iterations: int
    # Raw unprocessed research notes collected from sub-agent research
    raw_notes: Annotated[List[str], operator.add]