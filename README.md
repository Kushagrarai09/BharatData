# BharatData — Government & Open Data Intelligence Platform

## Project Overview

BharatData is a government and open-data ingestion platform focused on collecting, cleaning, organizing and serving public Indian datasets. It is designed to turn scattered government data—starting with mandi market prices—into consistent records that can be queried through an API and explored in a dashboard.

### How it works

1. **Collect data from a source.** The primary working ingestion path calls the official data.gov.in resource API. It requests records in pages using an offset, and retries temporary failures such as rate limits and server errors with bounded exponential backoff. An optional Apify adapter is also available. The Scrapy package provides a reusable crawler foundation for permitted public websites; its example notice and mandi spiders are templates, not preconfigured live sources.
2. **Normalize the incoming records.** Source-specific normalizers clean text, standardize dates and convert mandi price fields into consistent numeric values. The original source payload is retained so that source details are not lost.
3. **Identify records consistently.** BharatData creates a stable identity for each logical mandi observation using fields such as state, district, market, commodity, variety, grade and arrival date. Price fields are deliberately excluded from that identity because prices can change while the observation remains the same.
4. **Save without creating repeat rows.** During a mandi import, a matching logical record is updated with the latest values; a new record is inserted only when no match exists. The ingestion operation reports how many records were seen, added or updated.
5. **Access and inspect the data.** FastAPI exposes ingestion and document-extraction endpoints, while the React dashboard provides a user interface for working with the platform. PDF text/table extraction is available as a separate capability.

**Current implementation boundary:** the data.gov.in mandi API path is connected to the database persistence flow. Scrapy currently provides crawler infrastructure and parsing examples, but scraped items are not yet wired into that same persistence pipeline. Live imports also require a valid data.gov.in API key in the local environment.

### Main capabilities

- Official data.gov.in client with pagination, bounded retries, exponential backoff and `Retry-After` handling.
- Mandi-specific normalization and stable-key upserts to reduce duplicate logical records.
- FastAPI ingestion and PDF extraction endpoints.
- Optional Apify adapter and a configurable Scrapy foundation with robots.txt compliance, throttling, retries and resumable crawls.
- React dashboard, automated backend tests and a GitHub Actions test workflow.

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
