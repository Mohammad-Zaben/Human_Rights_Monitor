from fastapi import APIRouter, HTTPException, status,Form,UploadFile,File, Depends,Query
from app.database import get_collection
from app.models.cases import CaseBase, CaseResponse , StatusUpdate
from app.routes.evidence import create_evidence
from datetime import datetime
from app.services.id_genarator import case_generate_id
from pydantic import ValidationError, BaseModel
import json
from app.auth.oauth import get_current_user

router = APIRouter(
    prefix="/case",
    tags=["Cases"],
    responses={404: {"description": "Not found"}},
)

@router.post("/",response_model=CaseResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create a new case",
            description="Create a new case with all required information. Example for `case_model`: \n\n```json\n{\"title\": \"Test Case\", \"description\": \"A sample case\", \"violation_types\": [\"type1\", \"type2\"], \"status\": \"under_investigation\", \"priority\": \"high\", \"location\": {\"country\": \"Country\", \"region\": \"Region\", \"coordinates\": {\"type\": \"Point\", \"coordinates\": [34.4667, 31.5000]}}, \"date_occurred\": \"2025-06-01T12:00:00\", \"date_reported\": \"2025-06-01T12:00:00\", \"victims\": [\"victim1\"], \"perpetrators\": [{\"name\": \"Perpetrator\", \"type\": \"individual\"}], \"created_by\": \"user_id\"}\n```",
            response_description="The created case with generated ID")
async def create_case(
    case_model: str = Form(..., example='{"title": "Test Case", "description": "A sample case", "violation_types": ["type1", "type2"], "status": "under_investigation", "priority": "high", "location": {"country": "Country", "region": "Region", "coordinates": {"type": "Point", "coordinates": [34.4667, 31.5000]}}, "date_occurred": "2025-06-01T12:00:00", "date_reported": "2025-06-01T12:00:00", "victims": ["victim1"], "perpetrators": [{"name": "Perpetrator", "type": "individual"}], "created_by": "user_id"}'),
    images: list[UploadFile] = File(...),
    current_user: str = Depends(get_current_user)
):

    try:
        case_data = json.loads(case_model)
        case = CaseBase(**case_data)  # do the validation her ,because the pydantic with Form data does not work
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e))


    images_list = []
    for image in images:
        content = await image.read()
        id=await create_evidence(image=content)
        images_list.append(id)

    cases_collection = await get_collection("cases")

    case_data = case.model_dump()

    # Convert enums to strings
    case_data["status"] = case_data["status"].value
    case_data["priority"] = case_data["priority"].value

    case_data["evidence"] = images_list
    case_data["case_id"] = await case_generate_id()
    case_data["created_by"] = current_user.username

    now = datetime.utcnow()
    case_data["created_at"] =  now
    case_data["updated_at"] =  now

    result = await cases_collection.insert_one(case_data)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case"
        )
    case_data["_id"] = str(result.inserted_id)
    return CaseResponse(**case_data)


"""
This file defines the routes for managing cases in the application.
body example:

case_model:
{
    "title": "Environmental Violation",
    "description": "Illegal dumping of hazardous waste",
    "violation_types": ["pollution", "illegal dumping"],
    "status": "under_investigation",
    "priority": "high",
    "location": {
        "country": "CountryName",
        "region": "RegionName",
        "coordinates": {
            "type": "Point",
            "coordinates": [34.4667, 31.5000]
        }
    },
    "date_occurred": "2025-06-01T12:00:00",
    "date_reported": "2025-06-01T12:00:00",
    " candidate_lawyers": ["lawyer1", "lawyer2"],
    "victims": ["VW-2025-0001"],
    "perpetrators": [
        {
            "name": "John Doe",
            "type": "individual"
        },
        {
            "name": "XYZ Corporation",
            "type": "organization"
        }
    ]
}

files example:
- images: [image1.jpg, image2.png]
"""



@router.get("/{case_id}", response_model=CaseResponse, summary="Get a case by ID")
async def get_case(case_id: str, current_user: str = Depends(get_current_user)):
    # if not current_user:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing JWT token")

    cases_collection = await get_collection("cases")
    case = await cases_collection.find_one({"case_id": case_id})
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    case["_id"] = str(case["_id"])
    return CaseResponse(**case)
"""
this dont need body or any data , just add the case id in the url
Example: GET http://127.0.0.1:8000/case/HRM-2025-0002
"""




