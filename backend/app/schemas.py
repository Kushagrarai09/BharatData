from pydantic import BaseModel, Field
from typing import Any

class DataGovIngestRequest(BaseModel):
    resource_id: str = Field(min_length=10, max_length=100)
    limit: int = Field(default=100, ge=1, le=1000)
    filters: list[str] = []

class ApifyIngestRequest(BaseModel):
    resource_id: str = Field(min_length=10, max_length=100)
    max_results: int = Field(default=100, ge=1, le=100000)
    filters: list[str] = []

class RecordOut(BaseModel):
    id: int
    title: str
    category: str | None
    record_date: str | None
    payload: dict[str, Any]
    source_url: str | None
    class Config:
        from_attributes = True
