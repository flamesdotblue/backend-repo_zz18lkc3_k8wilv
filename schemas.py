"""
Database Schemas for Blood Donor Nepal

Each Pydantic model represents a collection in MongoDB. The collection name is the
lowercased class name.

- User -> "user"
- Request -> "request"
"""
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    """
    Donor/User schema
    Collection: "user"
    """
    full_name: str = Field(..., description="Full name of the user")
    phone: str = Field(..., description="Contact phone number")
    blood_group: str = Field(..., description="Blood group, e.g., A+, O-, AB+")
    age: int = Field(..., ge=18, le=80, description="Age in years")
    city: str = Field(..., description="City name")
    latitude: Optional[float] = Field(None, description="Latitude from maps API")
    longitude: Optional[float] = Field(None, description="Longitude from maps API")
    password: str = Field(..., description="Password (MVP - stored as plain text)")
    role: str = Field("Donor", description="User role, default Donor")
    verified: bool = Field(False, description="Verification status")

class Request(BaseModel):
    """
    Blood Request schema
    Collection: "request"
    """
    required_blood_group: str = Field(..., description="Requested blood group")
    required_units: int = Field(..., ge=1, le=20, description="Units needed (pints)")
    hospital_name: str = Field(..., description="Hospital name")
    contact_name: str = Field(..., description="Primary contact person name")
    contact_phone: str = Field(..., description="Primary contact phone")
    city: str = Field(..., description="City where blood is needed")
    latitude: Optional[float] = Field(None, description="Latitude from maps API")
    longitude: Optional[float] = Field(None, description="Longitude from maps API")
    status: str = Field("Pending", description="Request status")
