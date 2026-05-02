"""Generate realistic synthetic HVAC distributor data.

Targets (from the MVP sketch):
  - ~5,000 SKUs across the standard HVAC parts ontology
    (capacitors, contactors, motors, refrigerants, coils, control boards,
    thermostats), tagged with manufacturers (Lennox, Carrier, Trane, etc.)
  - ~20 suppliers including 1-2 master distributors
  - ~500 customers (mix of contractors, builders, property managers)
  - 4-6 warehouses across plausible regions
  - ~2 years of order + inventory history with seasonality
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

MANUFACTURERS = [
    "Lennox", "Carrier", "Trane", "Goodman", "Rheem", "York", "Daikin",
    "Mitsubishi", "Bryant", "Heil", "Amana", "Honeywell", "White-Rodgers",
    "Ecobee", "Emerson", "Copeland", "GE", "Marathon", "US Motors", "Fasco",
]

# (category, sub-types, tag for SKU code)
CATEGORIES: list[tuple[str, list[str], str]] = [
    ("Capacitor", ["Run", "Start", "Dual-Run", "Hard-Start"], "CAP"),
    ("Contactor", ["1-Pole", "2-Pole", "3-Pole"], "CON"),
    ("Motor", ["Condenser Fan", "Blower", "ECM Blower", "Inducer"], "MTR"),
    ("Refrigerant", ["R-22", "R-410A", "R-32", "R-454B", "R-1234yf"], "RFG"),
    ("Coil", ["Evaporator", "Condenser", "A-Coil", "Slab"], "COL"),
    ("ControlBoard", ["Furnace IFC", "Ignition Module", "Defrost Board"], "CTL"),
    ("Thermostat", ["Programmable", "Smart Wi-Fi", "Conventional", "Heat-Pump"], "TST"),
]

SUPPLIER_NAMES = [
    "Global Industries", "MARS (Master)", "RE Michel", "ABCO Distribution",
    "Johnstone Supply", "Goodin Company", "Munch's Supply", "Carrier Enterprise",
    "Trane Supply", "Lennox PartsPlus", "Refrigeration Sales Corp",
    "Gemaire Distributors", "Baker Distributing", "Coastal HVAC Supply",
    "Northern HVAC Wholesale", "Pacific Coast Parts", "Shearer Supply",
    "Hills Distribution", "Team Air Distributing", "Everflow Supplies",
]

WAREHOUSES = [
    ("WH-ATL", "Atlanta DC", "GA"),
    ("WH-DAL", "Dallas DC", "TX"),
    ("WH-PHX", "Phoenix DC", "AZ"),
    ("WH-CHI", "Chicago DC", "IL"),
    ("WH-CHA", "Charlotte DC", "NC"),
]

CUSTOMER_SEGMENTS = ["Residential Contractor", "Commercial Contractor", "Property Manager", "Builder"]

REGIONS = ["Southeast", "Southwest", "Midwest", "Northeast", "West"]


@dataclass
class SKU:
    id: str
    name: str
    category: str
    sub_type: str
    manufacturer: str
    primary_supplier_id: str
    unit_cost: float
    list_price: float
    refrigerant: str | None  # for SKUs that contain or are designed for a refrigerant


@dataclass
class Supplier:
    id: str
    name: str
    is_master: bool
    primary_category: str


@dataclass
class Customer:
    id: str
    name: str
    segment: str
    region: str
    primary_warehouse_id: str


@dataclass
class Warehouse:
    id: str
    name: str
    state: str


def _seasonal_multiplier(d: date, category: str) -> float:
    """Cooling parts spike May-Aug; heating parts spike Nov-Feb."""
    month = d.month
    cooling = category in {"Capacitor", "Contactor", "Motor", "Refrigerant", "Coil"}
    heating = category in {"ControlBoard"}
    # A shifted cosine that peaks at month 7 (July) for cooling, month 1 (Jan) for heating.
    cool_curve = 1.0 + 0.7 * math.cos((month - 7) * math.pi / 6)
    heat_curve = 1.0 + 0.7 * math.cos((month - 1) * math.pi / 6)
    if cooling:
        return cool_curve
    if heating:
        return heat_curve
    return 1.0


def _gen_skus(rng: random.Random, suppliers: list[Supplier], n_target: int = 5000) -> list[SKU]:
    skus: list[SKU] = []
    per_category = n_target // len(CATEGORIES)
    for category, sub_types, tag in CATEGORIES:
        for i in range(per_category):
            sub = rng.choice(sub_types)
            mfr = rng.choice(MANUFACTURERS)
            # Suppliers that "carry" this category — master distributors carry everything.
            eligible = [s for s in suppliers if s.is_master or s.primary_category == category]
            supplier = rng.choice(eligible) if eligible else rng.choice(suppliers)

            spec_token = ""
            refrigerant: str | None = None
            if category == "Capacitor":
                spec_token = f"{rng.choice([5, 7, 10, 15, 20, 30, 35, 40, 45, 55, 65, 80])}MFD"
            elif category == "Contactor":
                spec_token = f"{rng.choice([24, 30, 40, 50])}A"
            elif category == "Motor":
                hp = rng.choice(["1/4", "1/3", "1/2", "3/4", "1"])
                spec_token = f"{hp.replace('/', '-')}HP"
            elif category == "Refrigerant":
                refrigerant = sub
                spec_token = f"{rng.choice([10, 25, 30, 50])}LB"
            elif category == "Coil":
                spec_token = f"{rng.choice([15, 20, 25, 30, 36, 42, 48, 60])}KBTU"
            elif category == "Thermostat":
                spec_token = rng.choice(["24V", "MULTI", "WIFI"])

            sku_id = f"{tag}-{mfr[:3].upper()}-{spec_token}-{i:04d}"
            sku_id = sku_id.replace("--", "-")
            cost = round(rng.uniform(8, 280), 2)
            price = round(cost * rng.uniform(1.25, 1.9), 2)

            # If a non-refrigerant SKU is "for" a system, sometimes tag it with a refrigerant
            if refrigerant is None and category in {"Coil", "Motor"} and rng.random() < 0.55:
                refrigerant = rng.choices(
                    ["R-410A", "R-32", "R-454B", "R-22"],
                    weights=[0.55, 0.2, 0.15, 0.10],
                )[0]

            name = f"{mfr} {sub} {category} {spec_token}".strip()
            skus.append(SKU(
                id=sku_id,
                name=name,
                category=category,
                sub_type=sub,
                manufacturer=mfr,
                primary_supplier_id=supplier.id,
                unit_cost=cost,
                list_price=price,
                refrigerant=refrigerant,
            ))
    return skus


def _gen_suppliers(rng: random.Random) -> list[Supplier]:
    suppliers: list[Supplier] = []
    for i, name in enumerate(SUPPLIER_NAMES):
        is_master = "Master" in name or i < 2
        category = rng.choice([c[0] for c in CATEGORIES])
        suppliers.append(Supplier(
            id=f"SUP-{i + 1:03d}",
            name=name,
            is_master=is_master,
            primary_category=category,
        ))
    return suppliers


def _gen_customers(rng: random.Random, n: int = 500) -> list[Customer]:
    customers: list[Customer] = []
    name_first = ["Acme", "Apex", "Pioneer", "Summit", "Coastal", "Highland", "Riverside",
                  "Metro", "Patriot", "Liberty", "Sunbelt", "Oakwood", "Greenfield",
                  "Lakeside", "Granite", "Cardinal", "Eagle", "Iron", "Bluebird", "Cedar"]
    name_suffix = ["Heating & Cooling", "HVAC Services", "Mechanical", "Climate Pros",
                   "Air Systems", "Comfort Solutions", "Refrigeration", "AC & Heat",
                   "Building Services", "Property Group"]
    for i in range(n):
        wh = rng.choice(WAREHOUSES)
        customers.append(Customer(
            id=f"CUS-{i + 1:04d}",
            name=f"{rng.choice(name_first)} {rng.choice(name_suffix)} #{i + 1}",
            segment=rng.choice(CUSTOMER_SEGMENTS),
            region=rng.choice(REGIONS),
            primary_warehouse_id=wh[0],
        ))
    return customers


def _gen_warehouses() -> list[Warehouse]:
    return [Warehouse(id=w[0], name=w[1], state=w[2]) for w in WAREHOUSES]


def _gen_orders(
    rng: random.Random,
    skus: list[SKU],
    customers: list[Customer],
    warehouses: list[Warehouse],
    days: int = 730,
) -> list[dict]:
    """Two years of order line items with seasonality."""
    orders: list[dict] = []
    sku_by_cat: dict[str, list[SKU]] = {}
    for s in skus:
        sku_by_cat.setdefault(s.category, []).append(s)

    start = date.today() - timedelta(days=days)
    order_id = 1
    # Aim for ~50 orders/day on average; varies with seasonality.
    for day_offset in range(days):
        d = start + timedelta(days=day_offset)
        base_orders = int(rng.gauss(50, 8))
        for _ in range(max(5, base_orders)):
            customer = rng.choice(customers)
            warehouse_id = customer.primary_warehouse_id
            order_id_str = f"ORD-{order_id:07d}"
            order_id += 1
            # Each order has 1-6 line items, weighted toward fewer.
            n_lines = rng.choices([1, 2, 3, 4, 5, 6], weights=[40, 25, 15, 10, 6, 4])[0]
            chosen: set[str] = set()
            for line_no in range(1, n_lines + 1):
                # Pick a category with a seasonal bias.
                cat = rng.choices(
                    [c[0] for c in CATEGORIES],
                    weights=[
                        _seasonal_multiplier(d, c[0]) * (3.0 if c[0] in {"Capacitor", "Motor"} else 1.0)
                        for c in CATEGORIES
                    ],
                )[0]
                sku = rng.choice(sku_by_cat[cat])
                if sku.id in chosen:
                    continue
                chosen.add(sku.id)
                qty = rng.choices([1, 2, 4, 6, 12, 24], weights=[55, 20, 10, 8, 5, 2])[0]
                price = round(sku.list_price * rng.uniform(0.85, 1.0), 2)
                orders.append({
                    "order_id": order_id_str,
                    "line_no": line_no,
                    "order_date": d.isoformat(),
                    "customer_id": customer.id,
                    "warehouse_id": warehouse_id,
                    "sku_id": sku.id,
                    "qty": qty,
                    "unit_price": price,
                    "extended_price": round(qty * price, 2),
                })
    return orders


def _gen_inventory(
    rng: random.Random,
    skus: list[SKU],
    warehouses: list[Warehouse],
) -> list[dict]:
    """Current on-hand inventory snapshot per SKU/warehouse."""
    rows: list[dict] = []
    for sku in skus:
        # SKUs are stocked at a subset of warehouses, biased toward ~3 of 5.
        n_wh = rng.choices([1, 2, 3, 4, 5], weights=[5, 15, 40, 25, 15])[0]
        chosen = rng.sample(warehouses, n_wh)
        for wh in chosen:
            qty = max(0, int(rng.gauss(80, 60)))
            rows.append({
                "sku_id": sku.id,
                "warehouse_id": wh.id,
                "qty_on_hand": qty,
                "reorder_point": int(qty * rng.uniform(0.2, 0.5)),
            })
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate(out_dir: Path, seed: int = 42) -> None:
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    suppliers = _gen_suppliers(rng)
    warehouses = _gen_warehouses()
    skus = _gen_skus(rng, suppliers)
    customers = _gen_customers(rng)
    orders = _gen_orders(rng, skus, customers, warehouses)
    inventory = _gen_inventory(rng, skus, warehouses)

    _write_csv(out_dir / "suppliers.csv", [s.__dict__ for s in suppliers])
    _write_csv(out_dir / "warehouses.csv", [w.__dict__ for w in warehouses])
    _write_csv(out_dir / "skus.csv", [s.__dict__ for s in skus])
    _write_csv(out_dir / "customers.csv", [c.__dict__ for c in customers])
    _write_csv(out_dir / "orders.csv", orders)
    _write_csv(out_dir / "inventory.csv", inventory)

    print(
        f"Generated: {len(suppliers)} suppliers, {len(warehouses)} warehouses, "
        f"{len(skus)} SKUs, {len(customers)} customers, "
        f"{len(orders)} order lines, {len(inventory)} inventory rows -> {out_dir}"
    )
