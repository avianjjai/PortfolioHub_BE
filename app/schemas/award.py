from pydantic import BaseModel
from datetime import date, datetime
from beanie import PydanticObjectId
from typing import Optional

class AwardBase(BaseModel):
    name: str
    issuer: str
    issue_date: date
    description: str
    category: str

class AwardCreate(AwardBase):
    pass

class Award(AwardBase):
    id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
