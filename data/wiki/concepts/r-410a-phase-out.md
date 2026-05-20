---
type: concept
topic: R-410A phase-out exposure
---

# R-410A Phase-Out Exposure

The HFC phase-down under the AIM Act bans manufacture of new R-410A residential
equipment starting January 2025. Service refills and existing inventory remain
legal but tighten quickly. Customers concentrated on R-410A-tied SKUs need
replacement-system quotes (R-32 or R-454B) and refrigerant pre-buy guidance.

**Total 24-month revenue from R-410A-tied SKUs:** $5,698,248

## Top 25 customers by R-410A exposure

| Customer | Name | Segment | Region | 24mo R-410A revenue |
|---|---|---|---|---|
| [[customers/CUS-0415]] | Eagle AC & Heat #415 | Builder | Midwest | $32,745 |
| [[customers/CUS-0187]] | Granite Heating & Cooling #187 | Residential Contractor | Northeast | $31,847 |
| [[customers/CUS-0239]] | Patriot AC & Heat #239 | Builder | West | $31,309 |
| [[customers/CUS-0021]] | Greenfield Mechanical #21 | Commercial Contractor | Southwest | $31,105 |
| [[customers/CUS-0012]] | Patriot Comfort Solutions #12 | Property Manager | Northeast | $30,059 |
| [[customers/CUS-0065]] | Lakeside AC & Heat #65 | Commercial Contractor | Southwest | $28,966 |
| [[customers/CUS-0324]] | Lakeside Property Group #324 | Property Manager | Northeast | $27,577 |
| [[customers/CUS-0069]] | Highland Climate Pros #69 | Property Manager | Midwest | $27,015 |
| [[customers/CUS-0434]] | Granite Air Systems #434 | Property Manager | Southwest | $26,315 |
| [[customers/CUS-0124]] | Riverside Building Services #124 | Residential Contractor | West | $25,524 |
| [[customers/CUS-0257]] | Cardinal Heating & Cooling #257 | Residential Contractor | West | $25,171 |
| [[customers/CUS-0073]] | Coastal Heating & Cooling #73 | Commercial Contractor | Southwest | $24,671 |
| [[customers/CUS-0024]] | Summit Refrigeration #24 | Residential Contractor | Southwest | $24,512 |
| [[customers/CUS-0076]] | Metro Climate Pros #76 | Property Manager | Northeast | $24,450 |
| [[customers/CUS-0101]] | Bluebird Air Systems #101 | Residential Contractor | Southwest | $23,608 |
| [[customers/CUS-0107]] | Iron Property Group #107 | Residential Contractor | Southeast | $23,001 |
| [[customers/CUS-0091]] | Eagle Building Services #91 | Commercial Contractor | Southeast | $22,821 |
| [[customers/CUS-0105]] | Patriot HVAC Services #105 | Commercial Contractor | Southwest | $22,755 |
| [[customers/CUS-0423]] | Highland Heating & Cooling #423 | Property Manager | Northeast | $22,560 |
| [[customers/CUS-0246]] | Greenfield Climate Pros #246 | Property Manager | Southeast | $22,408 |
| [[customers/CUS-0094]] | Liberty Comfort Solutions #94 | Commercial Contractor | Southeast | $21,966 |
| [[customers/CUS-0139]] | Riverside AC & Heat #139 | Residential Contractor | Southeast | $21,847 |
| [[customers/CUS-0099]] | Liberty Air Systems #99 | Residential Contractor | Southwest | $21,801 |
| [[customers/CUS-0126]] | Acme HVAC Services #126 | Commercial Contractor | Southwest | $21,435 |
| [[customers/CUS-0311]] | Granite Building Services #311 | Property Manager | Northeast | $20,932 |

## Recommended actions
- Outreach to top-10 customers for replacement equipment quotes (route to [[refrigerants/r-32]] or [[refrigerants/r-454b]])
- Refrigerant pre-buy guidance ahead of Q4 price escalation
- Inventory triage: drawdown plan for R-410A SKUs at warehouses (see [[warehouses/]] pages)

## Sources
- DuckDB: `SELECT customer_id, SUM(extended_price) FROM orders o JOIN skus s ON o.sku_id=s.id WHERE s.refrigerant='R-410A' GROUP BY 1 ORDER BY 2 DESC`
- See also: [[refrigerants/r-410a]], [[concepts/supplier-concentration]]
