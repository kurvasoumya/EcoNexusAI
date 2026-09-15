from typing import Dict

from agents.rag_agent import rag_agent


class WasteIntelligenceAgent:

    def analyze(
        self,
        waste_type: str,
        quantity_kg: float,
        contamination: float,
        source: str
    ) -> Dict:

        waste = waste_type.lower()

        # Basic waste classification
        if waste in ["food", "organic", "vegetable", "fruit"]:
            category = "Organic"

        elif waste in ["plastic", "bottle", "polythene"]:
            category = "Plastic"

        elif waste in ["paper", "cardboard"]:
            category = "Paper"

        elif waste in ["metal", "glass"]:
            category = "Metal/Glass"

        elif waste in ["e-waste", "electronic", "electronics"]:
            category = "E-Waste"

        elif waste in ["hazardous", "chemical", "toxic"]:
            category = "Hazardous"

        elif waste in ["textile", "clothing", "fabric"]:
            category = "Textile"

        elif waste in ["construction", "concrete", "bricks"]:
            category = "Construction"

        else:
            category = "Residual"

        # Contamination classification
        if contamination <= 10:
            contamination_level = "Low"

        elif contamination <= 30:
            contamination_level = "Medium"

        else:
            contamination_level = "High"

        # Priority
        if quantity_kg >= 500:
            priority = "High"

        elif quantity_kg >= 100:
            priority = "Medium"

        else:
            priority = "Low"

        # Recovery status
        if contamination <= 40:
            recovery_status = "Suitable for recovery"

        else:
            recovery_status = "Requires pre-treatment"

        # RAG knowledge retrieval
        query = f"""
        Waste type: {waste_type}
        Quantity: {quantity_kg} kg
        Contamination: {contamination} percent

        What are the recommended handling, recovery,
        recycling and treatment options for this waste?
        """

        knowledge_results = rag_agent.search(query, k=3)

        return {

            "source": source,

            "original_waste_type": waste_type,

            "category": category,

            "quantity_kg": quantity_kg,

            "contamination_percent": contamination,

            "contamination_level": contamination_level,

            "priority": priority,

            "recovery_status": recovery_status,

            "rag_knowledge": knowledge_results
        }


waste_intelligence_agent = WasteIntelligenceAgent()