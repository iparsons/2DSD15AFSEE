#!/usr/bin/env python3
"""Vendor Cost Comparison Tool

Reads a vendor pricing file (tab or comma separated), identifies each SKU's
primary vendor, and compares its landed cost against up to 4 alternative
vendors. Prints a console summary and exports detailed results to CSV.

Supports two CSV layouts:
  1. Wide format (your vendor tool export) — one row per SKU with columns:
     sku, item_short_description, segmentid, OS Primary,
     VendorID_1..5, cost_1..5, Landed_Cost_1..5, OrderMultiple_1..5, MOQ_1..5

  2. Simple format — one row per vendor-item pair with columns:
     item, vendor, unit_cost, is_primary

Usage:
    python vendor_compare.py <path_to_csv>
"""

import csv
import os
import sys


def detect_delimiter(filepath):
    """Detect whether the file is tab or comma separated."""
    with open(filepath, newline="") as f:
        first_line = f.readline()
    if "\t" in first_line:
        return "\t"
    return ","


def detect_format(fieldnames):
    """Detect whether the CSV is wide format or simple format."""
    if "sku" in fieldnames and "VendorID_1" in fieldnames:
        return "wide"
    if "item" in fieldnames and "vendor" in fieldnames:
        return "simple"
    return None


def load_wide_format(filepath, delimiter):
    """Load vendor data from the wide-format vendor tool export.

    Returns a list of dicts, one per SKU:
        {sku, description, segment, primary_vendor_id,
         vendors: [{vendor_id, cost, landed_cost, order_multiple, moq}, ...]}
    """
    records = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            sku = row.get("sku", "").strip()
            if not sku:
                continue

            primary_vendor_id = row.get("OS Primary", "").strip()
            description = row.get("item_short_description", "").strip()
            segment = row.get("segmentid", "").strip()

            vendors = []
            for i in range(1, 6):
                vid = (row.get(f"VendorID_{i}") or "").strip()
                lc = (row.get(f"Landed_Cost_{i}") or "").strip()
                if not vid or not lc:
                    continue
                try:
                    landed_cost = float(lc)
                except ValueError:
                    continue

                raw_cost_str = (row.get(f"cost_{i}") or "").strip()
                raw_cost = float(raw_cost_str) if raw_cost_str else None

                om_str = (row.get(f"OrderMultiple_{i}") or "").strip()
                order_multiple = int(float(om_str)) if om_str else None

                moq_str = (row.get(f"MOQ_{i}") or "").strip()
                moq = int(float(moq_str)) if moq_str else None

                vendors.append({
                    "vendor_id": vid,
                    "cost": raw_cost,
                    "landed_cost": landed_cost,
                    "order_multiple": order_multiple,
                    "moq": moq,
                })

            if vendors:
                records.append({
                    "sku": sku,
                    "description": description,
                    "segment": segment,
                    "primary_vendor_id": primary_vendor_id,
                    "vendors": vendors,
                })
    return records


def load_simple_format(filepath, delimiter):
    """Load vendor data from the simple long format.

    Returns a list of dicts in the same structure as load_wide_format.
    """
    from collections import defaultdict

    items = defaultdict(lambda: {"vendors": [], "primary_vendor_id": None})
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            item = row["item"].strip()
            vendor = row["vendor"].strip()
            unit_cost = float(row["unit_cost"].strip())
            is_primary = row.get("is_primary", "").strip().lower() in ("yes", "true", "1")

            items[item]["vendors"].append({
                "vendor_id": vendor,
                "cost": unit_cost,
                "landed_cost": unit_cost,
                "order_multiple": None,
                "moq": None,
            })
            if is_primary:
                items[item]["primary_vendor_id"] = vendor

    records = []
    for item_name, data in items.items():
        records.append({
            "sku": item_name,
            "description": "",
            "segment": "",
            "primary_vendor_id": data["primary_vendor_id"],
            "vendors": data["vendors"],
        })
    return records


def analyze(record):
    """Analyze a single SKU record.

    Returns a result dict or None if the primary vendor can't be identified.
    """
    primary_id = record["primary_vendor_id"]
    vendors = record["vendors"]

    # Find the primary vendor entry
    primary = None
    for v in vendors:
        if v["vendor_id"] == primary_id:
            primary = v
            break

    if primary is None:
        return None

    lowest = min(vendors, key=lambda v: v["landed_cost"])
    savings = round(primary["landed_cost"] - lowest["landed_cost"], 2)

    return {
        "sku": record["sku"],
        "description": record["description"],
        "segment": record["segment"],
        "primary_vendor": primary["vendor_id"],
        "primary_landed_cost": primary["landed_cost"],
        "primary_raw_cost": primary["cost"],
        "lowest_vendor": lowest["vendor_id"],
        "lowest_landed_cost": lowest["landed_cost"],
        "savings": savings,
        "is_primary_lowest": savings == 0,
        "num_vendors": len(vendors),
    }


