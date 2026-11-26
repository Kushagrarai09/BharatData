# BharatData — Government & Open Data Intelligence Platform

BharatData collects public Indian government datasets and documents, normalizes the results, detects repeat records and exposes data through an API and dashboard.

## Capabilities in this MVP
- Official data.gov.in client with offset pagination, bounded retries, exponential backoff and Retry-After support.
- Mandi-specific normalization, dates/amounts and a stable record identity that excludes mutable price values.
- Transactional ingestion that updates repeat logical records rather than creating duplicates.
- Optional Apify provider adapter.
- Scrapy starter engine with robots.txt compliance, AutoThrottle, retry middleware, cookies, configurable CSS selectors, pagination and resumable JOBDIR runs.
- Basic PDF text/table extraction, FastAPI API and React dashboard.
- Mocked API tests, SQLite persistence tests and a GitHub Actions test workflow.

## Run
1. Copy `.env.example` to `.env` and set `DATA_GOV_IN_API_KEY` with your own data.gov.in key.
2. Run `docker compose up --build`.
3. API docs: http://localhost:8000/docs; dashboard: http://localhost:5173.

## Import mandi prices
Resource UUID: `9ef84268-d588-465a-a308-a864a43d0070`.

```bash
curl -X POST http://localhost:8000/api/ingestion/datagov -H "Content-Type: application/json" -d '{"resource_id":"9ef84268-d588-465a-a308-a864a43d0070","limit":100,"filters":[]}'
```

A valid API key is required for live ingestion. Unit/integration tests use mocked HTTP and do not require a key.

## Run Scrapy
From the backend directory:

```bash
scrapy list
scrapy crawl datagov_portal_catalog -O /tmp/portal-pages.jsonl
```

For a permitted public page, pass source-specific selectors to the configurable spider and reuse the same JOBDIR to resume an interrupted run:

```bash
scrapy crawl configurable_public -a config='{"name":"sample","allowed_domains":["example.gov.in"],"start_urls":["https://example.gov.in/notices"]}' -s JOBDIR=crawls/sample-notices
```

The example.gov.in spider is an inactive template, not a real configured source. Verify the actual website's terms, robots.txt and markup before configuring a crawler. Never bypass authentication, CAPTCHAs or access controls.

## Next milestones
Live credential/resource validation; two inspected and permitted notice sources; Playwright for JavaScript-only pages; Celery/Redis queues; OCR; richer quality checks; Alembic migrations; authentication and deployment monitoring.
