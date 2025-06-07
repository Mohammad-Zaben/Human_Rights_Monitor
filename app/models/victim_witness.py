from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Demographics(BaseModel):
    gender: str
    age: int
    ethnicity: str
    occupation: str

class ContactInfo(BaseModel):
    email: str
    phone: str
    secure_messaging: str

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RiskAssessment(BaseModel):
    level: RiskLevel
    threats: List[str]
    protection_needed: bool

class SupportService(BaseModel):
    type: str
    provider: str
    status: str

class VictimWitnessType(str, Enum):
    VICTIM = "victim"
    WITNESS = "witness"

class VictimWitnessBase(BaseModel):
    type: VictimWitnessType
    anonymous: bool
    demographics: Demographics
    contact_info: ContactInfo
    risk_assessment: RiskAssessment
    support_services: List[SupportService]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class VictimWitnessCreate(VictimWitnessBase):
    pass  

class VictimWitnessResponse(VictimWitnessBase):
    id: Optional[str] = Field(None, alias="_id")
    vic_wit_id: str
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