def print_report(results):
    """Print a summary report to the console."""
    items_at_lowest = sum(1 for r in results if r["is_primary_lowest"])
    items_with_savings = sum(1 for r in results if not r["is_primary_lowest"])
    total_primary = sum(r["primary_landed_cost"] for r in results)
    total_lowest = sum(r["lowest_landed_cost"] for r in results)
    total_savings = round(total_primary - total_lowest, 2)

    print()
    print("=" * 90)
    print("  VENDOR COST COMPARISON REPORT  (by Landed Cost)")
    print("=" * 90)

    print()
    print(f"    Total SKUs analyzed:               {len(results)}")
    print(f"    Primary is lowest cost:            {items_at_lowest}")
    print(f"    Cheaper alternative available:      {items_with_savings}")
    print()
    print(f"    Total primary landed cost:          ${total_primary:,.2f}")
    print(f"    Total lowest available cost:        ${total_lowest:,.2f}")
    print(f"    Total potential savings:            ${total_savings:,.2f}")
    if total_primary > 0 and total_savings > 0:
        pct = (total_savings / total_primary) * 100
        print(f"    Savings as % of primary cost:      {pct:.1f}%")

    # Top savings opportunities
    savings_items = sorted(
        [r for r in results if not r["is_primary_lowest"]],
        key=lambda r: r["savings"],
        reverse=True,
    )

    if savings_items:
        top_n = min(10, len(savings_items))
        print()
        print("-" * 90)
        print(f"  TOP {top_n} SAVINGS OPPORTUNITIES")
        print("-" * 90)
        print(f"  {'SKU':<20} {'Description':<25} {'Primary':<10} {'Prim LC':>10} {'Lowest':>10} {'Lowest LC':>10} {'Savings':>10}")
        print(f"  {'-'*20} {'-'*25} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
        for r in savings_items[:top_n]:
            desc = r["description"][:25] if r["description"] else ""
            print(
                f"  {r['sku']:<20} {desc:<25} {r['primary_vendor']:<10} "
                f"${r['primary_landed_cost']:>9,.2f} {r['lowest_vendor']:>10} "
                f"${r['lowest_landed_cost']:>9,.2f} ${r['savings']:>9,.2f}"
            )

    print()
    print("=" * 90)
    print()


def export_csv(results, output_path):
    """Write detailed results to a CSV file."""
    fieldnames = [
        "sku", "item_short_description", "segmentid",
        "primary_vendor", "primary_landed_cost",
        "lowest_cost_vendor", "lowest_landed_cost",
        "savings", "is_primary_lowest", "num_vendors_compared",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "sku": r["sku"],
                "item_short_description": r["description"],
                "segmentid": r["segment"],
                "primary_vendor": r["primary_vendor"],
                "primary_landed_cost": r["primary_landed_cost"],
                "lowest_cost_vendor": r["lowest_vendor"],
                "lowest_landed_cost": r["lowest_landed_cost"],
                "savings": r["savings"],
                "is_primary_lowest": "Yes" if r["is_primary_lowest"] else "No",
                "num_vendors_compared": r["num_vendors"],
            })


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <csv_file>")
        print(f"Example: python {sys.argv[0]} sample_data.csv")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        delimiter = detect_delimiter(filepath)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        fieldnames = reader.fieldnames

    fmt = detect_format(fieldnames)
    if fmt is None:
        print("Error: Unrecognized CSV format.")
        print("Expected either wide format (sku, VendorID_1, Landed_Cost_1, ...)")
        print("or simple format (item, vendor, unit_cost, is_primary).")
        sys.exit(1)

    if fmt == "wide":
        records = load_wide_format(filepath, delimiter)
    else:
        records = load_simple_format(filepath, delimiter)

    if not records:
        print("No data found in the file.")
        sys.exit(1)

    results = []
    skipped = 0
    for rec in records:
        result = analyze(rec)
        if result is None:
            skipped += 1
            continue
        results.append(result)

    if skipped > 0:
        print(f"  Note: Skipped {skipped} SKU(s) where primary vendor could not be matched.")

    if not results:
        print("No SKUs with a matched primary vendor found.")
        sys.exit(1)

    print_report(results)

    # Export CSV alongside the input file
    input_dir = os.path.dirname(os.path.abspath(filepath))
    output_path = os.path.join(input_dir, "comparison_results.csv")
    export_csv(results, output_path)
    print(f"  Detailed results exported to: {output_path}")
    print()


if __name__ == "__main__":
    main()
