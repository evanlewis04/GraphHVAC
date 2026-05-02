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

from pathlib import Path


def generate(out_dir: Path, seed: int = 42) -> None:
    raise NotImplementedError
