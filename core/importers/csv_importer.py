import csv
import os


def parse(file_path: str) -> list:
    """Parse a simple CSV of manufacturer part numbers.
    Handles single-column (just part numbers) or multi-column with headers.
    Returns list of part dicts for bom_builder.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext != '.csv':
        raise ValueError(f"Expected .csv file, got {ext}")

    parts = []

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = [r for r in reader if r and any(cell.strip() for cell in r)]

    if not rows:
        return parts

    # Detect if first row is a header
    first_row = rows[0]
    header_keywords = {'part', 'p/n', 'pn', 'mpn', 'mfr', 'manufacturer', 'quantity', 'qty', 'number'}
    first_lower = [cell.strip().lower() for cell in first_row]
    has_header = any(word in cell for cell in first_lower for word in header_keywords)

    if has_header:
        # Find part number and optional quantity columns
        pn_col = None
        qty_col = None
        for i, cell in enumerate(first_lower):
            if pn_col is None and any(kw in cell for kw in ('part', 'p/n', 'pn', 'mpn', 'mfr')):
                pn_col = i
            elif qty_col is None and any(kw in cell for kw in ('quantity', 'qty')):
                qty_col = i

        if pn_col is None:
            pn_col = 0

        for row in rows[1:]:
            if pn_col < len(row):
                pn = row[pn_col].strip()
                if pn:
                    part = {'mfr_pn': pn}
                    if qty_col is not None and qty_col < len(row):
                        qty = row[qty_col].strip()
                        if qty:
                            part['quantity'] = qty
                    parts.append(part)
    else:
        # No header - treat first column as part numbers
        for row in rows:
            pn = row[0].strip()
            if pn:
                part = {'mfr_pn': pn}
                if len(row) > 1 and row[1].strip():
                    # Second column might be quantity
                    try:
                        int(row[1].strip())
                        part['quantity'] = row[1].strip()
                    except ValueError:
                        pass
                parts.append(part)

    return parts
