import argparse
import csv
import json
import re
import sys
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Literal, TypedDict


class Issue(TypedDict):
    row: int
    field: str
    message: str


class Report(TypedDict):
    schema_version: int
    status: Literal["PASS", "FAIL"]
    rows: int
    valid_rows: int
    invalid_rows: int
    valid_total: str
    issues: list[Issue]


def validate_csv(path: Path) -> Report:
    issues: list[Issue] = []
    rows = valid_rows = 0
    total = Decimal("0.00")
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        if next(reader, None) != ["item", "quantity", "unit_price"]:
            raise ValueError("Expected header: item,quantity,unit_price.")
        for number, cells in enumerate(reader, start=2):
            rows += 1
            row_issues: list[Issue] = []
            if len(cells) != 3:
                row_issues.append({
                    "row": number, "field": "row",
                    "message": "Expected exactly three cells.",
                })
            else:
                item, quantity, price = (cell.strip() for cell in cells)
                if not item:
                    row_issues.append({
                        "row": number, "field": "item",
                        "message": "Item must be nonempty.",
                    })
                if not re.fullmatch(r"[1-9][0-9]{0,3}", quantity):
                    row_issues.append({
                        "row": number, "field": "quantity",
                        "message": "Quantity must be an integer from 1 to 9999.",
                    })
                if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", price):
                    row_issues.append({
                        "row": number, "field": "unit_price",
                        "message": "Price must be nonnegative with at most two decimals.",
                    })
                if not row_issues:
                    with localcontext() as context:
                        context.prec = max(len(price), len(total.as_tuple().digits)) + 10
                        total += Decimal(quantity) * Decimal(price)
                    valid_rows += 1
            issues.extend(row_issues)
    if rows == 0:
        raise ValueError("CSV must contain at least one data row.")
    return {
        "schema_version": 1,
        "status": "FAIL" if issues else "PASS",
        "rows": rows,
        "valid_rows": valid_rows,
        "invalid_rows": rows - valid_rows,
        "valid_total": format(total, ".2f"),
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise ValueError("Output already exists. Choose a new report path.")
        report = validate_csv(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as destination:
            destination.write(json.dumps(report, indent=2) + "\n")
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(f"{report['status']}: {report['valid_rows']}/{report['rows']} valid rows.")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
