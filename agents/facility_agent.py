import json
from pathlib import Path

class FacilityAgent:

    def __init__(self):

        self.name = "Facility Agent"
        self.data_file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "facilities.json"
        )

        self.facilities = [

            {
                "name": "GreenCompost",
                "waste_type": "organic",
                "accepted_processes": [
                    "Composting"
                ],
                "capacity": 500,
                "status": "available"
            },
       
            {
                "name": "BioEnergy",
                "waste_type": "organic",
                "accepted_processes": [
                    "Anaerobic Digestion",
                    "Waste-to-Energy"
                ],
                "capacity": 700,
                "status": "available"
            },

            {
                "name": "PlasticRecycle",
                "waste_type": "plastic",
                "accepted_processes": [
                    "Plastic Recycling"
                ],
                "capacity": 600,
                "status": "available"
            },

            {
                "name": "PaperRecycle",
                "waste_type": "paper",
                "accepted_processes": [
                    "Paper Recycling"
                ],
                "capacity": 500,
                "status": "available"
            },

            {
                "name": "MaterialRecovery",
                "waste_type": "metal_glass",
                "accepted_processes": [
                    "Material Recovery",
                    "Recycling"
                ],
                "capacity": 400,
                "status": "available"
            },
            
            {
                "name": "EWasteFacility",
                "waste_type": "e-waste",
                "accepted_processes": [
                "Authorized E-Waste Recycling",
                "Specialized Recovery"
                ],
                "capacity": 300,
                "status": "available"
            },
            {
                "name": "WasteEnergy",
                "waste_type": "residual",
                "accepted_processes": [
                    "Waste-to-Energy"
                ],
                "capacity": 1000,
                "status": "available"
            }
        ]
      
    # ========================================================
    # LOAD / SAVE FACILITY STATE
    # ========================================================

    def _load_state(self):

        if not self.data_file.exists():

            

            return

        try:

            with open(
                self.data_file,
                "r",
                encoding="utf-8"
            ) as file:

                saved_facilities = json.load(file)

            if isinstance(saved_facilities, list):

                self.facilities = saved_facilities

        except (
            json.JSONDecodeError,
            OSError
        ):

            

    def _save_state(self):

        self.data_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.data_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.facilities,
                file,
                indent=4
            )


    # ========================================================
    # FIND SUITABLE FACILITIES
    # ========================================================

    def find_facilities(
        self,
        waste_type,
        quantity,
        recovery_options=None
    ):

        suitable_facilities = []

        for facility in self.facilities:

            # Waste compatibility
            if facility["waste_type"].lower() != waste_type.lower():
                continue

            # Capacity check
            if facility["capacity"] < quantity:
                continue

            # Status check
            if facility["status"] != "available":
                continue

            # Recovery compatibility
            if recovery_options:

                compatible = False

                for option in recovery_options:

                    for process in facility["accepted_processes"]:

                        if (
                            option.lower()
                            in process.lower()
                            or
                            process.lower()
                            in option.lower()
                        ):
                            compatible = True

                if not compatible:
                    continue

            suitable_facilities.append(facility)

        # ====================================================
        # No facility
        # ====================================================

        if not suitable_facilities:

            return {
                "status": "no_facility",

                "message": (
                    "No suitable facility is currently "
                    "available for this waste and recovery pathway."
                ),

                "facilities": []
            }

        # ====================================================
        # Facilities found
        # ====================================================

        return {

            "status": "facilities_found",

            "waste_type": waste_type,

            "quantity_kg": quantity,

            "facilities": suitable_facilities
        }


    # ========================================================
    # UPDATE CAPACITY
    # ========================================================

    def update_capacity(
        self,
        facility_name,
        used_capacity
    ):

        for facility in self.facilities:

            if (
                facility["name"].lower()
                == facility_name.lower()
            ):

                if used_capacity > facility["capacity"]:

                    return {
                        "status": "failed",

                        "message": (
                            "Used capacity exceeds "
                            "available capacity."
                        )
                    }

                facility["capacity"] -= used_capacity

                if facility["capacity"] == 0:

                    facility["status"] = "full"

                
                return {

                    "status": "updated",

                    "facility": facility["name"],

                    "remaining_capacity":
                        facility["capacity"],

                    "facility_status":
                        facility["status"]
                }

        return {

            "status": "failed",

            "message": "Facility not found."
        }
        def set_capacity(
            self,
            facility_name,
            new_capacity
        ):

            if new_capacity < 0:
                return {
                    "status": "failed",
                    "message": "Capacity cannot be negative."
                }

            for facility in self.facilities:

                if (
                    facility["name"].lower()
                    == facility_name.lower()
                ):

                    facility["capacity"] = int(new_capacity)

                    if facility["capacity"] == 0:
                        facility["status"] = "full"
                    elif facility["status"] == "full":
                        facility["status"] = "available"

                    

                return {
                    "status": "updated",
                    "facility": facility["name"],
                    "new_capacity": facility["capacity"],
                    "facility_status": facility["status"]
                }

        return {
            "status": "failed",
            "message": "Facility not found."
        }   

    # ========================================================
    # UPDATE STATUS
    # ========================================================

    def update_status(
        self,
        facility_name,
        new_status
    ):

        valid_statuses = [
            "available",
            "maintenance",
            "offline",
            "full"
        ]

        if new_status.lower() not in valid_statuses:

            return {

                "status": "failed",

                "message": "Invalid facility status."
            }

        for facility in self.facilities:

            if (
                facility["name"].lower()
                == facility_name.lower()
            ):

               facility["status"] = new_status.lower()

                return {

                    "status": "updated",

                    "facility": facility["name"],

                    "new_status":
                        facility["status"]
                }

        return {

            "status": "failed",

            "message": "Facility not found."
        }
   
    # ========================================================
    # GET ALL FACILITIES
    # ========================================================

    def get_facilities(self):

        return {

            "status": "success",

            "facilities": self.facilities
        }


facility_agent = FacilityAgent()