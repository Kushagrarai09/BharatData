# BharatData Scrapy engine

Use official APIs for structured data where available. This crawler is for permitted public HTML pages and discovery.

From the backend directory after installing requirements:

```bash
scrapy list
scrapy crawl datagov_portal_catalog -O /tmp/portal-pages.jsonl
```

Configure the reusable spider with inspected selectors:

```bash
scrapy crawl configurable_public -a config='{"name":"sample","allowed_domains":["example.gov.in"],"start_urls":["https://example.gov.in/notices"]}' -s JOBDIR=crawls/sample-notices
```

Reuse the same JOBDIR to resume an interrupted crawl. The example.gov.in notice spider is an inactive template, not a live target. Respect robots.txt, source terms and rate limits. Do not bypass logins, CAPTCHAs or access controls.
