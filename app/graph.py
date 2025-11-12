"""LangGraph workflow orchestration for the AI Task Router."""
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from app.schemas import TaskSpec, RouteDecision, AgentResult, FinalPackage
from app.agents import router, run_agent, merger_and_qa, formatter
from app.tools import fetch_url_or_pdf
from app.config import Config
import logging

# Set up logging (production: WARNING level)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class RouterState(TypedDict):
    """State object for the LangGraph workflow."""
    task: TaskSpec
    context: Dict[str, Any]
    route: RouteDecision
    results: List[AgentResult]
    final_output: str
    package: Dict[str, Any]

def fetch_source_node(state: RouterState) -> RouterState:
    """Node: Fetch source content if URL is provided."""
    task = state["task"]
    context = state.get("context", {})
    
    if task.source_url:
        try:
            source_text = fetch_url_or_pdf(task.source_url)
            context["source_text"] = source_text
        except Exception as e:
            context["source_text"] = ""
            context["source_error"] = str(e)
    else:
        context["source_text"] = ""
    
    state["context"] = context
    return state

def router_node(state: RouterState) -> RouterState:
    """Node: Router decides which agents to run."""
    task = state["task"]
    route_decision = router(task)
    state["route"] = route_decision
    return state


def merger_node(state: RouterState) -> RouterState:
    """Node: Merger/QA combines all agent outputs."""
    task = state["task"]
    results = state.get("results", [])
    context = state["context"]
    
    final_output = merger_and_qa(task, results, context)
    state["final_output"] = final_output
    return state

def formatter_node(state: RouterState) -> RouterState:
    """Node: Format final package."""
    route = state["route"]
    results = state.get("results", [])
    final_output = state["final_output"]
    
    package = formatter(route, results, final_output)
    state["package"] = package
    return state

def execute_agents_node(state: RouterState) -> RouterState:
    """Node: Execute all selected agents sequentially."""
    route = state.get("route")
    task = state["task"]
    context = state["context"]
    results = state.get("results", [])
    
    if not route:
        return state
    
    # Execute each agent in the order specified by the route
    for role in route.selected_agents:
        result = run_agent(role, task, context)
        results.append(result)
        
        # Update context with agent output for next agents
        context[f"{role}_output"] = result.content
        if result.citations:
            context.setdefault("citations", []).extend(result.citations)
    
    state["results"] = results
    state["context"] = context
    return state

def build_graph() -> StateGraph:
    """Build and return the LangGraph workflow."""
    workflow = StateGraph(RouterState)
    
    # Add nodes
    workflow.add_node("fetch_source", fetch_source_node)
    workflow.add_node("router", router_node)
    workflow.add_node("execute_agents", execute_agents_node)
    workflow.add_node("merger", merger_node)
    workflow.add_node("formatter", formatter_node)
    
    # Set entry point
    workflow.set_entry_point("fetch_source")
    
    # Add edges - simple linear flow
    workflow.add_edge("fetch_source", "router")
    workflow.add_edge("router", "execute_agents")
    workflow.add_edge("execute_agents", "merger")
    workflow.add_edge("merger", "formatter")
    workflow.add_edge("formatter", END)
    
    return workflow.compile()

def execute_pipeline(task: TaskSpec) -> FinalPackage:
    """
    Execute the complete pipeline for a task.
    
    Args:
        task: The task specification
    
    Returns:
        FinalPackage with routing trace and results
    """
    # Initialize state
    initial_state: RouterState = {
        "task": task,
        "context": {},
        "route": None,  # Will be set by router node
        "results": [],
        "final_output": "",
        "package": {}
    }
    
    # Build and run graph
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    # Extract and validate package
    package_dict = final_state["package"]
    package = FinalPackage(**package_dict)
    
    return package

