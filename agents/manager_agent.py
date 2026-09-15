from agents.waste_intelligence_agent import WasteIntelligenceAgent
from agents.resource_recovery_agent import resource_recovery_agent
from agents.facility_agent import facility_agent
from agents.environment_agent import environment_agent
from agents.logistics_agent import logistics_agent
from agents.verification_agent import verification_agent


class ManagerAgent:

    def __init__(self):
        self.name = "Manager Agent"

        # Initialize Waste Intelligence Agent
        self.waste_intelligence = WasteIntelligenceAgent()

    def process_waste(
        self,
        waste_type,
        quantity_kg,
        contamination,
        source,
        distance,
        delivered_quantity=None,
        actual_destination=None
    ):

        # =====================================================
        # 1. WASTE INTELLIGENCE AGENT
        # =====================================================

        waste_analysis = self.waste_intelligence.analyze(
            waste_type=waste_type,
            quantity_kg=quantity_kg,
            contamination=contamination,
            source=source
        )

        category = waste_analysis["category"]

        # =====================================================
        # 2. RESOURCE RECOVERY AGENT
        # =====================================================

        recovery_type = waste_type.lower()

        # Normalize waste types for the recovery agent
        if recovery_type in ["organic", "vegetable", "fruit"]:
            recovery_type = "food"

        elif recovery_type in ["bottle", "polythene"]:
            recovery_type = "plastic"

        elif recovery_type == "cardboard":
            recovery_type = "paper"

        elif recovery_type == "metal_glass":
            recovery_type = "metal"

        recovery_analysis = resource_recovery_agent.analyze_recovery(
            recovery_type,
            quantity_kg,
            contamination
        )

        # =====================================================
        # 3. FACILITY AGENT
        # =====================================================

        facility_type = recovery_type

        if facility_type == "metal":
            facility_type = "metal_glass"

        facility_result = facility_agent(
            facility_type,
            quantity_kg
        )

        # Stop if no facility is available
        if facility_result["status"] == "no_facility":

            return {
                "manager": self.name,
                "status": "failed",
                "message": "No suitable facility available.",
                "waste_intelligence": waste_analysis,
                "resource_recovery": recovery_analysis,
                "facility": facility_result
            }

        selected_facility = facility_result["facility"]

        # =====================================================
        # 4. ENVIRONMENT AGENT
        # =====================================================

        environment_result = environment_agent.evaluate(
            waste_type=facility_type,
            quantity=quantity_kg,
            distance=distance
        )

        # =====================================================
        # 5. LOGISTICS AGENT
        # =====================================================

        logistics_result = logistics_agent.plan_transport(
            waste_type=facility_type,
            quantity=quantity_kg,
            source=source,
            facility=selected_facility,
            distance=distance
        )

        # Stop if transport cannot be planned
        if logistics_result["status"] == "failed":

            return {
                "manager": self.name,
                "status": "failed",
                "message": "Transportation could not be planned.",
                "waste_intelligence": waste_analysis,
                "resource_recovery": recovery_analysis,
                "facility": facility_result,
                "environment": environment_result,
                "logistics": logistics_result
            }

        # =====================================================
        # 6. VERIFICATION AGENT
        # =====================================================

        # In the simulation, assume successful delivery
        # unless the user provides different values.

        if delivered_quantity is None:
            delivered_quantity = quantity_kg

        if actual_destination is None:
            actual_destination = selected_facility

        verification_result = verification_agent.verify_delivery(
            waste_type=waste_type,
            planned_quantity=quantity_kg,
            delivered_quantity=delivered_quantity,
            planned_destination=selected_facility,
            actual_destination=actual_destination
        )

        # =====================================================
        # 7. MANAGER DECISION
        # =====================================================

        if verification_result["replan_required"]:

            return {
                "manager": self.name,
                "status": "replanning_required",
                "message": "Verification failed. Manager Agent requires replanning.",
                "waste_intelligence": waste_analysis,
                "resource_recovery": recovery_analysis,
                "facility": facility_result,
                "environment": environment_result,
                "logistics": logistics_result,
                "verification": verification_result
            }

        # =====================================================
        # FINAL SUCCESSFUL RESULT
        # =====================================================

        return {
            "manager": self.name,
            "status": "completed",
            "message": "Waste successfully processed through the EcoNexus AI workflow.",

            "waste_intelligence": waste_analysis,

            "resource_recovery": recovery_analysis,

            "facility": facility_result,

            "environment": environment_result,

            "logistics": logistics_result,

            "verification": verification_result,

            "final_decision": {
                "action": recovery_analysis["recommended_option"],
                "facility": selected_facility,
                "transport": logistics_result["truck_id"],
                "environmental_impact": environment_result["impact_level"],
                "verification": verification_result["status"]
            }
        }


# Create Manager Agent object
manager_agent = ManagerAgent()