"""State definitions for the Research Agent."""

import operator
from typing import Annotated, List, Sequence

from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ResearcherState(TypedDict):
    """State for the research agent containing message history and research metadata."""
    
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]
    tool_call_iterations: int
    research_topic: str
    compressed_research: str
    raw_notes: Annotated[List[str], operator.add]


class ResearcherOutputState(TypedDict):
    """Output state for the research agent containing final research results."""
    
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]
    compressed_research: str
    raw_notes: Annotated[List[str], operator.add]