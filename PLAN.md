# BOM Auto-Populator GUI - Implementation Plan

## Context
The existing CLI-based BOM population tool (`populate_bom_advanced_FIXED.py`) worked but required editing hardcoded file paths each time. The project was refactored into a modern dark-themed GUI that supports multiple input formats, multiple distributor APIs, configurable purchasing settings, and names outputs based on a user-provided BOM name.

## File Structure

```
Automate-BOM/
├── main.py                          # Entry point
├── gui/
│   ├── __init__.py
│   ├── app.py                       # Main CTk window, thread mgmt, queue polling
│   └── frames/
│       ├── __init__.py
│       ├── input_frame.py           # BOM name, file browser, mode/distributor selectors, date
│       ├── settings_frame.py        # API credentials dialog with test buttons
│       ├── qty_settings_frame.py    # QTY TO BUY settings per component category
│       └── progress_frame.py        # Log textbox, progress bar, stats
├── core/
│   ├── __init__.py
│   ├── digikey_api.py               # DigiKeyAPI class (OAuth2, API v4)
│   ├── mouser_api.py                # MouserAPI class (API key)
│   ├── newark_api.py                # NewarkAPI class (API key, element14)
│   ├── bom_populator.py             # BOMPopulator class with multi-distributor support
│   ├── bom_builder.py               # Creates 20-column BOM workbook from scratch
│   ├── config.py                    # Load/save config.json (credentials + QTY settings)
│   └── importers/
│       ├── __init__.py
│       ├── excel_importer.py        # Validates existing BOM Excel files
│       ├── altium_importer.py       # Parses Altium BOM exports (fuzzy column matching)
│       └── csv_importer.py          # Parses CSV/Excel part number lists
├── config.json                      # API credentials + QTY settings (gitignored)
├── build.py                         # PyInstaller build script for standalone .exe
├── .gitignore
└── requirements.txt
```

## Implementation Phases

### Phase 1: Extract & Refactor Core Modules (Complete)
1. `core/config.py` - JSON read/write for credentials and QTY settings
2. `core/digikey_api.py` - DigiKeyAPI class with OAuth2, retry logic, `log_callback`
3. `core/bom_populator.py` - BOMPopulator with:
   - `log_callback` and `progress_callback` for GUI updates
   - `threading.Event` cancel support
   - Accept pre-built `Workbook` object (for CSV/Altium modes)
   - `bom_name` param for title and output filename

### Phase 2: Importers & BOM Builder (Complete)
4. `core/importers/excel_importer.py` - Validate .xlsx files
5. `core/bom_builder.py` - Build 20-column workbook from list of part dicts
   - Rows 1-2: Merged B1:U2 with BOM name
   - Row 3: All 20 headers
   - Row 4: Empty (spacer)
   - Row 5+: Data rows with formulas
6. `core/importers/csv_importer.py` - Parse CSV/Excel part number lists
7. `core/importers/altium_importer.py` - Map Altium columns to BOM format (fuzzy header matching)

### Phase 3: GUI (CustomTkinter, Dark Theme) (Complete)
8. `gui/app.py` - Main window (~850x700), dark mode, queue polling every 100ms
9. `gui/frames/input_frame.py`:
   - BOM Name text field
   - Auto-populated date label
   - Input Mode segmented button: "Excel BOM" / "Altium BOM" / "Part Number List"
   - Distributor dropdown: single or priority modes
   - Number of Boards field
   - File browser (filter changes per mode)
   - API Settings and QTY Settings buttons
10. `gui/frames/settings_frame.py` - CTkToplevel dialog for credentials + Test buttons per distributor
11. `gui/frames/qty_settings_frame.py` - CTkToplevel dialog for per-category QTY TO BUY settings
12. `gui/frames/progress_frame.py` - Progress bar, status label, stats counters, scrollable log
13. `main.py` - Entry point
14. Wire: Run button -> correct importer -> bom_builder if needed -> populator in background thread

### Phase 4: Multi-Distributor Support (Complete)
15. `core/mouser_api.py` - Mouser API integration (API key, search, price breaks)
16. `core/newark_api.py` - Newark/element14 API integration (API key, attributes parsing)
17. Distributor priority modes: DigiKey 1st, Mouser 1st, Newark 1st (fallback chain)
18. Detail supplementing: fill missing temperature/footprint/value from secondary distributors
19. Cart export: Generate DigiKey, Mouser, or Newark cart CSVs

### Phase 5: Intelligent Purchasing (Complete)
20. Configurable QTY TO BUY per component category (Resistors, Capacitors, Ferrite Beads, Inductors)
21. Per-category settings: enabled, step size, max qty, max budget
22. Global overhead percentage (default 10%)
23. Price break optimization at calculated buy quantity
24. QTY Settings dialog for GUI configuration

### Phase 6: Polish & Distribution (Complete)
25. `.gitignore`, `requirements.txt`
26. `build.py` - PyInstaller build script for standalone Windows .exe
27. `README.md` - Comprehensive project documentation
28. `GETTING_STARTED.md` - Step-by-step user guide
29. Git init, push to GitHub

## Key Design Decisions

- **CustomTkinter** for modern dark GUI, lightweight install
- **Thread + Queue pattern** for responsive UI during API calls
- **Reuse existing DigiKeyAPI/BOMPopulator logic** - add callbacks, don't rewrite
- **Output filename** derived from BOM Name field (sanitized for Windows)
- **Same 20-column format** for all input modes (CSV gets full BOM structure)
- **Altium importer** uses fuzzy column matching to handle export variations
- **Cancel support** via threading.Event checked each row iteration
- **Multi-distributor priority** - primary, secondary, tertiary fallback chain
- **Detail supplementing** - fills gaps from other distributors automatically
- **Configurable QTY settings** - per-category purchasing rules stored in config.json

## Verification
1. Run with existing Excel BOM - should produce fully formatted output
2. Run with Altium BOM export - should parse and create full 20-column BOM
3. Run with a CSV of part numbers - should create full BOM structure
4. Test all three distributor modes (single + priority)
5. Test settings save/load cycle (API credentials + QTY settings)
6. Test cancel mid-run
7. Test cart export for each distributor
8. Verify .gitignore excludes config.json, *.xlsx, *.log, *_Cart.csv
9. Build standalone .exe with build.py
