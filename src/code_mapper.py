"""
code_mapper.py
---------------
Maps text values (e.g., "Chief Engineer", "Bulk Carrier", "Passport") to
their numeric lookup codes — all done LOCALLY with no API cost.

Uses two strategies:
  1. Exact / substring match (fastest, most reliable)
  2. Fuzzy match with difflib (handles typos, abbreviations)

Returns:
  (code, matched_text, confidence)
  - code: int or None if no good match
  - matched_text: the lookup table entry that was matched
  - confidence: 0.0-1.0 score; >= 0.7 is considered a match
"""

import re
from difflib import SequenceMatcher

from lookups import (
    RANK_LOOKUP,
    STATUS_LOOKUP,
    CITIZENSHIP_LOOKUP,
    SALARY_CURRENCY_LOOKUP,
    SALARY_TYPE_LOOKUP,
    NOTICE_TYPE_LOOKUP,
    VESSEL_TYPE_LOOKUP,
    VESSEL_PUMP_LOOKUP,
    VESSEL_GEAR_LOOKUP,
    ENGINE_TYPE_LOOKUP,
    DP_TYPE_LOOKUP,
    DP_MANUFACTURER_LOOKUP,
    EXP_RANK_LOOKUP,
    OFF_REASON_LOOKUP,
    CERT_CATEGORIES,
)


CONFIDENCE_THRESHOLD = 0.7


