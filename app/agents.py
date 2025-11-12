"""Agent implementations for the AI Task Router."""
import json
import re
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.schemas import TaskSpec, RouteDecision, AgentResult, Role
from app.prompts import (
    build_router_prompt,
    build_researcher_prompt,
    build_summarizer_prompt,
    build_writer_prompt,
    build_coder_prompt,
    build_analyst_prompt,
    build_merger_prompt,
    SYSTEM_PROMPT
)
from app.config import Config

# Initialize LLM
llm = ChatOpenAI(
    model=Config.MODEL_NAME,
    temperature=Config.TEMPERATURE,
    max_tokens=Config.MAX_TOKENS,
    api_key=Config.OPENAI_API_KEY
)

# Heuristic routing rules
HEURISTICS = [
    ("researcher", lambda t: bool(t.source_url)),
    ("summarizer", lambda t: any(k in t.user_query.lower() for k in [
        "summarize", "summary", "tl;dr", "brief", "overview", "summarise"
    ])),
    ("writer", lambda t: any(k in t.user_query.lower() for k in [
        "write", "draft", "post", "email", "linkedin", "article", "blog", "content"
    ])),
    ("coder", lambda t: any(k in t.user_query.lower() for k in [
        "code", "python", "regex", "error", "stack trace", "function", "script", "program"
    ])),
    ("analyst", lambda t: any(k in t.user_query.lower() for k in [
        "csv", "table", "kpi", "metrics", "trend", "analyze", "analysis", "insight", "data"
    ])),
]

def heuristic_route(task: TaskSpec) -> List[str]:
    """Apply heuristic rules to determine initial agent selection."""
    picks = [role for role, cond in HEURISTICS if cond(task)]
    # Default to summarizer if no heuristics match
    return picks if picks else ["summarizer"]

def router(task: TaskSpec) -> RouteDecision:
    """
    Router agent: determines which agents to run and in what order.
    
    Uses heuristics first, then LLM refinement for ordering and confidence.
    """
    # Get heuristic route
    base_route = heuristic_route(task)
    
    # Build prompt for LLM refinement
    prompt = build_router_prompt(task, base_route)
    
    try:
        # Get LLM response
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Try to extract JSON from response
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        # Parse JSON
        try:
            route_data = json.loads(content)
            selected_agents = route_data.get("selected_agents", base_route)
            rationale = route_data.get("rationale", "Heuristic routing with LLM refinement")
            confidence = float(route_data.get("confidence", 0.7))
        except json.JSONDecodeError:
            # Fallback: try to extract list from response
            if "selected_agents" in content:
                # Try to find JSON-like structure
                match = re.search(r'selected_agents["\']?\s*:\s*\[(.*?)\]', content)
                if match:
                    agents_str = match.group(1)
                    selected_agents = [a.strip().strip('"\'') for a in agents_str.split(',')]
                else:
                    selected_agents = base_route
            else:
                selected_agents = base_route
            rationale = "Heuristic routing with LLM refinement (fallback parsing)"
            confidence = 0.7
        
        # Validate selected_agents are valid roles
        valid_roles = ["researcher", "summarizer", "writer", "coder", "analyst"]
        selected_agents = [a for a in selected_agents if a in valid_roles]
        
        # Ensure at least one agent
        if not selected_agents:
            selected_agents = base_route
        
        # Ensure researcher comes first if source_url exists
        if task.source_url and "researcher" in selected_agents:
            selected_agents = ["researcher"] + [a for a in selected_agents if a != "researcher"]
        
    except Exception as e:
        # Fallback to heuristic route
        selected_agents = base_route
        rationale = f"Heuristic routing (LLM error: {str(e)})"
        confidence = 0.6
    
    return RouteDecision(
        selected_agents=selected_agents,
        rationale=rationale,
        confidence=confidence
    )

def run_researcher(task: TaskSpec, context: Dict[str, Any]) -> AgentResult:
    """Researcher agent: extracts facts from source material."""
    source_text = context.get("source_text", "")
    
    if not source_text:
        return AgentResult(
            role="researcher",
            content="No source text available to research.",
            warnings=["No source text was provided or could be fetched."]
        )
    
    prompt = build_researcher_prompt(task, source_text)
    
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Extract citations (URLs mentioned)
        citations = []
        if task.source_url:
            citations.append(task.source_url)
        
        return AgentResult(
            role="researcher",
            content=content,
            citations=citations
        )
    except Exception as e:
        return AgentResult(
            role="researcher",
            content=f"Error in research: {str(e)}",
            warnings=[f"Research failed: {str(e)}"]
        )

