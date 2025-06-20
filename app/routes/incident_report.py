# This file defines the routes for Incident_Report

from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, Query
from pydantic import ValidationError
from datetime import datetime
import json
from typing import Optional

from app.models.incident_report import IncidentReportCreate, IncidentReportResponse, UpdateStatusRequest
from app.database import get_collection
from app.services.id_genarator import incident_report_generate_id
from app.routes.evidence import create_evidence
from app.auth.oauth import get_current_user

router = APIRouter()
router = APIRouter(
    prefix="/report",
    tags=["Reports"],
    responses={404: {"description": "Not found"}},
)
@router.post("/", response_model=IncidentReportResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Submit a new incident report",
            description="Submit a new incident report with all required information. Example for `report_model`: \n\n```json\n{\"reporter_type\": \"victim\", \"anonymous\": false, \"contact_info\": {\"email\": \"reporter@example.com\", \"phone\": \"+963912345678\", \"preferred_contact\": \"email\"}, \"incident_details\": {\"date\": \"2023-05-10T00:00:00Z\", \"location\": {\"country\": \"Yemen\", \"city\": \"Taiz\", \"coordinates\": {\"type\": \"Point\", \"coordinates\": [44.0333, 13.5833]}}, \"description\": \"Arbitrary detention of 15 civilians at checkpoint\", \"violation_types\": [\"arbitrary_detention\", \"torture\"]}, \"evidence\": [{\"type\": \"video\", \"url\": \"/evidence/ir0789-1.mp4\", \"description\": \"Checkpoint footage\"}], \"status\": \"new\"}\n```",
            response_description="The created incident report with generated ID")
async def submit_incident_report(
    report_model: str = Form(..., example='{"reporter_type": "victim", "anonymous": false, "contact_info": {"email": "reporter@example.com", "phone": "+963912345678", "preferred_contact": "email"}, "incident_details": {"date": "2023-05-10T00:00:00Z", "location": {"country": "Yemen", "city": "Taiz", "coordinates": {"type": "Point", "coordinates": [44.0333, 13.5833]}}, "description": "Arbitrary detention of 15 civilians at checkpoint", "violation_types": ["arbitrary_detention", "torture"]}, "evidence": [{"type": "video", "url": "/evidence/ir0789-1.mp4", "description": "Checkpoint footage"}], "status": "new"}'),
    images: list[UploadFile] = File(...),
    current_user: str = Depends(get_current_user)
):

    try:
        report_data = json.loads(report_model)
        report = IncidentReportCreate(**report_data)  # Validate using Pydantic

        # Validate file types
        allowed_types = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}
        for image in images:
            if image.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {image.content_type}. Allowed types are: {', '.join(allowed_types)}"
                )

    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    images_list = []
    for image in images:
        content = await image.read()
        id = await create_evidence(image=content)
        images_list.append(id)

    reports_collection = await get_collection("incident_reports")

    report_data = report.model_dump()

    report_data["evidence"] = images_list
    report_data["report_id"] = await incident_report_generate_id()

    now = datetime.utcnow()
    report_data["created_at"] = now
    report_data["created_by"] = current_user.username
    result = await reports_collection.insert_one(report_data)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit incident report"
        )
    report_data["_id"] = str(result.inserted_id)
   
    return IncidentReportResponse(**report_data)
"""
bodey example:
report_model:
{
    "reporter_type": "victim",
    "anonymous": false,
    "contact_info": {
        "email": "reporter@example.com",
        "phone": "+963912345678",
        "preferred_contact": "email"
    },
    "incident_details": {
        "date": "2023-05-10T00:00:00Z",
        "location": {
            "country": "Yemen",
            "city": "Taiz",
            "coordinates": {
                "type": "Point",
                "coordinates": [44.0333, 13.5833]
            }
        },
        "description": "Arbitrary detention of 15 civilians at checkpoint",
        "violation_types": ["arbitrary_detention", "torture"]
    },
    "status": "new"
}

file example:
images: [
    {image1.jpg},
    {image2.jpg}
]
"""

