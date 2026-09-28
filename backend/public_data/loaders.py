import csv
import json
import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from pathlib import Path

from backend.public_data.schemas import DatasetCreate, PublicDataRecordCreate
from backend.public_data.normalizer import (
    normalize_geographic_name,
    normalize_numeric_metric,
    normalize_category,
    normalize_integer,
)


class BaseDatasetLoader(ABC):
    """Abstract interface for civic dataset loaders."""

    @abstractmethod
    def load_and_normalize(self) -> Tuple[DatasetCreate, List[PublicDataRecordCreate]]:
        """Reads raw source data and produces validated metadata and normalized records."""
        pass


class JJMWaterCoverageLoader(BaseDatasetLoader):
    """
    Deterministic loader for Jal Jeevan Mission District-level Water Coverage dataset.
    Raw source: data/raw/jjm_district_water_coverage_2024.csv
    Metadata source: data/raw/jjm_district_water_coverage_2024.meta.json
    """

    def __init__(
        self,
        raw_csv_path: Optional[str] = None,
        meta_json_path: Optional[str] = None,
        normalized_output_path: Optional[str] = None,
    ):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.raw_csv_path = raw_csv_path or str(base_dir / "data" / "raw" / "jjm_district_water_coverage_2024.csv")
        self.meta_json_path = meta_json_path or str(base_dir / "data" / "raw" / "jjm_district_water_coverage_2024.meta.json")
        self.normalized_output_json = normalized_output_path or str(base_dir / "data" / "normalized" / "jjm_water_coverage_normalized.json")
        self.normalized_output_csv = str(base_dir / "data" / "normalized" / "jjm_water_coverage_normalized.csv")

    def load_and_normalize(self) -> Tuple[DatasetCreate, List[PublicDataRecordCreate]]:
        if not os.path.exists(self.meta_json_path):
            raise FileNotFoundError(f"Metadata file not found at: {self.meta_json_path}")
        if not os.path.exists(self.raw_csv_path):
            raise FileNotFoundError(f"Raw CSV file not found at: {self.raw_csv_path}")

        # 1. Load verified metadata
        with open(self.meta_json_path, "r", encoding="utf-8") as f:
            meta_raw = json.load(f)

        dataset_id = meta_raw["dataset_id"]

        # 2. Read and parse raw CSV
        records: List[PublicDataRecordCreate] = []
        serial = 1

        with open(self.raw_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Column mapping and deterministic normalization
                state_raw = row.get("state_name")
                district_raw = row.get("district_name")
                coverage_raw = row.get("coverage_percentage")
                year_raw = row.get("report_year")
                source_row_id = row.get("source_row_id", f"OGD-JJM-ROW-{serial:03d}")
                total_hh_raw = row.get("total_rural_households")
                tap_conn_raw = row.get("tap_connections_provided")

                state_clean = normalize_geographic_name(state_raw)
                district_clean = normalize_geographic_name(district_raw)
                metric_val = normalize_numeric_metric(coverage_raw)
                year_clean = normalize_integer(year_raw)
                category_clean = normalize_category("Water")

                if not state_clean or not district_clean or metric_val is None:
                    continue

                notes = None
                if total_hh_raw and tap_conn_raw:
                    notes = f"Total Rural Households: {total_hh_raw}, Tap Connections Provided: {tap_conn_raw}"

                record_id = f"{dataset_id}-REC-{serial:04d}"

                record = PublicDataRecordCreate(
                    record_id=record_id,
                    dataset_id=dataset_id,
                    state=state_clean,
                    district=district_clean,
                    locality=None,  # District-level dataset does not contain locality
                    category=category_clean,
                    metric_name="Rural Tap Water Coverage",
                    metric_value=metric_val,
                    unit="%",
                    year=year_clean,
                    period=f"FY {year_clean}" if year_clean else None,
                    geographic_level="District",
                    source_reference=source_row_id,
                    notes=notes,
                )
                records.append(record)
                serial += 1

        # 3. Create Dataset metadata schema
        dataset_meta = DatasetCreate(
            dataset_id=dataset_id,
            title=meta_raw["title"],
            description=meta_raw.get("description"),
            source_name=meta_raw["source_name"],
            source_url=meta_raw.get("source_url"),
            publisher=meta_raw.get("publisher"),
            data_type=meta_raw["data_type"],
            geographic_scope=meta_raw["geographic_scope"],
            last_updated=meta_raw.get("last_updated"),
            license=meta_raw["license"],
            ingestion_status="INGESTED" if records else "NOT_INGESTED",
            record_count=len(records),
        )

        # 4. Save normalized representation to data/normalized/
        self._save_normalized_outputs(dataset_meta, records)

        return dataset_meta, records

    def _save_normalized_outputs(self, dataset_meta: DatasetCreate, records: List[PublicDataRecordCreate]) -> None:
        os.makedirs(os.path.dirname(self.normalized_output_json), exist_ok=True)

        # Save JSON
        json_data = {
            "dataset": dataset_meta.model_dump(),
            "record_count": len(records),
            "records": [r.model_dump() for r in records],
        }
        with open(self.normalized_output_json, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        # Save CSV
        if records:
            fieldnames = [
                "record_id",
                "dataset_id",
                "state",
                "district",
                "locality",
                "category",
                "metric_name",
                "metric_value",
                "unit",
                "year",
                "period",
                "geographic_level",
                "source_reference",
                "notes",
            ]
            with open(self.normalized_output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    writer.writerow(r.model_dump())
