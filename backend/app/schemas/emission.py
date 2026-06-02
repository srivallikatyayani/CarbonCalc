"""
app/schemas/emission.py
───────────────────────
Pydantic v2 schemas for the Emissions API.

These models define the exact shape of JSON data entering and leaving the API.
They provide automatic validation, type coercion, and OpenAPI documentation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmissionBase(BaseModel):
    """
    Base schema containing fields common to both creation and reading.
    """
    industry_type: str | None = Field(
        None, max_length=100, description="Industry sector for companies"
    )
    electricity_kwh: float | None = Field(
        None, ge=0, description="Purchased electricity in kilowatt-hours (Scope 2)"
    )
    fuel_liters: float | None = Field(
        None, ge=0, description="Direct fuel combustion in liters (Scope 1)"
    )
    flights_taken: int | None = Field(
        None, ge=0, description="Number of flights taken (Scope 3)"
    )
    diet_type: str | None = Field(
        None, max_length=50, description="Dietary habits (e.g., Vegan, Omnivore)"
    )
    waste_generated_kg: float | None = Field(
        None, ge=0, description="Waste generated in kilograms (Scope 3)"
    )
    transportation_km: float | None = Field(
        None, ge=0, description="Fleet transportation distance in kilometers (Scope 3)"
    )
    month: int = Field(
        ..., ge=1, le=12, description="The month of the activity (1-12)"
    )
    year: int = Field(
        ..., ge=2000, description="The year of the activity (e.g., 2026)"
    )


class EmissionCreate(EmissionBase):
    """
    Input schema for POST /emissions/
    
    Includes user_id explicitly since authentication is not yet implemented.
    Once JWT auth is implemented, user_id will be extracted from the token
    and removed from this schema.
    """
    user_id: int = Field(..., description="The ID of the user submitting the data")


class EmissionResponse(EmissionBase):
    """
    Output schema for a single emission record.
    Returned by POST /emissions/ and inside GET /emissions/.
    """
    id: int = Field(..., description="The unique ID of the emission record")
    user_id: int = Field(..., description="The user this record belongs to")
    scope1_kg: float | None = Field(None, description="Scope 1 direct fuel emissions")
    scope2_kg: float | None = Field(None, description="Scope 2 electricity emissions")
    scope3_kg: float | None = Field(None, description="Scope 3 transport and waste emissions")
    total_kg: float | None = Field(None, description="Total carbon footprint in kg CO2e")
    personality: str | None = Field(None, description="DYNAMIC CARBON IDENTITY Tag")
    indian_average_kg: float | None = Field(None, description="Indian average emissions for this sector in kg CO2e")
    percent_difference: float | None = Field(None, description="Percentage difference compared to Indian average")
    comparison_status: str | None = Field(None, description="Comparison status (above_average or below_average)")
    created_at: datetime
    updated_at: datetime

    # Allow Pydantic to read data directly from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)


class EmissionListResponse(BaseModel):
    """
    Output schema for GET /emissions/ (paginated list).
    """
    count: int = Field(..., description="Total number of records returned in this page")
    emissions: list[EmissionResponse]
