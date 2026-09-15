class VerificationAgent:

    def __init__(self):
        self.name = "Verification Agent"

    def verify_delivery(
        self,
        waste_type,
        planned_quantity,
        delivered_quantity,
        planned_destination,
        actual_destination
    ):
        """
        Verify whether the waste was delivered correctly.
        """

        quantity_match = delivered_quantity >= planned_quantity
        destination_match = (
            bool(planned_destination)
            and bool(actual_destination)
            and planned_destination.lower()
            == actual_destination.lower()
)

        if quantity_match and destination_match:
            status = "verified"
            message = "Waste delivery successfully verified"
            replan_required = False

        elif not destination_match:
            status = "failed"
            message = "Waste reached the wrong facility"
            replan_required = True

        else:
            status = "partial"
            message = "Delivered quantity is less than planned"
            replan_required = True

        return {
            "agent": self.name,
            "status": status,
            "waste_type": waste_type,
            "planned_quantity_kg": planned_quantity,
            "delivered_quantity_kg": delivered_quantity,
            "planned_destination": planned_destination,
            "actual_destination": actual_destination,
            "replan_required": replan_required,
            "message": message
        }



verification_agent = VerificationAgent()