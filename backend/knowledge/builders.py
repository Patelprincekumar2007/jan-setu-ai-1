from typing import Union, Dict, Any
from backend.public_data.models import PublicDataRecord, Dataset
from backend.public_data.schemas import PublicDataRecordCreate, DatasetCreate
from backend.knowledge.schemas import KnowledgeEvidenceCreate


def build_evidence_content(
    state: str,
    district: str,
    locality: Union[str, None],
    metric_name: str,
    metric_value: Union[float, None],
    unit: Union[str, None],
    dataset_title: str,
    year: Union[int, None] = None,
    notes: Union[str, None] = None,
) -> str:
    """
    Constructs deterministic, strictly factual human-readable evidence text from stored data.
    No LLM, no adjectives, no synthetic assumptions.
    """
    loc_part = f"Locality {locality}, " if locality else ""
    geo_part = f"{loc_part}District {district}, {state}"
    
    val_part = ""
    if metric_value is not None:
        unit_str = f" {unit}" if unit and unit != "%" else (unit or "")
        val_part = f" of {metric_value}{unit_str}"
    
    time_part = f" for {year}" if year else ""
    
    content = f"{geo_part} recorded {metric_name.lower()}{val_part} according to the {dataset_title}{time_part}."
    
    if notes:
        content += f" Baseline details: {notes}."
        
    return content


def build_knowledge_evidence(
    record: Union[PublicDataRecord, PublicDataRecordCreate],
    dataset: Union[Dataset, DatasetCreate, Dict[str, Any]],
) -> KnowledgeEvidenceCreate:
    """
    Transforms a verified PublicDataRecord and associated Dataset metadata into a validated KnowledgeEvidence object.
    Preserves complete provenance and builds deterministic grounding text.
    """
    # Extract dataset attributes
    if isinstance(dataset, dict):
        dataset_id = dataset.get("dataset_id", "")
        title = dataset.get("title", "")
        source_name = dataset.get("source_name", "")
        source_url = dataset.get("source_url")
        publisher = dataset.get("publisher")
        license_str = dataset.get("license")
        last_updated = dataset.get("last_updated")
    else:
        dataset_id = dataset.dataset_id
        title = dataset.title
        source_name = dataset.source_name
        source_url = dataset.source_url
        publisher = dataset.publisher
        license_str = dataset.license
        last_updated = dataset.last_updated

    # Deterministic Evidence ID
    evidence_id = f"EVID-{record.dataset_id}-{record.source_reference}"

    # Factual Evidence Title
    title_str = f"{record.district} ({record.state}) - {record.metric_name}"

    # Factual Evidence Content
    content = build_evidence_content(
        state=record.state,
        district=record.district,
        locality=record.locality,
        metric_name=record.metric_name,
        metric_value=record.metric_value,
        unit=record.unit,
        dataset_title=title,
        year=record.year,
        notes=record.notes,
    )

    return KnowledgeEvidenceCreate(
        evidence_id=evidence_id,
        dataset_id=dataset_id,
        record_id=record.record_id,
        title=title_str,
        content=content,
        state=record.state,
        district=record.district,
        locality=record.locality,
        category=record.category,  # type: ignore
        metric_name=record.metric_name,
        metric_value=record.metric_value,
        unit=record.unit,
        year=record.year,
        period=record.period,
        geographic_level=record.geographic_level,
        source_name=source_name,
        source_url=source_url,
        source_reference=record.source_reference,
        publisher=publisher,
        license=license_str,
        last_updated=last_updated,
        notes=record.notes,
    )
