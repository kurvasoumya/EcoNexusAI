class EnvironmentAgent:

    def __init__(self):
        self.name = "Environment Agent"

    def evaluate(self, waste_type, quantity, distance):
        """
        Evaluate the environmental impact of a waste-management decision.
        """

        # Basic emission factors
        emission_factors = {
            "organic": 0.05,
            "plastic": 0.20,
            "paper": 0.08,
            "metal_glass": 0.10,
            "residual": 0.30
        }

        factor = emission_factors.get(waste_type.lower(), 0.15)

        # Estimated transport emissions
        transport_emission = distance * quantity * 0.001

        # Estimated processing emissions
        processing_emission = quantity * factor

        total_emission = transport_emission + processing_emission

        # Environmental score
        if total_emission < 50:
            score = 90
            level = "low impact"
        elif total_emission < 100:
            score = 70
            level = "Good"
        elif total_emission < 200:
            score = 50
            level = "Moderate"
        else:
            score = 30
            level = "High Impact"

        return {
            "agent": self.name,
            "waste_type": waste_type,
            "quantity_kg": quantity,
            "distance_km": distance,
            "estimated_emission": round(total_emission, 2),
            "environment_score": score,
            "impact_level": level
        }


environment_agent = EnvironmentAgent()