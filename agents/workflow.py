from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, START, END

from agents.waste_intelligence_agent import WasteIntelligenceAgent
from agents.resource_recovery_agent import resource_recovery_agent
from agents.facility_agent import facility_agent
from agents.environment_agent import environment_agent
from agents.logistics_agent import logistics_agent
from agents.verification_agent import verification_agent
from agents.rag_agent import rag_agent


# ============================================================
# SHARED STATE
# ============================================================

class WasteState(TypedDict, total=False):

    # Input
    waste_type: str
    quantity_kg: float
    contamination: float
    source: str
    distance: float
    delivered_quantity: float
    actual_destination: str

    # Agent results
    waste_intelligence: Dict[str, Any]
    rag_knowledge: list
    resource_recovery: Dict[str, Any]
    facility: Dict[str, Any]
    manager_decision: Dict[str, Any]
    environment: Dict[str, Any]
    logistics: Dict[str, Any]
    verification: Dict[str, Any]

    # Replanning
    
    replan_required: bool
    alternative_facility: str
    alternative_recovery: str
    replan_logistics: Dict[str, Any]
    replan_environment: Dict[str, Any]
    replan_verification: Dict[str, Any]

    # Final result
    status: str
    message: str
    final_decision: Dict[str, Any]


# ============================================================
# AGENT INSTANCES
# ============================================================

waste_intelligence_agent = WasteIntelligenceAgent()


# ============================================================
# 1. WASTE INTELLIGENCE AGENT
# ============================================================

def waste_intelligence_node(state: WasteState):

    result = waste_intelligence_agent.analyze(
        waste_type=state["waste_type"],
        quantity_kg=state["quantity_kg"],
        contamination=state["contamination"],
        source=state["source"]
    )

    return {
        "waste_intelligence": result
    }


# ============================================================
# 2. RAG KNOWLEDGE AGENT
# ============================================================

def rag_knowledge_node(state: WasteState):

    query = f"""
    Waste type: {state["waste_type"]}
    Quantity: {state["quantity_kg"]} kg
    Contamination: {state["contamination"]} percent

    What are the recommended recycling, recovery,
    treatment, composting, anaerobic digestion,
    waste-to-energy and safe handling options
    for this waste?
    """

    knowledge = rag_agent.search(
        query,
        k=3
    )

    return {
        "rag_knowledge": knowledge
    }


# ============================================================
# 3. RESOURCE RECOVERY AGENT
# ============================================================

def resource_recovery_node(state: WasteState):

    waste_type = state["waste_type"].lower()

    # Normalize waste names
    if waste_type in [
        "food",
        "organic",
        "vegetable",
        "fruit"
    ]:
        waste_type = "food"

    elif waste_type in [
        "plastic",
        "bottle",
        "polythene"
    ]:
        waste_type = "plastic"

    elif waste_type in [
        "paper",
        "cardboard"
    ]:
        waste_type = "paper"

    elif waste_type in [
        "metal",
        "glass"
    ]:
        waste_type = "metal_glass"

    elif waste_type in [
        "electronic",
        "electronics"
    ]:
        waste_type = "e-waste"

    elif waste_type in [
        "chemical",
        "toxic"
    ]:
        waste_type = "hazardous"

    elif waste_type in [
        "clothing",
        "fabric"
    ]:
        waste_type = "textile"

    elif waste_type in [
        "concrete",
        "bricks"
    ]:
        waste_type = "construction"

    result = resource_recovery_agent.analyze_recovery(
        waste_type,
        state["quantity_kg"],
        state["contamination"]
    )

    return {
        "resource_recovery": result
    }


# ============================================================
# 4. FACILITY AGENT
# ============================================================

