from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Evidence(BaseModel):
    type: str
    url: str  # or HttpUrl if it's a full URL
    description: Optional[str]


class EvidenceCreate(Evidence):
    pass  

class EvidenceResponse(Evidence):
 
    id: Optional[str] = None  # This can be used to return the database ID or any unique identifier
    created_at: Optional[datetime] = None  # Timestamp when the evidence was created
    updated_at: Optional[datetime] = None  # Timestamp when the evidence was last updated

    class Config:
        orm_mode = True  # Allows compatibility with ORM models
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Custom encoder for datetime fields
        }