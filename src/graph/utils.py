"""
Graph utilities - Visualization and debugging helpers.

Provides utilities for graph inspection and visualization.
"""

from typing import Optional


def display_graph(graph, xray: bool = False):
    """
    Display a graph visualization in Jupyter notebook.
    
    Args:
        graph: Compiled LangGraph to visualize
        xray: If True, show subgraph details
    """
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph(xray=xray).draw_mermaid_png()))
    except ImportError:
        print("IPython not available. Graph visualization requires Jupyter environment.")
    except Exception as e:
        print(f"Could not display graph: {e}")


def get_graph_mermaid(graph, xray: bool = False) -> Optional[str]:
    """
    Get Mermaid diagram code for a graph.
    
    Args:
        graph: Compiled LangGraph
        xray: If True, include subgraph details
        
    Returns:
        Mermaid diagram string or None if error
    """
    try:
        return graph.get_graph(xray=xray).draw_mermaid()
    except Exception as e:
        print(f"Could not generate Mermaid diagram: {e}")
        return None