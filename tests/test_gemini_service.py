import pytest
from unittest.mock import patch, MagicMock
from backend.schemas import GeminiExtractionResult
from backend.gemini_service import extract_request_intelligence
from backend.config import settings

def test_gemini_missing_api_key(monkeypatch):
    """4. Missing or empty Gemini API key returns None safely without raising exceptions."""
    monkeypatch.setattr(settings, "gemini_api_key", "")
    result = extract_request_intelligence("Primary health centre needs urgent water supply.")
    assert result is None

def test_gemini_placeholder_api_key(monkeypatch):
    """4b. Placeholder Gemini API key returns None safely."""
    monkeypatch.setattr(settings, "gemini_api_key", "your_gemini_api_key_here")
    result = extract_request_intelligence("Primary health centre needs urgent water supply.")
    assert result is None

def test_gemini_valid_structured_response(monkeypatch):
    """1. Valid structured Gemini response parses into GeminiExtractionResult."""
    monkeypatch.setattr(settings, "gemini_api_key", "mocked_valid_key")

    mock_json_response = """{
        "language": "English",
        "category": "Water",
        "problem_summary": "Primary health centre has a non-functional borewell and lacks clean drinking water.",
        "severity": "HIGH",
        "affected_group": "Patients and healthcare workers",
        "location_hint": "Ward 4"
    }"""

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_json_response
    mock_client.models.generate_content.return_value = mock_response

    with patch("backend.gemini_service.genai.Client", return_value=mock_client):
        result = extract_request_intelligence(
            citizen_text="Primary health centre lacks clean drinking water facility and borewell is non-functional.",
            state="Maharashtra",
            district="Dharashiv",
            locality="Ward 4",
            user_category="Water",
        )

    assert result is not None
    assert isinstance(result, GeminiExtractionResult)
    assert result.language == "English"
    assert result.category == "Water"
    assert result.severity == "HIGH"
    assert "borewell" in result.problem_summary
    assert result.affected_group == "Patients and healthcare workers"
    assert result.location_hint == "Ward 4"

def test_gemini_invalid_json_response(monkeypatch):
    """2. Invalid/corrupted JSON returned from Gemini gracefully returns None."""
    monkeypatch.setattr(settings, "gemini_api_key", "mocked_valid_key")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "NOT_A_VALID_JSON_STRING"
    mock_client.models.generate_content.return_value = mock_response

    with patch("backend.gemini_service.genai.Client", return_value=mock_client):
        result = extract_request_intelligence("Need road repair.")

    assert result is None

def test_gemini_api_exception(monkeypatch):
    """3. Gemini network or API exception gracefully returns None without throwing."""
    monkeypatch.setattr(settings, "gemini_api_key", "mocked_valid_key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("Gemini API Rate Limit Exceeded")

    with patch("backend.gemini_service.genai.Client", return_value=mock_client):
        result = extract_request_intelligence("Need road repair.")

    assert result is None

def test_gemini_category_validation():
    """8. Pydantic schema enforces valid category values."""
    valid_data = {
        "language": "Hindi",
        "category": "Healthcare",
        "problem_summary": "PHC clinic lacks basic antibiotics.",
        "severity": "MEDIUM",
        "affected_group": "Local villagers",
        "location_hint": "Ambedkar Nagar",
    }
    result = GeminiExtractionResult(**valid_data)
    assert result.category == "Healthcare"

    with pytest.raises(Exception):
        GeminiExtractionResult(**{**valid_data, "category": "InvalidNonExistentCategory"})

def test_gemini_severity_validation():
    """9. Pydantic schema enforces valid severity values (LOW, MEDIUM, HIGH)."""
    valid_data = {
        "language": "Marathi",
        "category": "Roads",
        "problem_summary": "Bridge washed away during heavy rainfall.",
        "severity": "HIGH",
        "affected_group": "School children and daily commuters",
        "location_hint": "Khed Bridge",
    }
    result = GeminiExtractionResult(**valid_data)
    assert result.severity == "HIGH"

    with pytest.raises(Exception):
        GeminiExtractionResult(**{**valid_data, "severity": "CRITICAL_INVALID"})