def facility_node(state: WasteState):

    waste_type = state["waste_type"].lower()

    # Normalize waste type
    if waste_type in [
        "food",
        "organic",
        "vegetable",
        "fruit"
    ]:
        facility_type = "organic"

    elif waste_type in [
        "plastic",
        "bottle",
        "polythene"
    ]:
        facility_type = "plastic"

    elif waste_type in [
        "paper",
        "cardboard"
    ]:
        facility_type = "paper"

    elif waste_type in [
        "metal",
        "glass"
    ]:
        facility_type = "metal_glass"

    elif waste_type in [
        "e-waste",
        "electronic",
        "electronics"
    ]:
        facility_type = "e-waste"

    elif waste_type in [
        "hazardous",
        "chemical",
        "toxic"
    ]:
        facility_type = "hazardous"

    elif waste_type in [
        "textile",
        "clothing",
        "fabric"
    ]:
        facility_type = "textile"

    elif waste_type in [
        "construction",
        "concrete",
        "bricks"
    ]:
        facility_type = "construction"

    elif waste_type == "residual":
        facility_type = "residual"

    else:
        facility_type = "residual"

    # Get recovery recommendations
    recovery_options = state.get(
        "resource_recovery",
        {}
    ).get(
        "recovery_options",
        []
    )

    # Find compatible facilities
    result = facility_agent.find_facilities(
        facility_type,
        state["quantity_kg"],
        recovery_options
    )

    if result["status"] == "facilities_found":

        return {
            "facility": {
                "status": "facility_found",
                "facility": result["facilities"][0]["name"],
                "available_capacity": result["facilities"][0]["capacity"],
                "waste_type": facility_type,
                "quantity": state["quantity_kg"],
                "available_facilities": result["facilities"]
            }
        }

    return {
        "facility": result
    }


# ============================================================
# 5. MANAGER AGENT
# ============================================================

def manager_decision_node(state: WasteState):

    facility_result = state.get(
        "facility",
        {}
    )

    facilities = facility_result.get(
        "available_facilities",
        []
    )

    recovery_result = state.get(
        "resource_recovery",
        {}
    )

    recovery_options = recovery_result.get(
        "recovery_options",
        []
    )

    recommended_option = recovery_result.get(
        "recommended_option"
    ) or "Safe Disposal"
    

    rag_knowledge = state.get(
        "rag_knowledge",
        []
    )

    # --------------------------------------------------------
    # No suitable facility
    # --------------------------------------------------------

    if not facilities:

        return {
            "manager_decision": {
                "status": "failed",
                "selected_facility": None,
                "available_options": [],
                "recommended_recovery": recommended_option,
                "message": (
                    "Manager could not find a suitable "
                    "compatible facility."
                )
            }
        }

    # --------------------------------------------------------
    # Score facilities
    # --------------------------------------------------------

    facility_scores = []

    best_facility = None
    best_score = float("-inf")

    for facility in facilities:

        capacity = facility.get(
            "capacity",
            0
        )

        accepted_processes = facility.get(
            "accepted_processes",
            []
        )

               # Check compatibility with the recommended recovery pathway
        compatible = False

        for process in accepted_processes:

            if (
                recommended_option.lower() in process.lower()
                or process.lower() in recommended_option.lower()
            ):
                compatible = True

        # Capacity score
        capacity_score = (
            capacity /
            max(state["quantity_kg"], 1)
        )

        # Environment score
        environment_result = environment_agent.evaluate(
            waste_type=facility_result.get(
                "waste_type",
                "residual"
            ),
            quantity=state["quantity_kg"],
            distance=state["distance"]
        )

        environment_score = environment_result.get(
            "environment_score",
            0
        )

        
        # Recovery compatibility score
        recovery_score = 50 if compatible else -1000

        # Total score
        score = (
            capacity_score * 10
            + environment_score
            + recovery_score
        )

        facility_scores.append({
            "facility": facility["name"],
            "capacity_kg": capacity,
            "capacity_score": round(
                capacity_score,
                2
            ),
            "accepted_processes": accepted_processes,
            "recovery_compatible": compatible,
            "environment_score": environment_score,
            "recovery_compatibility_score": recovery_score,
            "total_score": round(
                score,
                2
            )
        })

        if score > best_score:

            best_score = score
            best_facility = facility

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if best_facility is None:

        return {
            "manager_decision": {
                "status": "failed",
                "selected_facility": None,
                "available_options": [],
                "message": (
                    "No compatible facility could "
                    "be selected."
                )
            }
        }

    # --------------------------------------------------------
    # Decision explanation
    # --------------------------------------------------------

    reason = (
        f"Manager selected {best_facility['name']} "
        f"because it has sufficient capacity and "
        f"is compatible with the recovery pathway "
        f"'{recommended_option}'."
    )

    return {
        "manager_decision": {

            "status": "selected",

            "selected_facility": (
                best_facility["name"]
            ),

            "recommended_recovery": (
                recommended_option
            ),

            "recovery_options": (
                recovery_options
            ),

            "available_options": [
                facility["name"]
                for facility in facilities
            ],

            "facility_scores": (
                facility_scores
            ),

            "decision_score": round(
                best_score,
                2
            ),

            "rag_sources": [
                item.get("source")
                for item in rag_knowledge
            ],

            "reason": reason
        }
    }