def _normalize(s: str) -> str:
    """Lowercase, strip, collapse whitespace, remove common noise."""
    if not s:
        return ""
    s = str(s).lower().strip()
    # Remove parenthesized abbreviations: "FITTER (Fitter)" -> "fitter fitter"
    s = re.sub(r"[()]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _similarity(a: str, b: str) -> float:
    """Sequence similarity 0.0-1.0."""
    return SequenceMatcher(None, a, b).ratio()


def map_text_to_code(text: str, lookup: dict) -> tuple:
    """
    Given a text value and a lookup dict {code: text}, find the best matching code.

    Returns (code, matched_label, confidence).
    code is None if no match passes the threshold.
    """
    if not text or not str(text).strip():
        return (None, None, 0.0)

    query = _normalize(text)
    best_code = None
    best_label = None
    best_score = 0.0

    for code, label in lookup.items():
        label_norm = _normalize(label)

        # --- Strategy 1: exact match ---
        if query == label_norm:
            return (code, label, 1.0)

        # --- Strategy 2: token-level match ---
        # Extract abbreviations like "CENG" from "CENG (Chief Engineer)"
        tokens = label_norm.split()
        if query in tokens:
            score = 0.95
        elif query in label_norm:
            score = 0.85
        elif any(tok == query for tok in tokens):
            score = 0.9
        else:
            # --- Strategy 3: fuzzy similarity ---
            score = _similarity(query, label_norm)
            # Boost score if first words match
            if tokens and query.split() and tokens[0] == query.split()[0]:
                score = min(1.0, score + 0.1)

        if score > best_score:
            best_score = score
            best_code = code
            best_label = label

    if best_score >= CONFIDENCE_THRESHOLD:
        return (best_code, best_label, best_score)
    else:
        return (None, best_label, best_score)


def map_certificate(cert_text: str, category: str = None) -> tuple:
    """
    Special handling for certificates - they're grouped by category.
    Returns (cert_id, matched_label, category, confidence).
    """
    if not cert_text:
        return (None, None, None, 0.0)

    if category and category in CERT_CATEGORIES:
        # Try within the specified category first
        code, label, score = map_text_to_code(cert_text, CERT_CATEGORIES[category])
        if code is not None:
            return (code, label, category, score)

    # If no category given or no match, search ALL categories and pick best
    best = (None, None, None, 0.0)
    for cat_name, lookup in CERT_CATEGORIES.items():
        code, label, score = map_text_to_code(cert_text, lookup)
        if score > best[3]:
            best = (code, label, cat_name, score)
    return best


# ============================================================
# High-level mapping for a full extracted JSON from Claude
# ============================================================

def map_personal_info(data: dict) -> dict:
    """Add mapped codes to personal info data."""
    mapped = dict(data)
    unmatched = []

    # status (text -> code)
    if data.get("status_text"):
        code, label, conf = map_text_to_code(data["status_text"], STATUS_LOOKUP)
        mapped["status"] = code
        mapped["_status_match"] = {"code": code, "label": label, "confidence": conf}
        if code is None:
            unmatched.append(("status", data["status_text"]))

    # citizen
    if data.get("citizen_text"):
        code, label, conf = map_text_to_code(data["citizen_text"], CITIZENSHIP_LOOKUP)
        mapped["citizen"] = code
        mapped["_citizen_match"] = {"code": code, "label": label, "confidence": conf}
        if code is None:
            unmatched.append(("citizen", data["citizen_text"]))

    # salary_currency
    if data.get("salary_currency_text"):
        code, label, conf = map_text_to_code(data["salary_currency_text"], SALARY_CURRENCY_LOOKUP)
        mapped["salary_currency"] = code
        mapped["_salary_currency_match"] = {"code": code, "label": label, "confidence": conf}

    # salary_type
    if data.get("salary_type_text"):
        code, label, conf = map_text_to_code(data["salary_type_text"], SALARY_TYPE_LOOKUP)
        mapped["salary_type"] = code
        mapped["_salary_type_match"] = {"code": code, "label": label, "confidence": conf}

    # notice_type
    if data.get("notice_type_text"):
        code, label, conf = map_text_to_code(data["notice_type_text"], NOTICE_TYPE_LOOKUP)
        mapped["notice_type"] = code
        mapped["_notice_type_match"] = {"code": code, "label": label, "confidence": conf}

    # rank (current)
    if data.get("rank_text"):
        code, label, conf = map_text_to_code(data["rank_text"], RANK_LOOKUP)
        mapped["rank"] = code
        mapped["_rank_match"] = {"code": code, "label": label, "confidence": conf}
        if code is None:
            unmatched.append(("rank", data["rank_text"]))

    mapped["_unmatched"] = unmatched
    return mapped


def map_certificate_row(cert: dict) -> dict:
    """Add mapped codes to a single certificate."""
    mapped = dict(cert)
    if cert.get("name_text") or cert.get("type_text"):
        # 'type_text' is the category (Travel Documents, Training, etc.)
        # 'name_text' is the specific cert name (Passport, Basic Safety Training, etc.)
        cert_id, label, category, conf = map_certificate(
            cert.get("name_text") or cert.get("type_text") or "",
            cert.get("type_text"),
        )
        mapped["cert_id"] = cert_id
        mapped["type"] = category or cert.get("type_text")
        mapped["_cert_match"] = {"code": cert_id, "label": label, "category": category, "confidence": conf}
    return mapped


def map_experience_row(exp: dict) -> dict:
    """Add mapped codes to a single experience row."""
    mapped = dict(exp)

    for field, lookup in [
        ("type", VESSEL_TYPE_LOOKUP),
        ("pumping_system", VESSEL_PUMP_LOOKUP),
        ("cargo_handling_gear", VESSEL_GEAR_LOOKUP),
        ("engine_type", ENGINE_TYPE_LOOKUP),
        ("dp_type", DP_TYPE_LOOKUP),
        ("dp_manufacturer", DP_MANUFACTURER_LOOKUP),
        ("rank", EXP_RANK_LOOKUP),
        ("off_reason", OFF_REASON_LOOKUP),
    ]:
        text_key = f"{field}_text"
        if exp.get(text_key):
            code, label, conf = map_text_to_code(exp[text_key], lookup)
            mapped[field] = code
            mapped[f"_{field}_match"] = {"code": code, "label": label, "confidence": conf}

    return mapped
