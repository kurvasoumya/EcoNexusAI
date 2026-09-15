from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.workflow import waste_workflow
from agents.facility_agent import facility_agent


app = FastAPI(
    title="EcoNexus AI",
    description="Agentic AI-Based Autonomous Waste-to-Resource Management Network",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# INPUT MODELS
# ============================================================

class WasteInput(BaseModel):
    waste_type: str
    quantity_kg: float = Field(gt=0)
    contamination: float = Field(ge=0, le=100)
    source: str
    distance: float = Field(ge=0)
    delivered_quantity: float = Field(ge=0)
    actual_destination: str


class CapacityUpdate(BaseModel):
    facility_name: str
    used_capacity: float


class StatusUpdate(BaseModel):
    facility_name: str
    new_status: str

class CapacityUpdate(BaseModel):
    facility_name: str
    new_capacity: int

# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "project": "EcoNexus AI",
        "message": "EcoNexus AI is running",
        "status": "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# PROCESS WASTE
# ============================================================

@app.post("/process-waste")
def process_waste(data: WasteInput):

    state = {
        "waste_type": data.waste_type,
        "quantity_kg": data.quantity_kg,
        "contamination": data.contamination,
        "source": data.source,
        "distance": data.distance,
        "delivered_quantity": data.delivered_quantity,
        "actual_destination": data.actual_destination
    }
    result = waste_workflow.invoke(state)

    final_decision = result.get("final_decision", {})

    return {
    "status": result.get("status", "completed"),
    "message": result.get(
        "message",
        "Waste successfully processed through EcoNexus AI."
    ),
    "waste_type": result.get(
        "waste_type",
        data.waste_type
    ),
    "quantity_kg": result.get(
        "quantity_kg",
        data.quantity_kg
    ),
    "recovery_action": final_decision.get(
         "action"
    ),
    "facility": final_decision.get(
        "facility"
    ),
    "transport": final_decision.get(
        "transport"
    ),
    "environmental_impact": final_decision.get(
        "environmental_impact"
    ),
    "verification": final_decision.get(
        "verification"
    ),
    "replan_required": result.get(
        "replan_required",
        False
    ),
    "rag_knowledge": result.get(
        "waste_intelligence",
        {}
    ).get(
        "rag_knowledge",
        []
    )
    }


# ============================================================
# GET ALL FACILITIES
# ============================================================

@app.get("/facilities")
def get_facilities():

    return facility_agent.get_facilities()


# ============================================================
# UPDATE FACILITY CAPACITY
# ============================================================

@app.post("/facility/update-capacity")
def update_facility_capacity(data: CapacityUpdate):

    result = facility_agent.update_capacity(
        facility_name=data.facility_name,
        used_capacity=data.used_capacity
    )

    return result


# ============================================================
# UPDATE FACILITY STATUS
# ============================================================

@app.post("/facility/update-status")
def update_facility_status(data: StatusUpdate):

    result = facility_agent.update_status(
        facility_name=data.facility_name,
        new_status=data.new_status
    )

    return result
@app.post("/facility/update-capacity")
def update_facility_capacity(data: CapacityUpdate):

    result = facility_agent.update_capacity(
        facility_name=data.facility_name,
        new_capacity=data.new_capacity
    )

    return result    