# ============================================================
# 6. ENVIRONMENT AGENT
# ============================================================

def environment_node(state: WasteState):

    category = state["waste_intelligence"]["category"]

    mapping = {
        "Organic": "organic",
        "Plastic": "plastic",
        "Paper": "paper",
        "Metal/Glass": "metal_glass",
        "E-Waste": "e-waste",
        "Hazardous": "hazardous",
        "Textile": "textile",
        "Construction": "construction",
        "Residual": "residual"
    }

    environment_type = mapping.get(
        category,
        "residual"
    )

    result = environment_agent.evaluate(
        waste_type=environment_type,
        quantity=state["quantity_kg"],
        distance=state["distance"]
    )

    return {
        "environment": result
    }


# ============================================================
# 7. LOGISTICS AGENT
# ============================================================

def logistics_node(state: WasteState):

    facility_result = state.get(
        "facility",
        {}
    )

    if facility_result.get("status") == "no_facility":

        return {
            "logistics": {
                "status": "failed",
                "message": "No suitable facility available."
            }
        }

    # Get Manager decision
    manager_result = state.get(
        "manager_decision",
        {}
    )

    selected_facility = manager_result.get(
        "selected_facility"
    )

    if not selected_facility:

        selected_facility = facility_result.get(
            "facility"
        )

    category = state["waste_intelligence"]["category"]

    mapping = {
        "Organic": "organic",
        "Plastic": "plastic",
        "Paper": "paper",
        "Metal/Glass": "metal_glass",
        "E-Waste": "e-waste",
        "Hazardous": "hazardous",
        "Textile": "textile",
        "Construction": "construction",
        "Residual": "residual"
    }

    logistics_type = mapping.get(
        category,
        "residual"
    )

    result = logistics_agent.plan_transport(
        waste_type=logistics_type,
        quantity=state["quantity_kg"],
        source=state["source"],
        facility=selected_facility,
        distance=state["distance"]
    )

    return {
        "logistics": result
    }


# ============================================================
# 8. VERIFICATION AGENT
# ============================================================

def verification_node(state: WasteState):
    planned_destination = state["manager_decision"]["selected_facility"]

    verification = verification_agent.verify_delivery(
        waste_type=state["waste_type"],
        planned_quantity=state["quantity_kg"],
        delivered_quantity=state["delivered_quantity"],
        planned_destination=planned_destination,
        actual_destination=state["actual_destination"]
    )

    return {
        "verification": verification,
        "replan_required": verification["replan_required"]
    }
# ============================================================
# 9. ROUTING DECISION
# ============================================================

def verification_router(state: WasteState):

    verification = state.get(
        "verification",
        {}
    )

    if verification.get(
        "replan_required"
    ):

        return "replan"

    return "complete"


# ============================================================
# 10. DYNAMIC REPLANNING
# ============================================================

