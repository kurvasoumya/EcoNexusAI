from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, START, END

from agents.manager_agent1 import manager_agent


class WasteState(TypedDict, total=False):
    waste_type: str
    quantity_kg: float
    contamination: float
    source: str
    distance: float
    delivered_quantity: float
    actual_destination: str

    result: Dict[str, Any]
    status: str


def manager_node(state: WasteState) -> WasteState:

    result = manager_agent.process_waste(
        waste_type=state["waste_type"],
        quantity_kg=state["quantity_kg"],
        contamination=state["contamination"],
        source=state["source"],
        distance=state["distance"],
        delivered_quantity=state["delivered_quantity"],
        actual_destination=state["actual_destination"]
    )

    return {
        "result": result,
        "status": result.get("status", "unknown")
    }


# ==========================================
# CREATE LANGGRAPH WORKFLOW
# ==========================================

graph = StateGraph(WasteState)

# Add Manager Agent
graph.add_node("manager_agent", manager_node)

# Workflow connections
graph.add_edge(START, "manager_agent")
graph.add_edge("manager_agent", END)

# Compile the graph
waste_workflow = graph.compile()