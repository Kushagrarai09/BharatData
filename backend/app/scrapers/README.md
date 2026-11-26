# BharatData Scrapy engine

This package provides a polite crawler for permitted public websites. Prefer official APIs for structured open datasets; use Scrapy for public HTML pages and discovery.

## Run
From the backend directory after installing requirements:

```bash
scrapy list
scrapy crawl datagov_portal_catalog -O /tmp/portal-pages.jsonl
```

For a public site whose terms permit crawling, configure the reusable spider with inspected CSS selectors:

```bash
scrapy crawl configurable_public -a config='{"name":"sample","allowed_domains":["example.gov.in"],"start_urls":["https://example.gov.in/notices"]}' -s JOBDIR=crawls/sample-notices
```

Reuse the same JOBDIR to resume an interrupted crawl. Set source-specific selectors only after inspecting the actual page markup. The example.gov.in template is inactive and is not a real configured source. Obey robots.txt, source terms and rate limits; do not bypass authentication, CAPTCHAs or access controls.
