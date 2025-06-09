# This file defines the Incident_Report model

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional,Literal
from datetime import datetime
from enum import Enum

class Coordinates(BaseModel):
    type: Literal["Point"]  # Correctly define "Point" as a string literal
    coordinates: List[float]  # [longitude, latitude]

class Location(BaseModel):
    country: str
    city: str
    coordinates: Coordinates

class ContactInfo(BaseModel):
    email: EmailStr
    phone: str
    preferred_contact: str

class Evidence(BaseModel):
    type: str
    url: str
    description: Optional[str]

class ReporterType(str, Enum):
    VICTIM = "victim"
    WITNESS = "witness"
    OTHER = "other"


class StatusEnum(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentDetails(BaseModel):
    date: datetime
    location: Location
    description: str
    violation_types: List[str]

class IncidentReportBase(BaseModel):
    reporter_type: ReporterType
    anonymous: bool
    contact_info: ContactInfo
    incident_details: IncidentDetails
    status:StatusEnum
    assigned_to: Optional[str] = None  # ObjectId as str
    created_at: Optional[datetime] = None

class IncidentReportCreate(IncidentReportBase):
    pass

class IncidentReportResponse(IncidentReportBase):
    id: Optional[str] = Field(None, alias="_id")
    report_id: str
    evidence: Optional[List[str]] = None
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UpdateStatusRequest(BaseModel):
    status: StatusEnum
