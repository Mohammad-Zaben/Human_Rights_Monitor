from datetime import datetime
from app.database import get_collection

async def case_generate_id() -> str:
   
    
    current_year = datetime.now().year

    counters_collection = await get_collection("counters")

    existing_counter = await counters_collection.find_one({"_id": f"case_id_{current_year}"})
    if not existing_counter:
        await counters_collection.insert_one({"_id": f"case_id_{current_year}", "sequence": 0})

    result = await counters_collection.find_one_and_update(
        {"_id": f"case_id_{current_year}"},
        {"$inc": {"sequence": 1}},
        return_document=True  
    )

    sequence_number = result["sequence"]
    unique_id = f"HRM-{current_year}-{sequence_number:04d}"

    return unique_id