def run_summarizer(task: TaskSpec, context: Dict[str, Any]) -> AgentResult:
    """Summarizer agent: creates summaries from facts."""
    prompt = build_summarizer_prompt(task, context)
    
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        return AgentResult(
            role="summarizer",
            content=content
        )
    except Exception as e:
        return AgentResult(
            role="summarizer",
            content=f"Error in summarization: {str(e)}",
            warnings=[f"Summarization failed: {str(e)}"]
        )

def run_writer(task: TaskSpec, context: Dict[str, Any]) -> AgentResult:
    """Writer agent: creates polished prose."""
    prompt = build_writer_prompt(task, context)
    
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        return AgentResult(
            role="writer",
            content=content
        )
    except Exception as e:
        return AgentResult(
            role="writer",
            content=f"Error in writing: {str(e)}",
            warnings=[f"Writing failed: {str(e)}"]
        )

def run_coder(task: TaskSpec, context: Dict[str, Any]) -> AgentResult:
    """Coder agent: generates code solutions."""
    prompt = build_coder_prompt(task, context)
    
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        return AgentResult(
            role="coder",
            content=content
        )
    except Exception as e:
        return AgentResult(
            role="coder",
            content=f"Error in code generation: {str(e)}",
            warnings=[f"Code generation failed: {str(e)}"]
        )

def run_analyst(task: TaskSpec, context: Dict[str, Any]) -> AgentResult:
    """Analyst agent: extracts insights from data."""
    prompt = build_analyst_prompt(task, context)
    
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        return AgentResult(
            role="analyst",
            content=content
        )
    except Exception as e:
        return AgentResult(
            role="analyst",
            content=f"Error in analysis: {str(e)}",
            warnings=[f"Analysis failed: {str(e)}"]
        )

def run_agent(role: Role, task: TaskSpec, context: Dict[str, Any]) -> AgentResult:
    """Dispatch to the appropriate agent based on role."""
    agent_map = {
        "researcher": run_researcher,
        "summarizer": run_summarizer,
        "writer": run_writer,
        "coder": run_coder,
        "analyst": run_analyst,
    }
    
    agent_func = agent_map.get(role)
    if not agent_func:
        return AgentResult(
            role=role,
            content=f"Unknown agent role: {role}",
            warnings=[f"Agent {role} not implemented"]
        )
    
    return agent_func(task, context)

def merger_and_qa(task: TaskSpec, agent_results: List[AgentResult], context: Dict[str, Any]) -> str:
    """
    Merger/QA agent: combines multi-agent outputs and ensures quality.
    
    Returns the final merged output string.
    """
    if not agent_results:
        return "No agent results to merge."
    
    # If only one agent, return its output (with length check)
    if len(agent_results) == 1:
        output = agent_results[0].content
        if len(output) > Config.MAX_OUTPUT_LENGTH:
            output = output[:Config.MAX_OUTPUT_LENGTH] + "... [truncated]"
        return output
    
    # Build merger prompt
    prompt = build_merger_prompt(task, agent_results)
    
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        merged = response.content.strip()
        
        # Enforce length limit
        if len(merged) > Config.MAX_OUTPUT_LENGTH:
            merged = merged[:Config.MAX_OUTPUT_LENGTH] + "... [truncated]"
        
        return merged
    except Exception as e:
        # Fallback: concatenate results
        fallback = "\n\n".join([f"## {r.role}\n{r.content}" for r in agent_results])
        if len(fallback) > Config.MAX_OUTPUT_LENGTH:
            fallback = fallback[:Config.MAX_OUTPUT_LENGTH] + "... [truncated]"
        return fallback

def formatter(route: RouteDecision, agent_results: List[AgentResult], final_output: str) -> Dict[str, Any]:
    """
    Formatter: constructs the FinalPackage structure.
    
    Returns a dict that can be validated as FinalPackage.
    """
    return {
        "route": route.model_dump(),
        "steps": [r.model_dump() for r in agent_results],
        "final_output": final_output,
        "tokens_used": None  # Could be tracked if needed
    }