@router.get("/", response_model=list[IncidentReportResponse], summary="List reports")
async def list_reports(
    status: Optional[str] = Query(None, description="Filter by report status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    location: Optional[str] = Query(None, description="Filter by location"),
    current_user: str = Depends(get_current_user)
):
    reports_collection = await get_collection("incident_reports")

    query = {}
    if status:
        query["status"] = status
    if start_date and end_date:
        query["incident_details.date"] = {"$gte": start_date, "$lte": end_date}
    if location:
        query["incident_details.location.country"] = {"$regex": location, "$options": "i"}

    reports = []
    async for report in reports_collection.find(query):
        report["_id"] = str(report["_id"])
        reports.append(IncidentReportResponse(**report))

    return reports

"""
request example:
GET http://127.0.0.1:8000/report/?location=yemen
"""

@router.get("/total",response_model=int, summary="Get total number of reports")
async def get_total_cases_number(current_user:str= Depends(get_current_user)):
    cases_collection = await get_collection("incident_reports")
    
    # Count the total number of cases
    total_report = await cases_collection.count_documents({})
    
    return total_report


@router.get("/this-month", response_model=int, summary="Get number of reports submitted this month")
async def get_reports_submitted_this_month(current_user: str = Depends(get_current_user)):
    reports_collection = await get_collection("incident_reports")

    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)

    query = {
        "created_at": {
            "$gte": start_of_month,
            "$lt": next_month
        }
    }

    total = await reports_collection.count_documents(query)
    return total


@router.get("/monthly", response_model=list[tuple[int,int]], summary="Get number of reports created per month")
async def get_cases_per_month(current_user: str = Depends(get_current_user)):
    cases_collection = await get_collection("incident_reports")
    
    # Aggregate to count cases per month
    pipeline = [
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}  # Sort by month
        }
    ]
    
    results = await cases_collection.aggregate(pipeline).to_list(length=None)
    
    # Convert results to a list of tuples (month, count)
    monthly_counts = [(int(result["_id"].split("-")[1]), result["count"]) for result in results]
    
    return monthly_counts

@router.patch("/{report_id}", summary="Update report status")
async def update_report_status(
    report_id: str,
    update_data: UpdateStatusRequest,  
    current_user: str = Depends(get_current_user)
):
    reports_collection = await get_collection("incident_reports")

    update_result = await reports_collection.update_one(
        {"report_id": report_id},
        {"$set": {"status": update_data.status, "updated_at": datetime.utcnow()}},
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update report status")

    return {"message": "Report status updated successfully", "status": update_data.status}

"""
request example:

PATCH http://127.0.0.1:8000/report/IR-2025-0001
body example:
{
"status" : "resolved"
}
the allowed status values are: "new","in_progress","resolved","closed"
"""

@router.get("/analytics", summary="Count reports by violation type")
async def count_reports_by_violation_type(current_user: str = Depends(get_current_user)):
    reports_collection = await get_collection("incident_reports")

    pipeline = [
        {"$unwind": "$incident_details.violation_types"},
        {"$group": {"_id": "$incident_details.violation_types", "count": {"$sum": 1}}},
    ]

    analytics = await reports_collection.aggregate(pipeline).to_list(length=None)

    return {"analytics": analytics}

"""
request example:
GET http://127.0.0.1:8000/report/analytics/"""



@router.get("/{username}", response_model=list[IncidentReportResponse], summary="Get all reports by a specific user")
async def get_reports_by_user(
    username: str,
    current_user: str = Depends(get_current_user)
):
    reports_collection = await get_collection("incident_reports")

    # Query reports by username
    query = {"created_by": username}
    reports = []

    async for report in reports_collection.find(query):
        report["_id"] = str(report["_id"])
        reports.append(IncidentReportResponse(**report))

    if not reports:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reports found for the specified user."
        )

    return reports

"""
request example:
GET http://127.0.0.1:8000/report/<username>
example:
GET http://127.0.0.1:8000/report/zaben
"""