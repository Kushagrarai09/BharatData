import httpx
from app.core.config import settings

MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

async def fetch_datagov(resource_id: str, limit: int = 100, filters: list[str] | None = None):
    if not settings.data_gov_in_api_key:
        raise ValueError("DATA_GOV_IN_API_KEY is missing. Generate a key from your data.gov.in account.")
    url = f"{settings.data_gov_in_base_url.rstrip('/')}/{resource_id}"
    params = {"api-key": settings.data_gov_in_api_key, "format": "json", "limit": limit, "offset": 0}
    if filters:
        for index, filter_value in enumerate(filters):
            if "=" not in filter_value:
                raise ValueError(f"Invalid filter '{filter_value}'. Expected field=value.")
            field, value = filter_value.split("=", 1)
            params[f"filters[{field}]"] = value
    all_records = []
    async with httpx.AsyncClient(timeout=45, headers={"User-Agent": "BharatData/1.0 (open-data research platform)"}) as client:
        while len(all_records) < limit:
            params["limit"] = min(1000, limit - len(all_records))
            response = await client.get(url, params=params)
            response.raise_for_status()
            body = response.json()
            batch = body.get("records", [])
            if not isinstance(batch, list) or not batch:
                break
            all_records.extend(batch)
            params["offset"] = int(params["offset"]) + len(batch)
            if len(batch) < params["limit"]:
                break
    return all_records
