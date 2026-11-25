# BharatData — Government & Open Data Intelligence Platform

BharatData is a modular data-ingestion platform for Indian government open datasets and public documents. It combines the official data.gov.in API, an optional Apify actor integration, PDF extraction, normalization, deduplication, PostgreSQL persistence, a FastAPI backend and a React dashboard.

## What works in this starter
- Direct data.gov.in resource API client with pagination and API-key configuration.
- Optional Apify actor integration (`themineworks/india-data-gov-scraper`).
- Mandi price ingestion preset for resource `9ef84268-d588-465a-a308-a864a43d0070`.
- PostgreSQL models for sources, ingestion jobs, records, documents and data-quality checks.
- Idempotent record upserts using a SHA-256 fingerprint.
- PDF text/table extraction endpoint using pdfplumber.
- Searchable records, job/source/metrics endpoints.
- React dashboard with ingestion controls, metrics and records.
- Docker Compose for API, PostgreSQL, Redis and frontend.
- Unit tests for normalization and deduplication helpers.

## Integration notes
1. Create an API key from your data.gov.in account and set `DATA_GOV_IN_API_KEY`.
2. Apify is optional. Set `APIFY_TOKEN` to enable the actor integration.
3. Use direct official API access as the preferred provider; Apify is an optional provider/fallback. The actor may be subject to rate limits and charges.
4. Do not commit `.env` or API tokens.
5. Respect publisher terms, rate limits and access policies. Do not bypass authentication or access controls.

## Quick start (Docker)
```bash
cp .env.example .env
# Edit .env and add DATA_GOV_IN_API_KEY.
docker compose up --build
```
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Health: http://localhost:8000/health

## Example ingestion requests
```bash
curl -X POST http://localhost:8000/api/ingestion/datagov \
  -H "Content-Type: application/json" \
  -d '{"resource_id":"9ef84268-d588-465a-a308-a864a43d0070","limit":100,"filters":[]}'
```

```bash
curl -X POST http://localhost:8000/api/ingestion/apify \
  -H "Content-Type: application/json" \
  -d '{"resource_id":"9ef84268-d588-465a-a308-a864a43d0070","max_results":100,"filters":[]}'
```

## API overview
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/metrics` | Platform metrics |
| GET | `/api/sources` | Registered data sources |
| GET | `/api/records` | Search stored records |
| GET | `/api/jobs` | Ingestion job history |
| POST | `/api/ingestion/datagov` | Fetch official data.gov.in resource |
| POST | `/api/ingestion/apify` | Run Apify actor and import results |
| POST | `/api/documents/extract` | Extract text/tables from PDF |

## Current scope and next milestones
This is an MVP foundation, not yet a production deployment. Add Scrapy/Playwright source adapters, OCR for scanned PDFs, Celery workers, Redis-backed queues, scheduled jobs, richer quality monitoring, history snapshots and authentication before production use.
