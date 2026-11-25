# Architecture

```text
data.gov.in API ─────┐
                     ├── Provider adapters ── Normalization ── Fingerprint / dedupe
Apify actor ─────────┘                                      │
                                                            ▼
Public PDF upload ── pdfplumber ── Documents table     PostgreSQL
                                                            │
                                                            ▼
                                                     FastAPI REST API
                                                            │
                                                            ▼
                                                    React operations UI
```

## Design choices
- Official data.gov.in API is the preferred source-to-source integration.
- Apify is an optional adapter, not a hard dependency.
- Original provider fields are retained in JSON payloads.
- SHA-256 fingerprints make identical imports idempotent per source.
- PDF extraction stores extracted text and returns page-level/table output. OCR and automatic field extraction are future milestones.
- Current ingestion endpoints are synchronous; large runs should move to a worker queue.
