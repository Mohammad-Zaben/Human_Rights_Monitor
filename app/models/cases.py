from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime
from app.models.evidence import Evidence  
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


class CaseBase(BaseModel):
    title: str
    description: Optional[str]
    violation_types: List[str]
    status: Literal["under_investigation", "closed", "escalated"]
    priority: Literal["low", "medium", "high"]
    location: Location
    date_occurred: datetime
    date_reported: datetime
    victims: List[str]  # ObjectId as str
    perpetrators: List[Perpetrator]
    created_by: str  # ObjectId as str
    created_at: datetime
    updated_at: datetime

class CaseCreate(CaseBase):
    pass  # same as CaseBase, you can customize if needed

class CaseResponse(CaseBase):
    id: Optional[str] = Field(None, alias="_id")
    case_id: str
    evidence: Optional[List[str]] = None  # List of Evidence objects
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
