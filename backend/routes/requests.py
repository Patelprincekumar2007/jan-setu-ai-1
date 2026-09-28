from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import CitizenRequest
from backend.schemas import (
    CitizenRequestCreate,
    CitizenRequestCreateResponse,
    CitizenRequestDetailResponse,
    RequestLocation,
)
from backend.utils import generate_unique_reference_id
from backend.gemini_service import extract_request_intelligence

router = APIRouter(prefix="/api/requests", tags=["Citizen Requests"])

@router.post(
    "",
    response_model=CitizenRequestCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a citizen development request with AI structuring",
)
def create_citizen_request(
    payload: CitizenRequestCreate,
    db: Session = Depends(get_db),
):
    """Store a citizen development request, execute structured Gemini extraction, and issue a reference tracking ID."""
    ref_id = generate_unique_reference_id(db)

    # Phase 2 Step 2: Attempt Gemini structured extraction
    ai_result = extract_request_intelligence(
        citizen_text=payload.citizen_request,
        state=payload.state,
        district=payload.district,
        locality=payload.locality,
        user_category=payload.category,
    )

    if ai_result:
        ai_extraction_status = "PROCESSED"
        language = ai_result.language
        problem_summary = ai_result.problem_summary
        severity = ai_result.severity
        affected_group = ai_result.affected_group
        location_hint = ai_result.location_hint
    else:
        ai_extraction_status = "NOT_PROCESSED"
        language = None
        problem_summary = None
        severity = None
        affected_group = None
        location_hint = None

    new_request = CitizenRequest(
        reference_id=ref_id,
        citizen_request=payload.citizen_request,
        state=payload.state,
        district=payload.district,
        locality=payload.locality,
        category=payload.category,
        affected_households=payload.affected_households,
        status="RECEIVED",
        ai_extraction_status=ai_extraction_status,
        language=language,
        problem_summary=problem_summary,
        severity=severity,
        affected_group=affected_group,
        location_hint=location_hint,
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return CitizenRequestCreateResponse(
        success=True,
        reference_id=new_request.reference_id,
        status=new_request.status,
        ai_extraction_status=new_request.ai_extraction_status,
        message="Request submitted successfully.",
    )

@router.get(
    "/{reference_id}",
    response_model=CitizenRequestDetailResponse,
    summary="Track a citizen development request by reference ID",
)
def get_citizen_request(
    reference_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve public lifecycle status of a citizen request by reference code."""
    clean_ref = reference_id.strip().upper()
    record = db.query(CitizenRequest).filter(CitizenRequest.reference_id == clean_ref).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    return CitizenRequestDetailResponse(
        reference_id=record.reference_id,
        status=record.status,
        ai_extraction_status=record.ai_extraction_status,
        created_at=record.created_at.isoformat() if record.created_at else "",
        category=record.category,
        location=RequestLocation(
            state=record.state,
            district=record.district,
            locality=record.locality,
        ),
    )
