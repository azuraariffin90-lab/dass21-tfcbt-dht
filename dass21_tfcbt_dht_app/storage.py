"""Lapisan storan Excel dengan kunci fail dan simpanan atomik."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from filelock import FileLock
from openpyxl import load_workbook


SUBMISSION_SHEET = "Submissions_Raw"
TRAUMA_SHEET = "Trauma_Long"
AUDIT_SHEET = "Audit_Log"


def _lock_path(database_path: Path) -> str:
    return str(database_path.with_suffix(database_path.suffix + ".lock"))


def initialize_database(database_path: Path, template_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        return
    if not template_path.exists():
        raise FileNotFoundError(
            f"Templat pangkalan data tidak ditemui: {template_path}. "
            "Pastikan database_template.xlsx berada bersama app.py."
        )
    with FileLock(_lock_path(database_path), timeout=20):
        if not database_path.exists():
            shutil.copy2(template_path, database_path)


def _headers(worksheet) -> list[str]:
    return [str(cell.value) if cell.value is not None else "" for cell in worksheet[1]]


def _append_mapping(worksheet, record: dict[str, Any]) -> None:
    headers = _headers(worksheet)
    missing = sorted(set(record) - set(headers))
    if missing:
        raise ValueError(f"Lajur tidak wujud dalam {worksheet.title}: {missing}")
    worksheet.append([record.get(header) for header in headers])


def append_submission(
    database_path: Path,
    submission: dict[str, Any],
    trauma_rows: Iterable[dict[str, Any]],
) -> None:
    """Tambah satu submission dan butiran trauma sebagai satu transaksi fail."""

    with FileLock(_lock_path(database_path), timeout=30):
        workbook = load_workbook(database_path)
        temp_path: Path | None = None
        try:
            _append_mapping(workbook[SUBMISSION_SHEET], submission)
            for trauma_row in trauma_rows:
                _append_mapping(workbook[TRAUMA_SHEET], trauma_row)

            student_hash = hashlib.sha256(
                str(submission["student_id"]).encode("utf-8")
            ).hexdigest()[:12]
            audit = {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "event": "SUBMISSION_CREATED",
                "submission_id": submission["submission_id"],
                "student_id_hash": student_hash,
                "details": "Rekod baharu disimpan oleh borang pelajar.",
            }
            _append_mapping(workbook[AUDIT_SHEET], audit)

            with tempfile.NamedTemporaryFile(
                prefix="dass_dht_", suffix=".xlsx", dir=database_path.parent, delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
            workbook.save(temp_path)
            os.replace(temp_path, database_path)
        finally:
            workbook.close()
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)


def read_database(database_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not database_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    with FileLock(_lock_path(database_path), timeout=20):
        submissions = pd.read_excel(
            database_path, sheet_name=SUBMISSION_SHEET, dtype={"student_id": "string"}
        )
        trauma = pd.read_excel(
            database_path, sheet_name=TRAUMA_SHEET, dtype={"student_id": "string"}
        )
    return submissions, trauma


def read_database_bytes(database_path: Path) -> bytes:
    with FileLock(_lock_path(database_path), timeout=20):
        return database_path.read_bytes()