def replan_node(state: WasteState):

    manager_result = state.get(
        "manager_decision",
        {}
    )

    selected_facility = manager_result.get(
        "selected_facility"
    )

    facility_result = state.get(
        "facility",
        {}
    )

    if not selected_facility:
        selected_facility = facility_result.get(
            "facility"
        )

    recovery_result = state.get(
        "resource_recovery",
        {}
    )

    recovery_options = recovery_result.get(
        "recovery_options",
        []
    )

    facility_type = facility_result.get(
        "waste_type",
        "residual"
    )

    # ========================================================
    # SEARCH ALL FACILITIES FOR AN ALTERNATIVE PATHWAY
    # ========================================================

    alternative_facility = None
    alternative_recovery = None

    all_facilities = facility_agent.get_facilities().get(
        "facilities",
        []
    )

    for facility in all_facilities:

        # Do not select the same facility
        if facility["name"] == selected_facility:
            continue

        # Skip facilities that cannot currently accept waste
        if facility["status"] != "available":
            continue

        # Skip facilities without enough capacity
        if facility["capacity"] < state["quantity_kg"]:
            continue

        # Check supported processes
        for process in facility.get(
            "accepted_processes",
            []
        ):

            if process in recovery_options:
                alternative_facility = facility
                alternative_recovery = process
                break

        if alternative_facility is not None:
            break

    # ========================================================
    # NO ALTERNATIVE FOUND
    # ========================================================

    if alternative_facility is None:

        return {
            "status": "replanning_failed",
            "message": (
                "Verification failed and no "
                "compatible alternative facility "
                "is available."
            ),
            "alternative_facility": "",
            "alternative_recovery": "",
            "replan_logistics": {},
            "replan_environment": {}
        }

    # ========================================================
    # CREATE NEW LOGISTICS PLAN
    # ========================================================

    new_logistics = logistics_agent.plan_transport(
        waste_type=facility_type,
        quantity=state["quantity_kg"],
        source=state["source"],
        facility=alternative_facility["name"],
        distance=state["distance"]
    )

    # ========================================================
    # EVALUATE NEW ENVIRONMENTAL IMPACT
    # ========================================================

    new_environment = environment_agent.evaluate(
        waste_type=facility_type,
        quantity=state["quantity_kg"],
        distance=state["distance"]
    )

    return {
        "alternative_facility": alternative_facility["name"],
        "alternative_recovery": alternative_recovery,
        "replan_logistics": new_logistics,
        "replan_environment": new_environment,
        "replan_required": True
    }
    
# ============================================================
# 11. REPLANNED VERIFICATION
# ============================================================

def replan_verification_node(state: WasteState):

    alternative_facility = state.get(
        "alternative_facility"
    )

    if not alternative_facility:

        return {
            "replan_verification": {
                "status": "failed",
                "replan_required": True,
                "message": (
                    "No alternative facility available."
                )
            }
        }

    # Prototype simulation:
    # redirected delivery reaches alternative facility

    result = verification_agent.verify_delivery(
        waste_type=state["waste_type"],
        planned_quantity=state["quantity_kg"],
        delivered_quantity=state["quantity_kg"],
        planned_destination=alternative_facility,
        actual_destination=alternative_facility
    )

    return {
        "replan_verification": result
    }


# ============================================================
# 12. FINAL DECISION
# ============================================================

