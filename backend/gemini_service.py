import json
import logging
from typing import Optional
from google import genai
from google.genai import types
from backend.config import settings
from backend.schemas import GeminiExtractionResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an administrative civic intelligence parsing engine for Digital Public Infrastructure (DPI) in India.
Your task is to analyze raw citizen development requests (which may be submitted in English, Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Gujarati, or other Indic languages) and extract structured civic parameters.

Strict extraction rules:
1. "language": Identify the language of the citizen request (e.g. "English", "Hindi", "Marathi", "Tamil", etc.).
2. "category": Standardise the sector into exactly ONE of: "Water", "Roads", "Healthcare", "Sanitation", "Other".
3. "problem_summary": A clear, objective 1-2 sentence administrative summary of the core civic or infrastructure issue in English.
4. "severity": Assess the severity index as exactly ONE of:
   - "HIGH": Severe acute hazards (e.g., contaminated water outbreak, blocked emergency healthcare access, collapsed road/bridge).
   - "MEDIUM": Chronic or standard infrastructure deficit (e.g., pipeline leak, unpaved school approach road, intermittent power/water).
   - "LOW": Routine maintenance, minor civic grievance, or beautification request.
5. "affected_group": Who is primarily impacted (e.g., "Primary school students", "Patients and PHC staff", "Local farming community", "Ward residents").
6. "location_hint": Any specific landmark, ward, hamlet (pada/tola), or locality mentioned in the text. If none, summarize the locality context.

Return strictly a valid JSON object conforming to the schema."""

def extract_request_intelligence(
    citizen_text: str,
    state: str = "",
    district: str = "",
    locality: str = "",
    user_category: str = "",
) -> Optional[GeminiExtractionResult]:
    """
    Analyzes natural-language citizen request text using Google Gemini and returns structured Pydantic data.
    If the API key is not configured or the API call fails, logs safely and returns None.
    """
    if not settings.gemini_api_key or settings.gemini_api_key.strip() == "" or settings.gemini_api_key == "your_gemini_api_key_here":
        logger.info("Gemini API key is not configured. Skipping automated AI extraction.")
        return None

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        
        user_content = f"""Citizen Request:
\"\"\"{citizen_text}\"\"\"

Administrative Context Provided:
- State: {state}
- District: {district}
- Locality: {locality}
- Initial Category: {user_category}"""

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=GeminiExtractionResult,
                temperature=0.1,
            ),
        )

        if not response or not response.text:
            logger.warning("Gemini returned an empty response.")
            return None

        # Parse JSON and validate with Pydantic schema
        raw_json = json.loads(response.text)
        validated_result = GeminiExtractionResult(**raw_json)
        return validated_result

    except Exception as e:
        # Log failure safely without exposing API keys or sensitive data
        logger.warning(f"Gemini extraction encountered an error: {type(e).__name__} - {str(e)}")
        return None
