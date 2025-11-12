"""Prompt templates for all agents."""
from app.schemas import TaskSpec

# Global system prompt
SYSTEM_PROMPT = """You are a team of specialized assistants coordinated by a router. 
Always return clean, factual, concise outputs. Never invent sources. 
If you are unsure, state assumptions. Follow the JSON schemas strictly."""

def build_router_prompt(task: TaskSpec, heuristic_route: list[str]) -> str:
    """Build prompt for the router agent."""
    return f"""Given a TaskSpec, decide which of: researcher, summarizer, writer, coder, analyst should run and in what order.

Task Specification:
- User Query: {task.user_query}
- Source URL: {task.source_url or "None"}
- Desired Style: {task.desired_style}
- Desired Length: {task.desired_length}

Heuristic Route (initial suggestion): {', '.join(heuristic_route)}

Routing Rules:
1. If a URL/PDF is present → include researcher first.
2. If the user asks for 'summary', 'summarize', 'tl;dr', 'brief' → include summarizer.
3. If asking to 'draft', 'rewrite', 'post', 'email', 'linkedin' → include writer.
4. If code, regex, shell, or CSV asks → include coder or analyst.
5. If table, csv, metrics, kpi, trend → include analyst.

Refine the heuristic route and return a JSON object with:
- selected_agents: list of agent roles in execution order
- rationale: brief explanation (1-2 sentences)
- confidence: float between 0 and 1

Return ONLY valid JSON, no markdown formatting."""

def build_researcher_prompt(task: TaskSpec, source_text: str) -> str:
    """Build prompt for the researcher agent."""
    return f"""Extract trustworthy facts from the provided text below.

User Query: {task.user_query}
Source URL: {task.source_url or "None"}

Source Text:
{source_text[:10000]}  # Limit to 10k chars for prompt

Instructions:
- Extract key facts and information relevant to the user's query
- Output a brief, bullet-based fact sheet
- Include inline citations [1], [2] for sources (use the source URL as [1])
- No opinions, only factual information
- If information is missing or uncertain, state that clearly
- Keep output concise and focused

Return the fact sheet as plain text with bullet points."""

def build_summarizer_prompt(task: TaskSpec, context: dict) -> str:
    """Build prompt for the summarizer agent."""
    researcher_output = context.get("researcher_output", "")
    source_text = context.get("source_text", "")
    
    return f"""Summarize the provided facts into the requested style and length.

User Query: {task.user_query}
Desired Style: {task.desired_style}
Desired Length: {task.desired_length}

Researcher Output (facts):
{researcher_output[:5000] if researcher_output else "No researcher output available."}

Source Text (if available):
{source_text[:3000] if source_text else "No source text available."}

Instructions:
- Summarize the facts from the researcher output
- Match the requested style: {task.desired_style}
- Match the requested length: {task.desired_length} (short: 100-200 words, medium: 300-500 words, long: 600+ words)
- No new facts; cite by [n] indexes from the researcher result if available
- Maintain factual accuracy
- Keep it focused and relevant to the user's query

Return the summary as plain text."""

def build_writer_prompt(task: TaskSpec, context: dict) -> str:
    """Build prompt for the writer agent."""
    summary = context.get("summarizer_output", "")
    researcher_output = context.get("researcher_output", "")
    
    return f"""Using the summary and style guidelines, produce a polished prose artifact.

User Query: {task.user_query}
Desired Style: {task.desired_style}
Desired Length: {task.desired_length}

Summary to work with:
{summary[:3000] if summary else "No summary available."}

Researcher Facts (for reference):
{researcher_output[:2000] if researcher_output else "No researcher facts available."}

Instructions:
- Create polished prose (e.g., LinkedIn post, email, marketing blurb, article)
- Match the style: {task.desired_style}
  * concise: direct, no fluff
  * technical: precise terminology, structured
  * friendly: conversational, warm tone
  * executive: professional, strategic perspective
- Match the length: {task.desired_length}
- Keep it scoped and crisp
- Avoid claims you can't support
- Maintain citations [n] if present in source material
- Make it engaging and appropriate for the requested format

Return the written content as plain text."""

def build_coder_prompt(task: TaskSpec, context: dict) -> str:
    """Build prompt for the coder agent."""
    return f"""Given a coding request, produce minimal runnable code and a brief guide.

User Query: {task.user_query}

Instructions:
- Produce minimal, runnable code that solves the request
- Include brief comments only where necessary
- Provide a 3-step run guide:
  1. Setup (dependencies, environment)
  2. Execution (how to run)
  3. Expected output
- Keep code focused and avoid over-engineering
- If the request is unclear, ask clarifying questions or provide a reasonable interpretation

Return the code block followed by the 3-step guide."""

def build_analyst_prompt(task: TaskSpec, context: dict) -> str:
    """Build prompt for the analyst agent."""
    source_text = context.get("source_text", "")
    researcher_output = context.get("researcher_output", "")
    
    return f"""Given tabular/metric context, extract insights and list follow-ups.

User Query: {task.user_query}

Source Data:
{source_text[:5000] if source_text else "No source data available."}

Researcher Facts:
{researcher_output[:3000] if researcher_output else "No researcher facts available."}

Instructions:
- Extract 3-5 key insights from the data
- Identify trends, patterns, or notable findings
- List simple follow-up questions or actions
- Avoid creating charts (text-only for MVP)
- Be specific and data-driven
- If data is insufficient, state that clearly

Return insights as a structured list with follow-ups."""

def build_merger_prompt(task: TaskSpec, agent_results: list) -> str:
    """Build prompt for the merger/QA agent."""
    results_text = "\n\n".join([
        f"=== {r.role.upper()} ===\n{r.content[:2000]}"
        for r in agent_results
    ])
    
    return f"""Merge multi-agent outputs into a single coherent story.

User Query: {task.user_query}
Desired Style: {task.desired_style}
Desired Length: {task.desired_length}

Agent Outputs:
{results_text}

Instructions:
- Merge outputs into a single coherent narrative
- Resolve contradictions by preferring: Researcher → Summarizer → Writer chain
- Enforce style: {task.desired_style}
- Enforce length: {task.desired_length}
- Maintain citations if present
- Add a brief disclaimer if sources are weak or assumptions were made
- Ensure the output directly addresses the user's query
- Keep it polished and ready for final use

Return the merged output as plain text."""

