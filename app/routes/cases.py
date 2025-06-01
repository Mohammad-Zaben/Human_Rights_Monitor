from fastapi import APIRouter, HTTPException, status,Form,UploadFile,File
from app.database import get_collection
from app.models.cases import CaseBase, CaseResponse
from app.routes.evidence import create_evidence
from datetime import datetime
from app.services.id_genarator import case_generate_id
router = APIRouter(
    prefix="/case",
    tags=["Cases"],
    responses={404: {"description": "Not found"}},
)

@router.post("/",response_model=CaseResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create a new case",
            description="Create a new case with all required information",
            response_description="The created case with generated ID")
async def create_case(case: CaseBase=Form(...),images: list[UploadFile] = File(...)):

    images_list = []
    for image in images:
        content = await image.read()
        id=create_evidence(image=content)
        images_list.append(id)

    cases_collection = await get_collection("cases")

    case_data = case.model_dump()
    case_data["created_at"] = case_data["updated_at"] = datetime.utcnow()
    case_data["evidence"] = images_list
    case_data["case_id"] = case_generate_id()
    result = await cases_collection.insert_one(case_data)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case"
        )
    case_data["_id"] = str(result.inserted_id)
    return CaseResponse(**case_data)



