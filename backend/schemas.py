from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

# Phase 2 Step 2: Gemini Extraction Schema with strict category and severity literals
class GeminiExtractionResult(BaseModel):
    language: str = Field(..., description="Detected language of submission (e.g. English, Hindi, Marathi, etc.)")
    category: Literal["Water", "Roads", "Healthcare", "Sanitation", "Other"] = Field(
        ..., description="Standardised civic infrastructure category"
    )
    problem_summary: str = Field(..., description="Objective administrative summary of the infrastructure problem")
    severity: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        ..., description="Assessed civic severity index"
    )
    affected_group: str = Field(..., description="Identified group or community affected")
    location_hint: str = Field(..., description="Specific location reference, landmark, or ward mention")

class CitizenRequestCreate(BaseModel):
    citizen_request: str = Field(..., min_length=5, max_length=5000, description="Description of citizen civic need or infrastructure issue")
    state: str = Field(..., min_length=1, max_length=100, description="State or Union Territory")
    district: str = Field(..., min_length=1, max_length=100, description="District name")
    locality: str = Field(..., min_length=1, max_length=150, description="Locality, village, or ward name")
    category: str = Field(..., min_length=1, max_length=100, description="Primary infrastructure category")
    affected_households: Optional[int] = Field(None, ge=0, le=10_000_000, description="Estimated number of affected households")

    @field_validator("citizen_request", "state", "district", "locality", "category", mode="before")
    @classmethod
    def check_not_empty_or_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Field cannot be empty or whitespace only.")
            return cleaned
        raise ValueError("Field must be a valid string.")

class CitizenRequestCreateResponse(BaseModel):
    success: bool = True
    reference_id: str
    status: str
    ai_extraction_status: Literal["PROCESSED", "NOT_PROCESSED"] = "NOT_PROCESSED"
    message: str = "Request submitted successfully."

class RequestLocation(BaseModel):
    state: str
    district: str
    locality: str

class CitizenRequestDetailResponse(BaseModel):
    reference_id: str
    status: str
    ai_extraction_status: Optional[str] = "NOT_PROCESSED"
    created_at: str
    category: str
    location: RequestLocation
