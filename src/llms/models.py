"""LLM model configurations for the Deep Research Agent."""

from langchain_groq import ChatGroq

from .config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, WRITER_MAX_TOKENS


def get_main_model(temperature: float = DEFAULT_TEMPERATURE) -> ChatGroq:
    """Get the main model for research and decision-making.
    
    Args:
        temperature: Model temperature for response variability
        
    Returns:
        Configured ChatGroq model instance
    """
    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=temperature
    )


def get_summarization_model(temperature: float = DEFAULT_TEMPERATURE) -> ChatGroq:
    """Get the model for webpage content summarization.
    
    Args:
        temperature: Model temperature for response variability
        
    Returns:
        Configured ChatGroq model instance for summarization
    """
    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=temperature
    )


def get_compress_model(temperature: float = DEFAULT_TEMPERATURE) -> ChatGroq:
    """Get the model for research compression.
    
    Args:
        temperature: Model temperature for response variability
        
    Returns:
        Configured ChatGroq model instance for compression
    """
    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=temperature
    )


def get_supervisor_model(temperature: float = DEFAULT_TEMPERATURE) -> ChatGroq:
    """Get the model for supervisor agent coordination.
    
    Args:
        temperature: Model temperature for response variability
        
    Returns:
        Configured ChatGroq model instance for supervisor
    """
    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=temperature
    )


def get_writer_model(
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = WRITER_MAX_TOKENS
) -> ChatGroq:
    """Get the model for final report generation.
    
    Args:
        temperature: Model temperature for response variability
        max_tokens: Maximum tokens for report output
        
    Returns:
        Configured ChatGroq model instance for report writing
    """
    return ChatGroq(
        model=DEFAULT_MODEL,
        temperature=temperature,
        max_tokens=max_tokens
    )