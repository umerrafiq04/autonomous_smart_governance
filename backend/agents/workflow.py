from typing import TypedDict

from langgraph.graph import StateGraph, END

from backend.agents.analysis_agent import analyze_complaint
from backend.agents.knowledge_agent import generate_guidance
from backend.agents.governance_agent import governance_decision
from backend.agents.resolution_agent import resolution_decision


# ==========================================
# Workflow State
# ==========================================
class ComplaintState(TypedDict):

    title: str
    description: str

    issue_type: str
    severity: str
    department: str
    eta: str
    summary: str
    follow_up_question: str

    citizen_guidance: str

    priority: str
    tracking_status: str
    official_response: str
    escalation_required: str

    resolved_by_ai: bool
    needs_human: bool
    resolution_reason: str
    final_response: str


# ==========================================
# Analysis Agent Node
# ==========================================
def analysis_node(state: ComplaintState):

    result = analyze_complaint(
        title=state["title"],
        description=state["description"]
    )

    return {
        **state,
        "issue_type": result["issue_type"],
        "severity": result["severity"],
        "department": result["department"],
        "eta": result["eta"],
        "summary": result["summary"],
        "follow_up_question": result["follow_up_question"]
    }


# ==========================================
# Knowledge Agent Node
# ==========================================
def knowledge_node(state: ComplaintState):

    guidance = generate_guidance(
        department=state["department"],
        issue_type=state["issue_type"],
        description=state["description"]
    )

    return {
        **state,
        "citizen_guidance": guidance
    }


# ==========================================
# Governance Agent Node
# ==========================================
def governance_node(state: ComplaintState):

    result = governance_decision(
        issue_type=state["issue_type"],
        severity=state["severity"],
        department=state["department"],
        description=state["description"]
    )

    return {
        **state,
        "priority": result["priority"],
        "tracking_status": result["tracking_status"],
        "official_response": result["official_response"],
        "escalation_required": result["escalation_required"]
    }


# ==========================================
# Resolution Agent Node
# ==========================================
def resolution_node(state: ComplaintState):

    result = resolution_decision(
        issue_type=state["issue_type"],
        severity=state["severity"],
        department=state["department"],
        description=state["description"],
        citizen_guidance=state["citizen_guidance"]
    )

    return {
        **state,
        "resolved_by_ai": result["resolved_by_ai"],
        "needs_human": result["needs_human"],
        "resolution_reason": result["resolution_reason"],
        "final_response": result["final_response"]
    }


# ==========================================
# Build Workflow Graph
# ==========================================
graph = StateGraph(ComplaintState)

graph.add_node(
    "analysis_agent",
    analysis_node
)

graph.add_node(
    "knowledge_agent",
    knowledge_node
)

graph.add_node(
    "governance_agent",
    governance_node
)

graph.add_node(
    "resolution_agent",
    resolution_node
)

# Entry point
graph.set_entry_point("analysis_agent")

# Workflow edges
graph.add_edge(
    "analysis_agent",
    "knowledge_agent"
)

graph.add_edge(
    "knowledge_agent",
    "governance_agent"
)

graph.add_edge(
    "governance_agent",
    "resolution_agent"
)

graph.add_edge(
    "resolution_agent",
    END
)

# Compile workflow
workflow = graph.compile()


# ==========================================
# Run Full Workflow
# ==========================================
def run_complaint_workflow(
    title: str,
    description: str
):

    initial_state = {
        "title": title,
        "description": description
    }

    result = workflow.invoke(initial_state)

    return result