@router.get("/", response_model=list[CaseResponse], summary="Get all cases")
async def get_all_cases(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing JWT token")

    cases_collection = await get_collection("cases")
    cases = []
    
    async for case in cases_collection.find():
        case["_id"] = str(case["_id"])
        cases.append(CaseResponse(**case))
    
    return cases

"""This endpoint retrieves all cases from the database.
Example: GET http://"""





@router.get("/search/", response_model=list[CaseResponse], summary="Search cases by field")
async def search_cases(field: str = Query(..., description="Field to search by (e.g., 'title', 'status')"),
                       value: str = Query(..., description="Value to search for in the specified field"),
                       current_user: str = Depends(get_current_user)):
    cases_collection = await get_collection("cases")

    # Handle date fields by converting value to datetime if applicable
    if field in ["date_occurred", "date_reported"]:
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Use ISO 8601 format (e.g., '2025-06-01T12:00:00')."
            )

    # Query the database
    query = {field: value}
    cases = []
    async for case in cases_collection.find(query):
        case["_id"] = str(case["_id"])
        cases.append(CaseResponse(**case))

    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cases found matching the query."
        )

    return cases
"""
dont need body or any data , just add the field and value in the url
Example: GET http://127.0.0.1:8000/case/search/?field=priority&value=high
"""



@router.delete("/{case_id}", summary="Delete a case by ID")
async def delete_case(case_id: str, current_user: str = Depends(get_current_user)):
    cases_collection = await get_collection("cases")
    
    result = await cases_collection.delete_one({"case_id": case_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return {"detail": "Case deleted successfully"}
"""This endpoint deletes a case by its ID.
Example: DELETE http://case/HRM-2025-0002"""



@router.patch("/{case_id}", summary="Update case status")
async def update_case_status(case_id: str, new_status: StatusUpdate, current_user: str = Depends(get_current_user)):
    history_collection = await get_collection("case_status_history")

    # Find the case using case_id
    cases_collection = await get_collection("cases")
    case = await cases_collection.find_one({"case_id": case_id})

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Extract the new status value
    status_value = new_status.new_status

    # Update the case status
    update_result = await cases_collection.update_one(
        {"case_id": case_id},
        {"$set": {"status": status_value, "updated_at": datetime.utcnow()}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update case status")

    # Add to history collection
    history_entry = {
        "case_id": case_id,
        "updated_status": status_value,
        "update_date": datetime.utcnow()
    }
    await history_collection.insert_one(history_entry)

    return {"message": "Case status updated successfully", "updated_status": status_value}
"""This endpoint updates the status of a case by its ID.
Example: PATCH http://case/HRM-2025-0002
Request body:
{ 
    "new_status": "closed"
}
The status can be one of the following: "new", "under_investigation", "resolved", "closed"
"""


class Lawyer(BaseModel):
    name: str

@router.patch("/{case_id}/add-lawyers", summary="Add lawyers to a case")
async def add_lawyer_to_case(
    case_id: str,
    lawyers: list[Lawyer],  # List of lawyers from the request body
    current_user: str = Depends(get_current_user)
):
    cases_collection = await get_collection("cases")

    # Find the case using case_id
    case = await cases_collection.find_one({"case_id": case_id})

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Add lawyers to the case
    update_result = await cases_collection.update_one(
        {"case_id": case_id},
        {"$push": {"lawyers": {"$each": [lawyer.model_dump() for lawyer in lawyers]}}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add lawyers to the case")

    return {"message": "Lawyers added successfully", "lawyers": lawyers}
"""
This endpoint adds one or more lawyers to a case by its ID.
Example: PATCH http://case/HRM-2025-0002/add-lawyers
Request body:
[
        {
            "name": "Lawyer One"
        },
        {
            "name": "Lawyer Two"
        }
]
"""
@router.get("/cases-need-lawyers", response_model=list[CaseResponse], summary="Get cases that need assigen a lawyers")
async def get_cases_need_lawyers(current_user: str = Depends(get_current_user)):
    cases_collection = await get_collection("cases")
    
    # Find cases that have no lawyers assigned
    query = {"lawyers": {"$exists": False}}
    cases = []
    
    async for case in cases_collection.find(query):
        case["_id"] = str(case["_id"])
        cases.append(CaseResponse(**case))
    
    return cases