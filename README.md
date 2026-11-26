# BharatData — Government & Open Data Intelligence Platform

BharatData collects public Indian government datasets and documents, normalizes records, detects repeated logical records and exposes the data through a REST API and dashboard.

## Implemented foundation
- Official data.gov.in resource API client with offset pagination, bounded retries, exponential backoff and Retry-After support.
- Mandi-specific field normalization, date/amount normalization and a stable record identity excluding mutable price fields.
- Repeat imports update the same logical record.
- Optional Apify adapter.
- Scrapy starter with robots.txt compliance, AutoThrottle, retries, cookies, CSS selectors, pagination and resumable JOBDIR runs.
- Basic PDF text/table extraction, FastAPI endpoints and React dashboard.
- Mocked API tests, SQLite persistence tests and GitHub Actions backend test workflow.

## Setup
1. Copy .env.example to .env.
2. Set DATA_GOV_IN_API_KEY to your personal data.gov.in API key.
3. Run docker compose up --build.
4. API docs: http://localhost:8000/docs; dashboard: http://localhost:5173.

## Import mandi prices
Resource UUID: 9ef84268-d588-465a-a308-a864a43d0070.

```bash
curl -X POST http://localhost:8000/api/ingestion/datagov -H "Content-Type: application/json" -d '{"resource_id":"9ef84268-d588-465a-a308-a864a43d0070","limit":100,"filters":[]}'
```

Live ingestion needs a valid API key. Mocked tests need no live credentials.

## Run Scrapy
From the backend directory:

```bash
scrapy list
scrapy crawl datagov_portal_catalog -O /tmp/portal-pages.jsonl
```

Configure the reusable spider with selectors inspected from a permitted public site. Reuse the same JOBDIR to resume an interrupted crawl. The example.gov.in spider is an inactive template, not a live source configuration.

Respect robots.txt, terms and rate limits. Do not bypass logins, CAPTCHAs or access controls. Keep keys/tokens in environment variables and never commit .env.

## Remaining milestones
Validate live credentials/resource schema; configure two actual approved public notice sources; add Playwright only for JS-rendered pages; add Celery/Redis queues, OCR, migrations, auth, stronger quality metrics and production deployment.
