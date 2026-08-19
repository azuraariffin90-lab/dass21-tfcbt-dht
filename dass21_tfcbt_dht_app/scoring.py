"""Fungsi pemarkahan tulen supaya logik boleh diuji tanpa Streamlit."""

from __future__ import annotations

from typing import Any

from survey_config import DASS_ITEMS, DASS_THRESHOLDS, SEVERITY_ORDER, TRAUMA_ITEMS


def dass_category(scale: str, score: int) -> str:
    if scale not in DASS_THRESHOLDS:
        raise ValueError(f"Subskala tidak dikenali: {scale}")
    if not 0 <= score <= 42:
        raise ValueError("Skor subskala DASS-21 mesti antara 0 hingga 42.")
    for minimum, maximum, label in DASS_THRESHOLDS[scale]:
        if minimum <= score <= maximum:
            return label
    raise ValueError(f"Skor {score} tidak dapat dikategorikan.")


def calculate_dass(answers: dict[int, int]) -> dict[str, Any]:
    expected = {item["id"] for item in DASS_ITEMS}
    if set(answers) != expected:
        missing = sorted(expected - set(answers))
        extra = sorted(set(answers) - expected)
        raise ValueError(f"Jawapan DASS tidak lengkap. Hilang={missing}; tambahan={extra}")
    if any(value not in (0, 1, 2, 3) for value in answers.values()):
        raise ValueError("Setiap jawapan DASS mestilah 0, 1, 2 atau 3.")

    raw = {"Depression": 0, "Anxiety": 0, "Stress": 0}
    for item in DASS_ITEMS:
        raw[item["scale"]] += answers[item["id"]]

    scaled = {scale: value * 2 for scale, value in raw.items()}
    levels = {scale: dass_category(scale, score) for scale, score in scaled.items()}
    highest = max(levels.values(), key=SEVERITY_ORDER.index)
    return {"raw": raw, "scores": scaled, "levels": levels, "highest_level": highest}


def calculate_trauma(answers: dict[str, int | None]) -> dict[str, Any]:
    by_id = {item["id"]: item for item in TRAUMA_ITEMS}
    unknown = set(answers) - set(by_id)
    if unknown:
        raise ValueError(f"Item trauma tidak dikenali: {sorted(unknown)}")
    for value in answers.values():
        if value is not None and value not in (0, 1, 2, 3):
            raise ValueError("Jawapan trauma mestilah kosong, 0, 1, 2 atau 3.")

    answered = {item_id: value for item_id, value in answers.items() if value is not None}
    positives = {item_id: value for item_id, value in answered.items() if value >= 2}
    urgent = [
        item_id
        for item_id, value in answered.items()
        if value >= 1 and by_id[item_id]["safety_critical"]
    ]
    dharuriyyat_positives = [
        item_id
        for item_id, value in positives.items()
        if by_id[item_id]["need_level"] == "Dharuriyyat"
    ]
    domains = sorted({by_id[item_id]["domain"] for item_id in positives})

    domain_max: dict[str, int | None] = {}
    for domain in ("Agama", "Nyawa", "Akal", "Keturunan", "Harta"):
        values = [
            value
            for item_id, value in answered.items()
            if by_id[item_id]["domain"] == domain
        ]
        domain_max[domain] = max(values) if values else None

    return {
        "answered_count": len(answered),
        "positive_count": len(positives),
        "positive_items": sorted(positives),
        "dharuriyyat_positive_count": len(dharuriyyat_positives),
        "immediate_safety_flag": bool(urgent),
        "urgent_items": sorted(urgent),
        "domains_flagged": domains,
        "domain_max": domain_max,
    }


def determine_review_priority(dass_result: dict[str, Any], trauma_result: dict[str, Any]) -> str:
    levels = set(dass_result["levels"].values())
    if trauma_result["immediate_safety_flag"]:
        return "Segera"
    if "Sangat Teruk" in levels or trauma_result["dharuriyyat_positive_count"] > 0:
        return "Tinggi"
    if "Teruk" in levels or trauma_result["positive_count"] > 0:
        return "Sederhana"
    return "Rutin"

