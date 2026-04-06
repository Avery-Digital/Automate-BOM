# BOM Auto-Populator GUI - Implementation Plan

## Context
The existing CLI-based BOM population tool (`populate_bom_advanced_FIXED.py`) works well but requires editing hardcoded file paths each time. The user needs a modern dark-themed GUI that supports multiple input formats (existing Excel BOM, Altium exports, CSV part lists), saves DigiKey credentials to a config file, and names outputs based on a user-provided BOM name.

## File Structure

```
Automate BOM/
├── main.py                          # Entry point
├── gui/
│   ├── __init__.py
│   ├── app.py                       # Main CTk window, thread mgmt, queue polling
│   └── frames/
│       ├── __init__.py
│       ├── input_frame.py           # BOM name, file browser, mode selector, date
│       ├── settings_frame.py        # DigiKey credentials dialog
│       └── progress_frame.py        # Log textbox, progress bar, stats
├── core/
│   ├── __init__.py
│   ├── digikey_api.py               # DigiKeyAPI class (extracted from existing)
│   ├── bom_populator.py             # BOMPopulator class (refactored)
│   ├── bom_builder.py               # Creates 22-column BOM workbook from scratch
│   ├── config.py                    # Load/save config.json
│   └── importers/
│       ├── __init__.py
│       ├── excel_importer.py        # Validates existing BOM Excel files
│       ├── altium_importer.py       # Parses Altium BOM exports
│       └── csv_importer.py          # Parses CSV part number lists
├── config.json                      # DigiKey credentials (gitignored)
├── .gitignore
└── requirements.txt
```

## Implementation Phases

### Phase 1: Extract & Refactor Core Modules
1. `core/config.py` - JSON read/write for credentials
2. `core/digikey_api.py` - Extract DigiKeyAPI class from existing script, add `log_callback` param
3. `core/bom_populator.py` - Extract BOMPopulator, add:
   - `log_callback` and `progress_callback` for GUI updates
   - `threading.Event` cancel support
   - Accept pre-built `Workbook` object (for CSV/Altium modes)
   - `bom_name` param for rows 1-2 title and output filename
4. Verify refactored modules work identically to original

### Phase 2: Importers & BOM Builder
5. `core/importers/excel_importer.py` - Validate .xlsx files
6. `core/bom_builder.py` - Build 22-column workbook from list of part dicts
   - Rows 1-2: Merged B1:V2 with BOM name
   - Row 3: All 22 headers
   - Row 4: Empty
   - Row 5+: Data rows
7. `core/importers/csv_importer.py` - Parse single-column MPN CSV
8. `core/importers/altium_importer.py` - Map Altium columns to BOM format (fuzzy header matching)

### Phase 3: GUI (CustomTkinter, Dark Theme)
9. `gui/app.py` - Main window (~800x700), dark mode, queue polling every 100ms
10. `gui/frames/input_frame.py`:
    - BOM Name text field
    - Auto-populated date label
    - Input Mode selector: "Excel BOM" / "Altium BOM" / "CSV Part List"
    - File browser (filter changes per mode)
    - Settings button
11. `gui/frames/settings_frame.py` - CTkToplevel dialog for credentials + Test Connection
12. `gui/frames/progress_frame.py` - Progress bar, status label, stats counters, scrollable log
13. `main.py` - Entry point
14. Wire: Run button -> correct importer -> bom_builder if needed -> populator in background thread

### Phase 4: Polish & Repo
15. `.gitignore`, `requirements.txt`
16. Git init, initial commit, push to GitHub
17. Remove hardcoded credentials from old script before committing

## Key Design Decisions

- **CustomTkinter** for modern dark GUI, lightweight install
- **Thread + Queue pattern** for responsive UI during API calls
- **Reuse existing DigiKeyAPI/BOMPopulator logic** - add callbacks, don't rewrite
- **Output filename** derived from BOM Name field (sanitized for Windows)
- **Same 22-column format** for all input modes (CSV gets full BOM structure)
- **Altium importer** uses fuzzy column matching to handle export variations
- **Cancel support** via threading.Event checked each row iteration

## Verification
1. Run with existing Excel BOM (e.g., Motherboard Panel Connectors.xlsx) - should produce identical output
2. Run with a CSV of part numbers - should create full 22-column BOM
3. Test settings save/load cycle
4. Test cancel mid-run
5. Verify .gitignore excludes config.json, *.xlsx, *.log
