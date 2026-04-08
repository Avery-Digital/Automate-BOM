import os
import openpyxl


def validate_excel_bom(path: str) -> tuple:
    """Validate that the file is a valid Excel BOM with Mfr. P/N column.
    Returns (True, "") on success or (False, "error message") on failure.
    """
    if not os.path.exists(path):
        return False, f"File not found: {path}"

    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.xlsx', '.xls'):
        return False, f"Not an Excel file: {ext}"

    try:
        wb = openpyxl.load_workbook(path)
        ws = wb.active
    except Exception as e:
        return False, f"Cannot open file: {e}"

    # Look for Mfr. P/N header in first 10 rows
    for row_idx in range(1, 11):
        for cell in ws[row_idx]:
            val = str(cell.value).strip() if cell.value else ""
            if "Mfr" in val and "P/N" in val:
                return True, ""

    return False, "Could not find 'Mfr. P/N' column header in the first 10 rows"
