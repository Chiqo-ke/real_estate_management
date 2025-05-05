from pydantic import BaseModel
from typing import Optional

class PropertyBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    total_units: int
    available_units: int

class PropertyCreate(PropertyBase):
    pass

class Property(PropertyBase):
    property_id: int

    class Config:
        from_attributes = True
