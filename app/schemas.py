"""Pydantic data models for the AI Task Router."""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

Role = Literal["researcher", "summarizer", "writer", "coder", "analyst"]

class TaskSpec(BaseModel):
    """User task specification."""
    user_query: str = Field(..., description="The user's task request")
    source_url: Optional[str] = Field(None, description="Optional URL/PDF to pull context from")
    desired_style: Optional[Literal["concise", "technical", "friendly", "executive"]] = Field(
        "concise", description="Desired output style"
    )
    desired_length: Optional[str] = Field(
        "short", description="Desired output length: short, medium, or long"
    )

class RouteDecision(BaseModel):
    """Routing decision made by the router agent."""
    selected_agents: List[Role] = Field(..., description="List of agents to execute in order")
    rationale: str = Field(..., description="Explanation for the routing decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the routing")

class AgentResult(BaseModel):
    """Result from a single agent execution."""
    role: Role = Field(..., description="The agent role that produced this result")
    content: str = Field(..., description="The agent's output content")
    citations: List[str] = Field(default_factory=list, description="List of citation URLs or references")
    warnings: List[str] = Field(default_factory=list, description="List of warnings or assumptions")

class FinalPackage(BaseModel):
    """Final output package with routing trace and results."""
    route: RouteDecision = Field(..., description="The routing decision made")
    steps: List[AgentResult] = Field(..., description="Results from each agent step")
    final_output: str = Field(..., description="The final merged and formatted output")
    tokens_used: Optional[int] = Field(None, description="Total tokens used in the process")

