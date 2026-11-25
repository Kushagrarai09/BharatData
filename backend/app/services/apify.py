import httpx
from app.core.config import settings

async def fetch_apify_dataset(resource_id: str, max_results: int = 100, filters: list[str] | None = None):
    if not settings.apify_token: raise ValueError("APIFY_TOKEN is missing. Add your Apify API token to .env.")
    url = f"https://api.apify.com/v2/acts/{settings.apify_actor_id}/run-sync-get-dataset-items"
    payload = {"resourceId": resource_id, "maxResults": max_results, "filters": filters or []}
    if settings.data_gov_in_api_key: payload["apiKey"] = settings.data_gov_in_api_key
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(url, params={"token": settings.apify_token}, json=payload)
        if response.status_code == 429: raise RuntimeError("Apify/data.gov.in returned HTTP 429. Use direct data.gov.in API integration as fallback.")
        response.raise_for_status(); result = response.json()
        if isinstance(result, list): return result
        if isinstance(result, dict): return result.get("items", result.get("records", [result]))
        return []
