# BharatData Scrapy engine

Use official APIs for structured data where available. This crawler is for permitted public HTML pages and discovery.

## Run
From backend after installing requirements:

```bash
scrapy list
scrapy crawl datagov_portal_catalog -O /tmp/portal-pages.jsonl
```

## Configure a public source
Inspect the site's markup, usage terms and robots.txt first, then pass selectors to the reusable spider:

```bash
scrapy crawl configurable_public -a config='{"name":"sample","allowed_domains":["example.gov.in"],"start_urls":["https://example.gov.in/notices"]}' -s JOBDIR=crawls/sample-notices
```

Reuse the same JOBDIR to resume an interrupted crawl. The example.gov.in spider is an inactive template; it is not a live configured target. Obey source terms, robots.txt and rate limits. Do not bypass logins, CAPTCHAs or access controls.
