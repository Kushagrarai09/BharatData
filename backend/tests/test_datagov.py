import httpx
import pytest
import respx
from app.services.datagov import fetch_datagov
from app.core.config import settings
RESOURCE="9ef84268-d588-465a-a308-a864a43d0070"

@pytest.mark.asyncio
@respx.mock
async def test_fetch_datagov_paginates(monkeypatch):
    monkeypatch.setattr(settings,"data_gov_in_api_key","test-key")
    route=respx.get(f"{settings.data_gov_in_base_url}/{RESOURCE}")
    route.side_effect=[httpx.Response(200,json={"records":[{"commodity":"Onion"}]}),httpx.Response(200,json={"records":[{"commodity":"Potato"}]})]
    rows=await fetch_datagov(RESOURCE,limit=2,max_retries=0)
    assert [r["commodity"] for r in rows]==["Onion","Potato"]
    assert route.call_count==2

@pytest.mark.asyncio
@respx.mock
async def test_fetch_datagov_retries_429(monkeypatch):
    monkeypatch.setattr(settings,"data_gov_in_api_key","test-key")
    route=respx.get(f"{settings.data_gov_in_base_url}/{RESOURCE}")
    route.side_effect=[httpx.Response(429,headers={"Retry-After":"0"}),httpx.Response(200,json={"records":[{"commodity":"Onion"}]})]
    rows=await fetch_datagov(RESOURCE,limit=10,max_retries=1)
    assert len(rows)==1 and route.call_count==2

@pytest.mark.asyncio
async def test_fetch_datagov_requires_key(monkeypatch):
    monkeypatch.setattr(settings,"data_gov_in_api_key","")
    with pytest.raises(ValueError,match="DATA_GOV_IN_API_KEY"):
        await fetch_datagov(RESOURCE,limit=1)