def final_decision_node(state: WasteState):

    verification = state.get(
        "verification",
        {}
    )

    # ========================================================
    # NORMAL SUCCESSFUL ROUTE
    # ========================================================

    if not verification.get(
        "replan_required"
    ):

        recovery = state.get(
            "resource_recovery",
            {}
        )

        logistics = state.get(
            "logistics",
            {}
        )

        environment = state.get(
            "environment",
            {}
        )

        manager_result = state.get(
            "manager_decision",
            {}
        )

        selected_facility = manager_result.get(
            "selected_facility"
        )

        return {
            "status": "completed",

            "message": (
                "Waste successfully processed "
                "through EcoNexus AI."
            ),

                "final_decision": {

                "action": recovery.get(
                "recommended_option"
                ),

                "facility": selected_facility,

                "transport": logistics.get(
                    "truck_id"
                ),

                "environmental_impact": environment.get(
                    "impact_level"
                ),

                "verification": verification.get(
                    "status"
                )
            }
        }

    # ========================================================
    # REPLANNED ROUTE
    # ========================================================

    replan_verification = state.get(
        "replan_verification",
        {}
    )

    if replan_verification.get(
        "status"
    ) == "verified":

        recovery = state.get(
            "resource_recovery",
            {}
        )

        return {
            "status": "replanned_and_completed",

            "message": (
                "Original delivery failed. "
                "EcoNexus AI automatically "
                "replanned the waste pathway "
                "and verified the alternative route."
            ),
        

            "original_plan": {

                "facility": state.get(
                    "manager_decision",
                    {}
                ).get(
                    "selected_facility"
                ),

                "verification": verification.get(
                    "status"
                ),

                "verification_message": verification.get(
                    "message"
                )
            },

                        "replanned_solution": {

                "facility": state.get(
                    "alternative_facility"
                ),

                "recovery": state.get(
                    "alternative_recovery"
                ),

                "transport": state.get(
                    "replan_logistics",
                    {}
                ).get(
                    "truck_id"
                ),

                "environmental_impact": state.get(
                    "replan_environment",
                    {}
                ).get(
                    "impact_level"
                ),

                "verification": replan_verification.get(
                    "status"
                )
            },

            "final_decision": {

                "action": state.get(
                    "alternative_recovery"
                ),

                "facility": state.get(
                    "alternative_facility"
                ),

                "transport": state.get(
                    "replan_logistics",
                    {}
                ).get(
                    "truck_id"
                ),

                "verification": replan_verification.get(
                    "status"
                )
            }
        }

    # ========================================================
    # REPLANNING FAILED
    # ========================================================

    return {
        "status": "replanning_failed",

        "message": (
            "Verification failed and the "
            "alternative recovery plan could "
            "not be completed."
        )
    }


# ============================================================
# CREATE LANGGRAPH
# ============================================================

graph = StateGraph(
    WasteState
)


# ============================================================
# ADD NODES
# ============================================================

graph.add_node(
    "waste_intelligence",
    waste_intelligence_node
)

graph.add_node(
    "rag_knowledge",
    rag_knowledge_node
)

graph.add_node(
    "resource_recovery",
    resource_recovery_node
)

graph.add_node(
    "facility",
    facility_node
)

graph.add_node(
    "manager_decision",
    manager_decision_node
)

graph.add_node(
    "environment",
    environment_node
)

graph.add_node(
    "logistics",
    logistics_node
)

graph.add_node(
    "verification",
    verification_node
)

graph.add_node(
    "replan",
    replan_node
)

graph.add_node(
    "replan_verification",
    replan_verification_node
)

graph.add_node(
    "final_decision",
    final_decision_node
)


# ============================================================
# NORMAL WORKFLOW
# ============================================================

graph.add_edge(
    START,
    "waste_intelligence"
)

graph.add_edge(
    "waste_intelligence",
    "rag_knowledge"
)

graph.add_edge(
    "rag_knowledge",
    "resource_recovery"
)

graph.add_edge(
    "resource_recovery",
    "facility"
)

graph.add_edge(
    "facility",
    "manager_decision"
)

graph.add_edge(
    "manager_decision",
    "environment"
)

graph.add_edge(
    "environment",
    "logistics"
)

graph.add_edge(
    "logistics",
    "verification"
)


# ============================================================
# CONDITIONAL ROUTING
# ============================================================

graph.add_conditional_edges(
    "verification",
    verification_router,
    {
        "complete": "final_decision",
        "replan": "replan"
    }
)


# ============================================================
# REPLANNING WORKFLOW
# ============================================================

graph.add_edge(
    "replan",
    "replan_verification"
)

graph.add_edge(
    "replan_verification",
    "final_decision"
)

graph.add_edge(
    "final_decision",
    END
)


# ============================================================
# COMPILE WORKFLOW
# ============================================================

waste_workflow = graph.compile()