import hashlib, json, re
from datetime import datetime
from dateutil import parser

def clean_text(value):
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None

def normalize_date(value):
    if not value:
        return None
    try:
        return parser.parse(str(value), dayfirst=True).date().isoformat()
    except (ValueError, TypeError, OverflowError):
        return None

def record_fingerprint(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def normalize_record(item: dict) -> dict:
    cleaned = {str(k).strip().lower(): clean_text(v) for k, v in item.items()}
    title = (cleaned.get("title") or cleaned.get("commodity") or cleaned.get("name")
             or cleaned.get("dataset_title") or "Untitled government record")
    date = (cleaned.get("arrival_date") or cleaned.get("date")
            or cleaned.get("published_date") or cleaned.get("updated_date"))
    return {
        "title": title[:500],
        "category": cleaned.get("category") or cleaned.get("sector") or "Government Open Data",
        "record_date": normalize_date(date),
        "payload": item,
        "source_url": cleaned.get("source_url") or cleaned.get("url"),
    }
