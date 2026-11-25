# Data source registry

## Mandi prices (included preset)
- Dataset: Current daily price of various commodities from various markets (Mandi)
- Resource ID: `9ef84268-d588-465a-a308-a864a43d0070`
- Publisher: Ministry of Agriculture & Farmers Welfare / Directorate of Marketing & Inspection
- Common fields: state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price
- Portal resource: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi

## Add other datasets
1. Find a dataset on https://data.gov.in/.
2. Open its API tab and copy the resource UUID.
3. Verify its fields and access policy.
4. Send the UUID to `/api/ingestion/datagov` or `/api/ingestion/apify`.
5. Use exact field names in filters (for example `state=Maharashtra`).

Original provider fields are preserved in `data_records.payload`; common normalized fields support cross-dataset search.
