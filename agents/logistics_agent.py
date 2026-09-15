class LogisticsAgent:

    def __init__(self):
        self.name = "Logistics Agent"

    def plan_transport(self, waste_type, quantity, source, facility, distance):
        """
        Select a suitable truck and estimate transportation details.
        """

        # Simulated truck data
        trucks = [
            {
                "id": "TRUCK-01",
                "capacity": 1000,
                "status": "available"
            },
            {
                "id": "TRUCK-02",
                "capacity": 500,
                "status": "available"
            },
            {
                "id": "TRUCK-03",
                "capacity": 750,
                "status": "available"
            }
        ]

        # Find a truck with enough capacity
        selected_truck = None

        for truck in trucks:
            if truck["status"] == "available" and truck["capacity"] >= quantity:
                selected_truck = truck
                break

        if selected_truck is None:
            return {
                "agent": self.name,
                "status": "failed",
                "message": "No suitable truck available"
            }

        # Simple transportation cost
        cost_per_km = 2.5
        transport_cost = distance * cost_per_km

        return {
            "agent": self.name,
            "status": "planned",
            "waste_type": waste_type,
            "quantity_kg": quantity,
            "source": source,
            "destination": facility,
            "truck_id": selected_truck["id"],
            "truck_capacity_kg": selected_truck["capacity"],
            "distance_km": distance,
            "estimated_cost": round(transport_cost, 2)
        }


logistics_agent = LogisticsAgent()