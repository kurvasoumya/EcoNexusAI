from agents.rag_agent import rag_agent


class ResourceRecoveryAgent:

    def analyze_recovery(
        self,
        waste_type,
        quantity,
        contamination
    ):

        # Ask the RAG system for relevant recovery knowledge
        query = f"""
        What are the best recovery, recycling, treatment,
        composting, anaerobic digestion or waste-to-energy
        options for {waste_type} waste?

        Quantity: {quantity} kg
        Contamination: {contamination} percent
        """

        knowledge_results = rag_agent.search(query, k=3)

        # Basic recovery options
        waste = waste_type.lower()

        if waste in ["food", "organic", "vegetable", "fruit"]:
            options = [
                "Composting",
                "Anaerobic Digestion",
                "Waste-to-Energy"
            ]

        elif waste in ["plastic", "bottle", "polythene"]:
            options = [
                "Plastic Recycling",
                "Waste-to-Energy"
            ]

        elif waste in ["paper", "cardboard"]:
            options = [
                "Paper Recycling",
                "Waste-to-Energy"
            ]

        elif waste in ["metal", "glass", "metal_glass"]:
            options = [
                "Material Recovery",
                "Recycling"
            ]

        elif waste in ["e-waste", "electronic", "electronics"]:
            options = [
                "Authorized E-Waste Recycling",
                "Specialized Recovery"
            ]

        elif waste in ["hazardous", "chemical", "toxic"]:
            options = [
                "Specialized Hazardous Waste Treatment"
            ]

        elif waste in ["textile", "clothing", "fabric"]:
            options = [
                "Reuse",
                "Textile Recycling",
                "Fiber Recovery"
            ]

        elif waste in ["construction", "concrete", "bricks"]:
            options = [
                "Material Recovery",
                "Reuse",
                "Recycling"
            ]

        else:
            options = [
                "Waste-to-Energy",
                "Safe Disposal"
            ]

        # Adjust recovery pathway according to contamination
        if contamination > 70:
            recommended_option = "Pre-Treatment Required"

        elif contamination > 50:
            non_recycling_options = [
                option
                for option in options
                if "Recycling" not in option
            ]

            recommended_option = (
                non_recycling_options[0]
                if non_recycling_options
                else "Pre-Treatment Required"
            )

        elif contamination > 30:
            recommended_option = (
                options[0]
                if options
                else "Pre-Treatment Required"
            )

        else:
            recommended_option = (
                options[0]
                if options
                else "Safe Disposal"
            )

        return {
            "waste_type": waste_type,
            "quantity_kg": quantity,
            "contamination_percent": contamination,
            "recovery_options": options,
            "recommended_option": recommended_option,
            "rag_knowledge": knowledge_results
        }


resource_recovery_agent = ResourceRecoveryAgent()