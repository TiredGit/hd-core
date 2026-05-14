from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.database.models import EmployeeType


class UserFullUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    password: Optional[str] = Field(None, min_length=6)

    address: Optional[str] = None
    apartment: Optional[str] = None
    personal_account: Optional[str] = None


class UserMeResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    role: str
    address: Optional[str] = None
    apartment: Optional[str] = None
    personal_account: Optional[str] = None
    employee_type: Optional[EmployeeType] = None

    model_config = ConfigDict(from_attributes=True)