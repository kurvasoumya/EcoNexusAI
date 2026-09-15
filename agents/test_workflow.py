from agents.workflow import waste_workflow

state = {
    "waste_type": "food",
    "quantity_kg": 100,
    "contamination": 5,
    "source": "restaurant",
    "distance": 10,
    "delivered_quantity": 100,
    "actual_destination": "WrongFacility"
}

result = waste_workflow.invoke(state)

print("\n==============================")
print("RAG KNOWLEDGE")
print("==============================")

for item in result.get("rag_knowledge", []):
    print("\nSource:", item.get("source"))
    print("Knowledge:", item.get("content"))

print("\n==============================")
print("VERIFICATION RESULT")
print("==============================")

print(result.get("verification"))

print("\n==============================")
print("REPLAN REQUIRED")
print("==============================")

print(result.get("replan_required"))

print("\n==============================")
print("REPLAN RESULT")
print("==============================")

print("Alternative Facility:",
      result.get("alternative_facility"))

print("Alternative Recovery:",
      result.get("alternative_recovery"))

print("Replan Logistics:",
      result.get("replan_logistics"))

print("Replan Environment:",
      result.get("replan_environment"))

print("Replan Verification:",
      result.get("replan_verification"))

print("\n==============================")
print("FINAL DECISION")
print("==============================")

print(result.get("final_decision"))