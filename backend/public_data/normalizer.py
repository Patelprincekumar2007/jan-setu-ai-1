from typing import Optional, Any
import re

# Known State/UT standard title mappings
STATE_NAME_MAPPINGS = {
    "ANDAMAN AND NICOBAR ISLANDS": "Andaman and Nicobar Islands",
    "ANDHRA PRADESH": "Andhra Pradesh",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "ASSAM": "Assam",
    "BIHAR": "Bihar",
    "CHANDIGARH": "Chandigarh",
    "CHHATTISGARH": "Chhattisgarh",
    "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "Dadra and Nagar Haveli and Daman and Diu",
    "DELHI": "Delhi",
    "GOA": "Goa",
    "GUJARAT": "Gujarat",
    "HARYANA": "Haryana",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "JAMMU AND KASHMIR": "Jammu and Kashmir",
    "JHARKHAND": "Jharkhand",
    "KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "LADAKH": "Ladakh",
    "LAKSHADWEEP": "Lakshadweep",
    "MADHYA PRADESH": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra",
    "MANIPUR": "Manipur",
    "MEGHALAYA": "Meghalaya",
    "MIZORAM": "Mizoram",
    "NAGALAND": "Nagaland",
    "ODISHA": "Odisha",
    "PUDUCHERRY": "Puducherry",
    "PUNJAB": "Punjab",
    "RAJASTHAN": "Rajasthan",
    "SIKKIM": "Sikkim",
    "TAMIL NADU": "Tamil Nadu",
    "TELANGANA": "Telangana",
    "TRIPURA": "Tripura",
    "UTTAR PRADESH": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "WEST BENGAL": "West Bengal",
}

VALID_CATEGORIES = {"Water", "Roads", "Healthcare", "Sanitation", "Other"}

def normalize_geographic_name(name: Optional[str]) -> Optional[str]:
    """
    Deterministically cleans and standardises geographic string (State, District, Locality).
    Strips leading/trailing whitespace, collapses internal whitespace, and applies standard casing.
    """
    if name is None:
        return None
    cleaned = str(name).strip()
    if not cleaned or cleaned.upper() in {"NULL", "NONE", "NA", "N/A", "-"}:
        return None
    
    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned)
    
    # Check known state mapping
    upper = cleaned.upper()
    if upper in STATE_NAME_MAPPINGS:
        return STATE_NAME_MAPPINGS[upper]
    
    # Otherwise standard title case
    return cleaned.title()

def normalize_numeric_metric(val: Any) -> Optional[float]:
    """
    Deterministically parses numeric metric value.
    Returns float or None if missing/unavailable. Does NOT invent zeroes or averages.
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    
    cleaned = str(val).strip().replace(",", "")
    if not cleaned or cleaned.upper() in {"NULL", "NONE", "NA", "N/A", "-", "N.A."}:
        return None
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def normalize_category(category_input: Optional[str]) -> str:
    """
    Normalizes sector category string to one of: Water, Roads, Healthcare, Sanitation, Other.
    Defaults to 'Other' if unknown or ambiguous.
    """
    if not category_input:
        return "Other"
    
    cleaned = str(category_input).strip().title()
    if cleaned in VALID_CATEGORIES:
        return cleaned
    
    # Sector mapping keywords
    lower = category_input.lower()
    if any(w in lower for w in ["water", "drinking", "jjm", "jal", "pipe", "borewell"]):
        return "Water"
    if any(w in lower for w in ["road", "highway", "pmgsy", "paved", "connectivity", "bridge"]):
        return "Roads"
    if any(w in lower for w in ["health", "hospital", "phc", "chc", "nhm", "clinic", "medical"]):
        return "Healthcare"
    if any(w in lower for w in ["sanitation", "toilet", "drain", "drainage", "sbm", "waste", "sewer"]):
        return "Sanitation"
    
    return "Other"

def normalize_integer(val: Any) -> Optional[int]:
    """Parses integer value (e.g. year, count) or returns None if missing."""
    if val is None:
        return None
    if isinstance(val, int):
        return val
    cleaned = str(val).strip().replace(",", "")
    if not cleaned or cleaned.upper() in {"NULL", "NONE", "NA", "N/A", "-"}:
        return None
    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return None
