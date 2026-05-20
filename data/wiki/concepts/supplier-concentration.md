---
type: concept
topic: Supplier concentration
---

# Supplier Concentration

Where one supplier accounts for an outsized share of a single category, a
disruption (price hike, allocation cut, M&A) becomes an immediate operational
issue. This page lists the top supplier x category cells by revenue so the
operating team can see where second-source effort would pay off.

## Top supplier-category combinations (last 24 months)

| Supplier | Name | Category | SKUs | Revenue |
|---|---|---|---|---|
| [[suppliers/SUP-005]] | Johnstone Supply | Motor | 238 | $4,571,226 |
| [[suppliers/SUP-001]] | Global Industries | Motor | 240 | $4,118,341 |
| [[suppliers/SUP-002]] | MARS (Master) | Motor | 236 | $3,926,994 |
| [[suppliers/SUP-001]] | Global Industries | Thermostat | 369 | $2,782,252 |
| [[suppliers/SUP-002]] | MARS (Master) | Thermostat | 345 | $2,615,131 |
| [[suppliers/SUP-018]] | Hills Distribution | Capacitor | 95 | $1,727,086 |
| [[suppliers/SUP-001]] | Global Industries | Capacitor | 88 | $1,714,646 |
| [[suppliers/SUP-014]] | Coastal HVAC Supply | Capacitor | 91 | $1,608,324 |
| [[suppliers/SUP-010]] | Lennox PartsPlus | Capacitor | 92 | $1,594,995 |
| [[suppliers/SUP-016]] | Pacific Coast Parts | Refrigerant | 262 | $1,588,717 |
| [[suppliers/SUP-019]] | Team Air Distributing | Capacitor | 83 | $1,571,080 |
| [[suppliers/SUP-002]] | MARS (Master) | Capacitor | 95 | $1,488,972 |
| [[suppliers/SUP-003]] | RE Michel | Capacitor | 78 | $1,455,201 |
| [[suppliers/SUP-017]] | Shearer Supply | Capacitor | 92 | $1,364,916 |
| [[suppliers/SUP-001]] | Global Industries | Refrigerant | 221 | $1,328,023 |
| [[suppliers/SUP-002]] | MARS (Master) | Refrigerant | 231 | $1,304,079 |
| [[suppliers/SUP-002]] | MARS (Master) | Coil | 195 | $1,189,579 |
| [[suppliers/SUP-011]] | Refrigeration Sales Corp | ControlBoard | 117 | $1,180,040 |
| [[suppliers/SUP-015]] | Northern HVAC Wholesale | Coil | 178 | $1,119,294 |
| [[suppliers/SUP-004]] | ABCO Distribution | ControlBoard | 113 | $1,106,728 |
| [[suppliers/SUP-002]] | MARS (Master) | ControlBoard | 126 | $1,097,892 |
| [[suppliers/SUP-009]] | Trane Supply | ControlBoard | 123 | $1,096,779 |
| [[suppliers/SUP-001]] | Global Industries | ControlBoard | 120 | $1,091,574 |
| [[suppliers/SUP-012]] | Gemaire Distributors | ControlBoard | 115 | $981,245 |
| [[suppliers/SUP-013]] | Baker Distributing | Coil | 179 | $966,418 |
| [[suppliers/SUP-002]] | MARS (Master) | Contactor | 143 | $893,018 |
| [[suppliers/SUP-001]] | Global Industries | Coil | 162 | $855,154 |
| [[suppliers/SUP-001]] | Global Industries | Contactor | 134 | $739,540 |
| [[suppliers/SUP-008]] | Carrier Enterprise | Contactor | 117 | $725,370 |
| [[suppliers/SUP-007]] | Munch's Supply | Contactor | 125 | $716,749 |
| [[suppliers/SUP-006]] | Goodin Company | Contactor | 104 | $618,690 |
| [[suppliers/SUP-020]] | Everflow Supplies | Contactor | 91 | $510,362 |

## Sources
- DuckDB: `SELECT primary_supplier_id, category, COUNT(*), SUM(extended_price) FROM skus JOIN orders USING(sku_id... -- see query above`
