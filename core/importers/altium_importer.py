import csv
import os


# Expected Altium BOM columns: Designator, Description, MFR PN, Quantity, Value, Comment
# Fuzzy matching for flexibility
COLUMN_MAP = {
    'designator': 'designator',
    'description': 'description',
    'mfr pn': 'mfr_pn',
    'mfr. pn': 'mfr_pn',
    'mfr p/n': 'mfr_pn',
    'manufacturer part number': 'mfr_pn',
    'manufacturer part no': 'mfr_pn',
    'mpn': 'mfr_pn',
    'quantity': 'quantity',
    'qty': 'quantity',
    'value': 'value',
    'comment': 'comment',
    'footprint': 'footprint',
    'pcb footprint': 'footprint',
}


def parse(file_path: str) -> list:
    """Parse an Altium BOM (CSV or Excel) into a list of part dicts for bom_builder."""
    ext = os.path.splitext(file_path)[1].lower()

    parts = []

    if ext in ('.xlsx', '.xls'):
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([str(cell) if cell is not None else '' for cell in row])
    elif ext == '.csv':
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .csv or .xlsx")

    if not rows:
        return parts

    # Find header row (first row with recognizable column names)
    header_row_idx = None
    header_map = {}

    for idx, row in enumerate(rows):
        matched = 0
        temp_map = {}
        for col_idx, cell in enumerate(row):
            cell_lower = cell.strip().lower()
            if cell_lower in COLUMN_MAP:
                temp_map[COLUMN_MAP[cell_lower]] = col_idx
                matched += 1
        if matched >= 2:
            header_row_idx = idx
            header_map = temp_map
            break

    if header_row_idx is None:
        raise ValueError("Could not find recognizable headers in the CSV. "
                         "Expected columns like: Designator, Description, MFR PN, Quantity, Value, Comment")

    # Parse data rows
    for row in rows[header_row_idx + 1:]:
        if not row or all(not cell.strip() for cell in row):
            continue

        part = {}
        for field, col_idx in header_map.items():
            if col_idx < len(row):
                val = row[col_idx].strip()
                if val:
                    part[field] = val

        # Skip if no MFR PN
        if not part.get('mfr_pn'):
            continue

        parts.append(part)

    return parts
