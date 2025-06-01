from fastapi import APIRouter, HTTPException, status,Form,UploadFile,File, Depends
from app.database import get_collection
from app.models.cases import CaseBase, CaseResponse
from app.routes.evidence import create_evidence
from datetime import datetime
from app.services.id_genarator import case_generate_id
from pydantic import ValidationError
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
        case = CaseBase(**case_data)  # Apply Pydantic validation here
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e))


    images_list = []
    for image in images:
        content = await image.read()
        id=await create_evidence(image=content)
        images_list.append(id)

    cases_collection = await get_collection("cases")

    case_data = case.model_dump()
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



