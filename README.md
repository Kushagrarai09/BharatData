# BharatData — Government & Open Data Intelligence Platform

BharatData collects public Indian government datasets and documents, normalizes records, detects repeated logical records and exposes data through a REST API and dashboard.

## Implemented foundation
- Official data.gov.in resource API client with offset pagination, bounded retries, exponential backoff and Retry-After support.
- Mandi-specific normalization for dates and prices, with a stable record identity excluding mutable price fields.
- Repeat imports update existing logical records instead of creating duplicates.
- One-click mandi ingestion API route: POST /api/ingestion/mandi?limit=100.
- Optional Apify provider adapter.
- Scrapy starter with robots.txt compliance, AutoThrottle, retries, cookies, configurable CSS selectors, pagination and resumable JOBDIR runs.
- Basic PDF text/table extraction, FastAPI endpoints and React dashboard.
- Mocked API tests, SQLite persistence tests, Scrapy parser tests and GitHub Actions backend test workflow.

## Setup
1. Copy .env.example to .env.
2. Set DATA_GOV_IN_API_KEY to your personal data.gov.in API key.
3. Change POSTGRES_PASSWORD from the development default if needed.
4. Run docker compose up --build.
5. API docs: http://localhost:8000/docs; dashboard: http://localhost:5173.

## Import mandi prices
Resource UUID: 9ef84268-d588-465a-a308-a864a43d0070.

```bash
curl -X POST "http://localhost:8000/api/ingestion/mandi?limit=100"
```

A valid API key is required for live ingestion. Mocked tests require no live credentials.

## Run tests
From the backend directory:

```bash
pip install -r requirements.txt
pytest -q
```

## Run Scrapy
From the backend directory:

```bash
scrapy list
scrapy crawl datagov_portal_catalog -O /tmp/portal-pages.jsonl
```

Configure the reusable spider with CSS selectors inspected from a permitted public site. Reuse the same JOBDIR to resume an interrupted crawl:

```bash
scrapy crawl configurable_public -a config='{"name":"sample","allowed_domains":["example.gov.in"],"start_urls":["https://example.gov.in/notices"]}' -s JOBDIR=crawls/sample-notices
```

The example.gov.in spider is an inactive template, not a live configured source. Verify actual website terms, robots.txt and markup before configuring crawlers. Never bypass authentication, CAPTCHAs or access controls.

## Remaining milestones
- Verify the live data.gov.in API key, resource access and response schema.
- Configure two actual approved public notice sources after inspecting their current page markup and terms.
- Integrate Scrapy output into the same persistence pipeline.
- Add Playwright only for JavaScript-rendered pages, Celery/Redis queues, OCR, migrations, auth, stronger quality metrics and production deployment.
