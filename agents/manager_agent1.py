from agents.waste_intelligence_agent import WasteIntelligenceAgent
from agents.resource_recovery_agent import resource_recovery_agent
from agents.facility_agent import facility_agent
from agents.environment_agent import environment_agent
from agents.logistics_agent import logistics_agent
from agents.verification_agent import verification_agent


class ManagerAgent:

    def __init__(self):
        self.name = "Manager Agent"
        self.waste_intelligence = WasteIntelligenceAgent()

    # ============================================================
    # WASTE TYPE NORMALIZATION
    # ============================================================

    def normalize_waste_type(self, waste_type):

        waste = waste_type.lower()

        if waste in ["food", "organic", "vegetable", "fruit"]:
            return "organic"

        elif waste in ["bottle", "polythene"]:
            return "plastic"

        elif waste in ["paper", "cardboard"]:
            return "paper"

        elif waste in ["metal", "glass"]:
            return "metal_glass"

        elif waste in ["e-waste", "electronic", "electronics"]:
            return "e-waste"

        elif waste in ["hazardous", "chemical", "toxic"]:
            return "hazardous"

        elif waste in ["textile", "clothing", "fabric"]:
            return "textile"

        elif waste in ["construction", "concrete", "bricks"]:
            return "construction"

        else:
            return "residual"

    # ============================================================
    # FIND COMPATIBLE FACILITY
    # ============================================================

    def find_best_facility(
        self,
        facility_type,
        quantity_kg,
        recovery_options
    ):

        result = facility_agent.find_facilities(
            facility_type,
            quantity_kg,
            recovery_options
        )

        if result["status"] == "no_facility":
            return None, result

        # Choose the first compatible facility
        selected_facility = result["facilities"][0]

        return selected_facility, result

    # ============================================================
    # MAIN PROCESS
    # ============================================================

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

        # ========================================================
        # 1. WASTE INTELLIGENCE
        # ========================================================

        waste_analysis = self.waste_intelligence.analyze(
            waste_type=waste_type,
            quantity_kg=quantity_kg,
            contamination=contamination,
            source=source
        )

        # ========================================================
        # 2. RESOURCE RECOVERY
        # ========================================================

        facility_type = self.normalize_waste_type(waste_type)

        recovery_analysis = resource_recovery_agent.analyze_recovery(
            facility_type,
            quantity_kg,
            contamination
        )

        recovery_options = recovery_analysis.get(
            "recovery_options",
            []
        )

        recommended_option = recovery_analysis.get(
            "recommended_option",
            "Safe Disposal"
        )

        # ========================================================
        # 3. FACILITY AGENT
        # ========================================================

        selected_facility_data, facility_result = self.find_best_facility(
            facility_type,
            quantity_kg,
            recovery_options
        )

        if selected_facility_data is None:

            return {
                "manager": self.name,
                "status": "failed",
                "message": "No compatible facility is currently available.",
                "waste_intelligence": waste_analysis,
                "resource_recovery": recovery_analysis,
                "facility": facility_result
            }

        selected_facility = selected_facility_data["name"]

        # ========================================================
        # 4. ENVIRONMENT AGENT
        # ========================================================

        environment_result = environment_agent.evaluate(
            waste_type=facility_type,
            quantity=quantity_kg,
            distance=distance
        )

        # ========================================================
        # 5. LOGISTICS AGENT
        # ========================================================

        logistics_result = logistics_agent.plan_transport(
            waste_type=facility_type,
            quantity=quantity_kg,
            source=source,
            facility=selected_facility,
            distance=distance
        )

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

        # ========================================================
        # 6. VERIFICATION AGENT
        # ========================================================

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

        # ========================================================
        # 7. AUTOMATIC REPLANNING
        # ========================================================

        if verification_result["replan_required"]:

            # Find another compatible facility
            alternative_result = facility_agent.find_facilities(
                facility_type,
                quantity_kg,
                recovery_options
            )

            alternative_facility = None

            if alternative_result["status"] == "facilities_found":

                for facility in alternative_result["facilities"]:

                    if facility["name"] != selected_facility:

                        alternative_facility = facility
                        break

            # ----------------------------------------------------
            # No alternative facility
            # ----------------------------------------------------

            if alternative_facility is None:

                return {
                    "manager": self.name,
                    "status": "replanning_failed",
                    "message": (
                        "Verification failed and no compatible "
                        "alternative facility is available."
                    ),

                    "original_plan": {
                        "facility": selected_facility,
                        "logistics": logistics_result,
                        "verification": verification_result
                    },

                    "waste_intelligence": waste_analysis,
                    "resource_recovery": recovery_analysis,
                    "facility": facility_result,
                    "environment": environment_result
                }

            # ----------------------------------------------------
            # Replan transportation
            # ----------------------------------------------------

            replan_logistics = logistics_agent.plan_transport(
                waste_type=facility_type,
                quantity=quantity_kg,
                source=source,
                facility=alternative_facility["name"],
                distance=distance
            )

            # ----------------------------------------------------
            # Replan environment
            # ----------------------------------------------------

            replan_environment = environment_agent.evaluate(
                waste_type=facility_type,
                quantity=quantity_kg,
                distance=distance
            )

            return {
                "manager": self.name,
                "status": "replanned",

                "message": (
                    "Verification failed. Manager Agent "
                    "automatically created a new compatible plan."
                ),

                "original_plan": {
                    "facility": selected_facility,
                    "logistics": logistics_result,
                    "verification": verification_result
                },

                "replanned_solution": {
                    "recovery_option": recommended_option,
                    "alternative_facility": alternative_facility["name"],
                    "remaining_capacity": alternative_facility["capacity"],
                    "logistics": replan_logistics,
                    "environment": replan_environment,
                    "next_action": (
                        "Redirect waste to the alternative facility "
                        "and verify again."
                    )
                }
            }

        # ========================================================
        # 8. FINAL SUCCESS
        # ========================================================

        return {
            "manager": self.name,
            "status": "completed",

            "message": (
                "Waste successfully processed through "
                "the EcoNexus AI workflow."
            ),

            "waste_intelligence": waste_analysis,

            "resource_recovery": recovery_analysis,

            "facility": facility_result,

            "environment": environment_result,

            "logistics": logistics_result,

            "verification": verification_result,

            "final_decision": {
                "action": recommended_option,
                "facility": selected_facility,
                "transport": logistics_result["truck_id"],
                "environmental_impact": environment_result["impact_level"],
                "verification": verification_result["status"]
            }
        }


# ============================================================
# CREATE MANAGER AGENT
# ============================================================

manager_agent = ManagerAgent()