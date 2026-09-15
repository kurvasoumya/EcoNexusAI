from agents.workflow import waste_workflow


scenarios = [
    {
        "name": "Food Waste",
        "waste_type": "food",
        "quantity_kg": 100,
        "contamination": 5,
        "source": "restaurant",
        "distance": 10,
        "delivered_quantity": 100,
        "actual_destination": "GreenCompost"
    },
    {
        "name": "Plastic Waste",
        "waste_type": "plastic",
        "quantity_kg": 100,
        "contamination": 5,
        "source": "shopping_center",
        "distance": 15,
        "delivered_quantity": 100,
        "actual_destination": "PlasticRecycle"
    },
    {
        "name": "Paper Waste",
        "waste_type": "paper",
        "quantity_kg": 100,
        "contamination": 5,
        "source": "office",
        "distance": 12,
        "delivered_quantity": 100,
        "actual_destination": "PaperRecycle"
    },
    {
        "name": "Metal Waste",
        "waste_type": "metal",
        "quantity_kg": 100,
        "contamination": 5,
        "source": "workshop",
        "distance": 20,
        "delivered_quantity": 100,
        "actual_destination": "MaterialRecovery"
    },
    {
        "name": "E-Waste",
        "waste_type": "e-waste",
        "quantity_kg": 100,
        "contamination": 5,
        "source": "electronics_store",
        "distance": 25,
        "delivered_quantity": 100,
        "actual_destination": "EWasteFacility"
    }
]


for scenario in scenarios:

    print("\n========================================")
    print(scenario["name"])
    print("========================================")

    state = {
        "waste_type": scenario["waste_type"],
        "quantity_kg": scenario["quantity_kg"],
        "contamination": scenario["contamination"],
        "source": scenario["source"],
        "distance": scenario["distance"],
        "delivered_quantity": scenario["delivered_quantity"],
        "actual_destination": scenario["actual_destination"]
    }

    try:
        result = waste_workflow.invoke(state)

        print("Final Decision:")
        print(result.get("final_decision"))

        print("Verification:")
        print(result.get("verification"))

    except Exception as e:
        print("ERROR:", e)