from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime
from app.models.evidence import Evidence  
from enum import Enum
from app.models.users import Lawyer

class Coordinates(BaseModel):
    type: Literal["Point"]
    coordinates: List[float]  # [longitude, latitude]

class Location(BaseModel):
    country: str
    region: str
    coordinates: Coordinates

class Perpetrator(BaseModel):
    name: str
    type: str


class CaseStatus(str,Enum):
    UNDER_INVESTIGATION = "under_investigation"
    CLOSED = "closed"
    ESCALATED = "escalated"

class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CaseBase(BaseModel):
    title: str
    description: Optional[str]
    violation_types: List[str]
    status: CaseStatus
    priority: PriorityLevel
    location: Location
    date_occurred: datetime
    date_reported: datetime
    victims: List[str]  # ObjectId as str
    perpetrators: List[Perpetrator]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    candidate_lawyers: Optional[List[str]] = None  # List of ObjectId as str

class CaseCreate(CaseBase):
    pass  # same as CaseBase, you can customize if needed

class CaseResponse(CaseBase):
    id: Optional[str] = Field(None, alias="_id")
    case_id: str
    evidence: Optional[List[str]] = None  # List of Evidence objects
    created_by: str
    lawyers: Optional[List[Lawyer]] = None  # List of ObjectId as str
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CaseStatusHistory(BaseModel):
    case_id: str
    updated_status: str
    update_date: datetime
    # Example usage in the database
    # This class will represent the history of case status updates.


class StatusUpdate(BaseModel):
    new_status: CaseStatus
