"""Dataset-aware normalization while preserving the original source payload."""
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any
from dateutil import parser

def clean_text(value: Any) -> str | None:
    if value is None: return None
    text=re.sub(r"\\s+"," ",str(value)).strip()
    return text or None

def normalize_date(value: Any) -> str | None:
    if not value: return None
    try: return parser.parse(str(value),dayfirst=True,fuzzy=False).date().isoformat()
    except (ValueError,TypeError,OverflowError): return None

def normalize_amount(value: Any) -> str | None:
    if value is None: return None
    raw=str(value).replace(",","").replace("₹","").replace("Rs.","").replace("Rs","").strip()
    raw=re.sub(r"[^0-9.\\-]","",raw)
    if not raw: return None
    try: return str(Decimal(raw).quantize(Decimal("0.01")))
    except (InvalidOperation,ValueError): return None

def record_fingerprint(payload: dict) -> str:
    canonical=json.dumps(payload,sort_keys=True,ensure_ascii=False,default=str,separators=(",",":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def mandi_business_key(item: dict) -> str:
    """Stable identity for a mandi price row; excludes mutable price values."""
    fields=(item.get("state",""),item.get("district",""),item.get("market",""),
      item.get("commodity",""),item.get("variety",""),item.get("grade",""),
      normalize_date(item.get("arrival_date") or item.get("date")) or "")
    canonical="|".join(clean_text(v) or "" for v in fields).casefold()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def normalize_mandi_record(item: dict) -> dict:
    get=lambda *names: next((item.get(name) for name in names if item.get(name) not in (None,"")),None)
    commodity=clean_text(get("commodity","Commodity","COMMODITY"))
    market=clean_text(get("market","Market","MARKET"))
    state=clean_text(get("state","State","STATE"))
    district=clean_text(get("district","District","DISTRICT"))
    variety=clean_text(get("variety","Variety","VARIETY"))
    grade=clean_text(get("grade","Grade","GRADE"))
    arrival_date=normalize_date(get("arrival_date","Arrival_Date","date"))
    return {"title":commodity or market or "Mandi price record","category":"Agriculture / Mandi Prices",
      "record_date":arrival_date,"payload":{**item,"_bharatdata":{"dataset":"mandi_prices",
      "business_key":mandi_business_key(item),"state":state,"district":district,"market":market,
      "commodity":commodity,"variety":variety,"grade":grade,"arrival_date":arrival_date,
      "min_price":normalize_amount(get("min_price","Min Price")),
      "max_price":normalize_amount(get("max_price","Max Price")),
      "modal_price":normalize_amount(get("modal_price","Modal Price"))}},
      "source_url":clean_text(get("source_url","url"))}

def normalize_generic_record(item: dict) -> dict:
    cleaned={str(k).strip().lower():clean_text(v) for k,v in item.items()}
    title=cleaned.get("title") or cleaned.get("commodity") or cleaned.get("name") or cleaned.get("dataset_title") or "Untitled government record"
    record_date=cleaned.get("arrival_date") or cleaned.get("date") or cleaned.get("published_date") or cleaned.get("updated_date")
    return {"title":title[:500],"category":cleaned.get("category") or cleaned.get("sector") or "Government Open Data",
      "record_date":normalize_date(record_date),"payload":item,
      "source_url":cleaned.get("source_url") or cleaned.get("url")}

def normalize_record(item: dict, dataset: str | None = None) -> dict:
    dataset_name=(dataset or "").lower()
    if dataset_name in {"mandi","mandi_prices","9ef84268-d588-465a-a308-a864a43d0070","agriculture_mandi"}:
        return normalize_mandi_record(item)
    return normalize_generic_record(item)
