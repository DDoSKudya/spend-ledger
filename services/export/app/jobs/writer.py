import csv
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from app.jobs.schemas import ExportFormat

COLUMNS: tuple[str, ...] = (
    "id",
    "amount",
    "category",
    "tags",
    "description",
    "expense_date",
    "created_at",
)


def write_export_file(
    path: Path,
    export_format: ExportFormat,
    rows: Iterable[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if export_format == ExportFormat.CSV:
        _write_csv(path, rows)
    else:
        _write_xlsx(path, rows)


def _normalize_row(row: dict[str, Any]) -> list[str]:
    category = row.get("category")
    category_name = ""
    if isinstance(category, dict):
        category_name = str(category.get("name", ""))

    tags_raw = row.get("tags")
    tag_names: list[str] = []
    if isinstance(tags_raw, list):
        tag_names = [
            str(tag["name"])
            for tag in tags_raw
            if isinstance(tag, dict) and tag.get("name") is not None
        ]

    values = {
        "id": str(row.get("id", "")),
        "amount": str(row.get("amount", "")),
        "category": category_name,
        "tags": ", ".join(tag_names),
        "description": str(row.get("description") or ""),
        "expense_date": str(row.get("expense_date", "")),
        "created_at": str(row.get("created_at", "")),
    }
    return [values[column] for column in COLUMNS]


def _write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow(_normalize_row(row))


def _write_xlsx(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    if sheet is None:
        sheet = workbook.create_sheet("expenses")
    sheet.title = "expenses"
    sheet.append(list(COLUMNS))
    for row in rows:
        sheet.append(_normalize_row(row))
    workbook.save(path)
