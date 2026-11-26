"""Official data.gov.in resource API client with bounded retries and pagination."""
import asyncio
import random
from typing import Any
import httpx
from app.core.config import settings

MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}

class DataGovAPIError(RuntimeError):
    """Raised when the Open Government Data API cannot serve a valid response."""

def _retry_delay(attempt: int, retry_after: str | None = None) -> float:
    if retry_after:
        try: return min(60.0, max(0.0, float(retry_after)))
        except ValueError: pass
    return min(30.0, (2 ** attempt) + random.uniform(0, 0.5))

async def fetch_datagov(resource_id: str, limit: int = 100, filters: list[str] | None = None,
                        *, client: httpx.AsyncClient | None = None, max_retries: int = 4) -> list[dict[str, Any]]:
    if not settings.data_gov_in_api_key:
        raise ValueError("DATA_GOV_IN_API_KEY is missing. Configure it in your environment.")
    if not resource_id or not 10 <= len(resource_id) <= 100:
        raise ValueError("A valid data.gov.in resource UUID is required.")
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000.")
    url = f"{settings.data_gov_in_base_url.rstrip('/')}/{resource_id}"
    params: dict[str, Any] = {"api-key": settings.data_gov_in_api_key, "format": "json", "limit": min(limit,1000), "offset": 0}
    for filter_value in filters or []:
        if "=" not in filter_value: raise ValueError(f"Invalid filter {filter_value!r}; expected field=value.")
        field, value = filter_value.split("=",1)
        if not field.strip() or not value.strip(): raise ValueError(f"Invalid filter {filter_value!r}; field and value are required.")
        params[f"filters[{field.strip()}]"] = value.strip()
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=httpx.Timeout(45.0),
        headers={"User-Agent":"BharatData/0.2 (+https://github.com/Kushagrarai09/BharatData)"})
    records: list[dict[str,Any]]=[]
    try:
        while len(records)<limit:
            params["limit"]=min(1000,limit-len(records))
            response=None
            for attempt in range(max_retries+1):
                try:
                    response=await http.get(url,params=params)
                    if response.status_code in RETRYABLE_STATUS:
                        if attempt>=max_retries: response.raise_for_status()
                        await asyncio.sleep(_retry_delay(attempt,response.headers.get("Retry-After"))); continue
                    response.raise_for_status(); break
                except (httpx.TimeoutException,httpx.NetworkError):
                    if attempt>=max_retries: raise
                    await asyncio.sleep(_retry_delay(attempt))
            if response is None: raise DataGovAPIError("No response received from data.gov.in.")
            try: body=response.json()
            except ValueError as exc: raise DataGovAPIError("data.gov.in returned invalid JSON.") from exc
            if not isinstance(body,dict): raise DataGovAPIError("Unexpected API response: expected a JSON object.")
            batch=body.get("records",[])
            if not isinstance(batch,list): raise DataGovAPIError("Unexpected API response: 'records' is not a list.")
            if not batch: break
            if not all(isinstance(item,dict) for item in batch): raise DataGovAPIError("API returned non-object records.")
            records.extend(batch); params["offset"]=int(params["offset"])+len(batch)
            if len(batch)<params["limit"]: break
    finally:
        if owns_client: await http.aclose()
    return records[:limit]
