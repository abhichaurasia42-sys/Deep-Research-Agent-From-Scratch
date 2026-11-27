"""
Scope nodes - User clarification and research brief generation.

These nodes handle the initial scoping phase of the research workflow:
1. Determine if user's request needs clarification
2. Generate a comprehensive research brief from conversation history
"""

from typing import Literal

from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import END
from langgraph.types import Command

from src.states import AgentState, ClarifyWithUser, ResearchQuestion
from src.prompts import CLARIFY_WITH_USER_INSTRUCTIONS, TRANSFORM_MESSAGES_INTO_RESEARCH_TOPIC_PROMPT
from src.llms import get_main_model, get_today_str


def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:
    """
    Determine if the user's request contains sufficient information to proceed with research.
    
    This node analyzes the conversation history and decides whether to:
    1. Ask a clarifying question if more information is needed
    2. Proceed to research brief generation if information is sufficient
    
    Args:
        state: Current agent state containing message history
        
    Returns:
        Command to either end (with clarifying question) or proceed to write_research_brief
    """
    model = get_main_model()
    structured_output_model = model.with_structured_output(ClarifyWithUser, method="json_schema")
    
    response = structured_output_model.invoke(
        [
            HumanMessage(content=CLARIFY_WITH_USER_INSTRUCTIONS.format(
                messages=get_buffer_string(messages=state['messages']),
                date=get_today_str()
            ))
        ]
    )
    
    # Route based on clarification need
    if response.need_clarification:
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        return Command(
            goto='write_research_brief',
            update={"messages": [AIMessage(content=response.verification)]}
        )


def write_research_brief(state: AgentState) -> dict:
    """
    Transform the conversation history into a comprehensive research brief.
    
    This node takes the user's messages and generates a detailed, concrete
    research question that will guide the research process.
    
    Args:
        state: Current agent state containing message history
        
    Returns:
        Dictionary with research_brief and initial supervisor_messages
    """
    model = get_main_model()
    structured_output_model = model.with_structured_output(ResearchQuestion, method="json_schema")
    
    response = structured_output_model.invoke(
        [
            HumanMessage(content=TRANSFORM_MESSAGES_INTO_RESEARCH_TOPIC_PROMPT.format(
                messages=get_buffer_string(messages=state.get('messages', [])),
                date=get_today_str()
            ))
        ]
    )
    
    return {
        "research_brief": response.research_brief,
        "supervisor_messages": [HumanMessage(content=f"{response.research_brief}.")]
    }