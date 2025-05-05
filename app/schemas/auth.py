from pydantic import BaseModel, EmailStr

class TenantLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LeaseDetails(BaseModel):
    property_id: int
    unit_number: str
    start_date: str
    end_date: str
    monthly_rent: float
    security_deposit: float

class TenantCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    identification_type: str | None = None
    identification_number: str | None = None
    lease_details: LeaseDetails
