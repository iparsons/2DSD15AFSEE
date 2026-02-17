#!/usr/bin/env python3
"""Vendor Cost Comparison Tool

Reads a CSV file containing per-item vendor pricing, identifies the primary
vendor for each item, and reports whether a lower-cost alternative exists.

CSV format (columns):
    item         - Name/identifier of the product or part
    vendor       - Vendor name
    unit_cost    - Cost per unit from that vendor
    is_primary   - "yes" if this is the current primary vendor, "no" otherwise

Usage:
    python vendor_compare.py <path_to_csv>
    python vendor_compare.py sample_data.csv
"""

import csv
import sys
from collections import defaultdict


def load_vendor_data(filepath):
    """Load vendor pricing data from a CSV file.

    Returns a dict mapping each item to a list of
    {"vendor": str, "unit_cost": float, "is_primary": bool} entries.
    """
    items = defaultdict(list)
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = row["item"].strip()
            vendor = row["vendor"].strip()
            unit_cost = float(row["unit_cost"].strip())
            is_primary = row["is_primary"].strip().lower() in ("yes", "true", "1")
            items[item].append({
                "vendor": vendor,
                "unit_cost": unit_cost,
                "is_primary": is_primary,
            })
    return dict(items)


def analyze_item(item_name, vendors):
    """Analyze a single item's vendor pricing.

    Returns a dict with:
        item            - item name
        primary_vendor  - name of the primary vendor
        primary_cost    - primary vendor's unit cost
        lowest_vendor   - name of the lowest-cost vendor
        lowest_cost     - lowest unit cost
        savings         - cost difference (primary - lowest), 0 if primary is lowest
        is_primary_lowest - True if primary vendor is already the cheapest
    """
    primary = None
    for v in vendors:
        if v["is_primary"]:
            primary = v
            break

    if primary is None:
        return None

    lowest = min(vendors, key=lambda v: v["unit_cost"])

    savings = round(primary["unit_cost"] - lowest["unit_cost"], 2)

    return {
        "item": item_name,
        "primary_vendor": primary["vendor"],
        "primary_cost": primary["unit_cost"],
        "lowest_vendor": lowest["vendor"],
        "lowest_cost": lowest["unit_cost"],
        "savings": savings,
        "is_primary_lowest": savings == 0,
    }


def print_report(results):
    """Print a formatted comparison report to stdout."""
    separator = "-" * 90

    print()
    print("=" * 90)
    print("  VENDOR COST COMPARISON REPORT")
    print("=" * 90)

    items_at_lowest = 0
    items_with_savings = 0
    total_primary_cost = 0.0
    total_lowest_cost = 0.0

    for r in results:
        total_primary_cost += r["primary_cost"]
        total_lowest_cost += r["lowest_cost"]

        print(separator)
        print(f"  Item: {r['item']}")
        print(f"    Primary vendor:      {r['primary_vendor']}  @ ${r['primary_cost']:.2f}")
        print(f"    Lowest-cost vendor:  {r['lowest_vendor']}  @ ${r['lowest_cost']:.2f}")

        if r["is_primary_lowest"]:
            print(f"    Status:              PRIMARY IS LOWEST COST")
            items_at_lowest += 1
        else:
            print(f"    Status:              SAVINGS AVAILABLE  -  ${r['savings']:.2f} less with {r['lowest_vendor']}")
            items_with_savings += 1

    total_savings = round(total_primary_cost - total_lowest_cost, 2)

    print()
    print("=" * 90)
    print("  SUMMARY")
    print("=" * 90)
    print(f"    Total items analyzed:              {len(results)}")
    print(f"    Items where primary is lowest:     {items_at_lowest}")
    print(f"    Items with cheaper alternative:    {items_with_savings}")
    print(f"    Total primary vendor cost:         ${total_primary_cost:.2f}")
    print(f"    Total lowest available cost:       ${total_lowest_cost:.2f}")
    print(f"    Total potential savings:           ${total_savings:.2f}")

    if total_savings > 0:
        pct = (total_savings / total_primary_cost) * 100
        print(f"    Savings as % of primary cost:     {pct:.1f}%")

    print("=" * 90)
    print()


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <csv_file>")
        print(f"Example: python {sys.argv[0]} sample_data.csv")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        data = load_vendor_data(filepath)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing expected column in CSV: {e}")
        print("Required columns: item, vendor, unit_cost, is_primary")
        sys.exit(1)

    if not data:
        print("No data found in the CSV file.")
        sys.exit(1)

    results = []
    for item_name, vendors in data.items():
        result = analyze_item(item_name, vendors)
        if result is None:
            print(f"Warning: No primary vendor marked for '{item_name}', skipping.")
            continue
        results.append(result)

    if not results:
        print("No items with a primary vendor found.")
        sys.exit(1)

    print_report(results)


if __name__ == "__main__":
    main()
