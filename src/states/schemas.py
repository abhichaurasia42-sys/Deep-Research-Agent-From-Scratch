"""Pydantic schemas for structured LLM outputs."""

from pydantic import BaseModel, Field


class ClarifyWithUser(BaseModel):
    """Schema for user clarification responses."""
    
    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question."
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope."
    )
    verification: str = Field(
        description="Verification message that we will start research after the user has provided the necessary information."
    )


class ResearchQuestion(BaseModel):
    """Schema for research brief generation."""
    
    research_brief: str = Field(
        description="A research question that will be used to guide the research."
    )


class Summary(BaseModel):
    """Schema for webpage content summarization."""
    
    summary: str = Field(
        description="Concise summary of the webpage content"
    )
    key_excerpts: str = Field(
        description="Important quotes and excerpts from the content"
    )