# BOM Auto-Populator

A desktop GUI tool that automates Bill of Materials (BOM) population by looking up manufacturer part numbers across DigiKey, Mouser, and Newark APIs. It retrieves pricing, stock availability, descriptions, temperature ratings, footprints, and component values, then outputs a fully formatted Excel BOM.

## Features

- **Dark-themed GUI** built with CustomTkinter
- **Three input modes:**
  - **Excel BOM** - Existing Excel BOM with Mfr. P/N column
  - **Altium BOM** - CSV or Excel exported from Altium Designer
  - **Part Number List** - Simple list of manufacturer part numbers (CSV or Excel)
- **Three distributor APIs:**
  - DigiKey (OAuth2, API v4)
  - Mouser (API key)
  - Newark/element14 (API key)
- **Distributor priority modes:** DigiKey 1st, Mouser 1st, Newark 1st - searches primary distributor first, falls back to others if unavailable
- **Detail supplementing** - If the primary distributor (e.g., Mouser) doesn't return temperature/footprint/value data, automatically fetches it from DigiKey or Newark
- **Smart part matching** - Normalized matching strips dashes, spaces, and leading zeros for flexible part number matching
- **DigiKey packaging hierarchy** - Prefers Cut Tape > Tape & Reel > Digi-Reel
- **Configurable QTY TO BUY calculation** with per-category settings via the QTY Settings dialog:
  - All parts: minimum needed + configurable overhead % (default 10%)
  - Resistors: bulk buy in configurable steps (default 50), max qty and budget limits
  - Capacitors & Ferrite Beads: bulk buy in configurable steps (default 5), max qty and budget limits
  - Inductors: bulk buy in configurable steps (default 5), max qty and budget limits
  - Each category can be individually enabled/disabled with custom step size, max quantity, and max budget
  - Price Ea updated with the price break for the quantity purchased
- **Excel output formatting:**
  - Green rows: found by primary distributor
  - Light blue rows: found by secondary (fallback) distributor
  - Light purple rows: found by tertiary distributor
  - Red rows: not found, 0 available, or DNI (Do Not Install)
  - Borders on all cells, Arial 10pt, currency formatting, hyperlinks to distributor pages
- **Excel formulas (per row):**
  - Quantity Total = Qty Per Board x Number of Boards
  - Price Total Per Board = Quantity Total x Price Ea
  - Total Buy = QTY TO BUY x Price Ea
  - SUM totals for Price Total Per Board and Total Buy
- **DNI handling** - Parts with "DNI" in the Notes column are highlighted red and skipped from API lookups
- **Cart export** - Export DigiKey, Mouser, or Newark cart CSVs for upload to each distributor's BOM manager. Filters by distributor and skips 0-available items.
- **BOM title** - Auto-populated with BOM name and current date (e.g., "My BOM, April 08, 2026")
- **Cancel support** - Stop a running BOM population at any time
- **Progress logging** - Real-time log output with per-part status, saved to timestamped log files

## Installation

### Requirements

- Python 3.10+
- Windows (tested on Windows 11)

### Setup

```bash
git clone https://github.com/Avery-Digital/Automate-BOM.git
cd Automate-BOM
pip install -r requirements.txt
```

### Dependencies

- `customtkinter` - Modern dark-themed GUI framework
- `openpyxl` - Excel file reading/writing
- `requests` - HTTP API calls

## Usage

### Launch the GUI

```bash
python main.py
```

### First-time setup

1. Click **API Settings** in the GUI
2. Enter your API credentials:
   - **DigiKey:** Client ID and Client Secret (from [DigiKey API](https://developer.digikey.com/))
   - **Mouser:** API Key (from [Mouser API Hub](https://www.mouser.com/api-hub/))
   - **Newark:** API Key (from [element14 Partner Portal](https://partner.element14.com/))
3. Click **Test** to verify each connection, then **Save**
4. Optionally click **QTY Settings** to customize bulk buying rules per component category (overhead %, step sizes, max quantities, budgets)

### Running a BOM

1. Enter a **BOM Name** (used for the title and output filename)
2. Select the **Input Mode** (Excel BOM, Altium BOM, or Part Number List)
3. Select the **Distributor** mode (single distributor or priority mode)
4. Optionally set **# of Boards** (defaults to 1)
5. **Browse** for your input file
6. Click **Run**
7. After completion, use **Export DigiKey/Mouser/Newark Cart** to generate cart CSVs

### Input file formats

**Excel BOM:** An `.xlsx` file with a header row containing "Mfr. P/N". The tool auto-detects columns.

**Altium BOM:** A `.csv` or `.xlsx` exported from Altium Designer. Expected columns: Designator, Description, MFR PN, Quantity, Value, Comment.

**Part Number List:** A `.csv` or `.xlsx` with manufacturer part numbers. Can be a single column of part numbers or include headers like "MFR PN" and "Quantity".

### Output

The tool generates `<BOM Name>_Populated.xlsx` with 20 columns:

| Column | Description |
|--------|-------------|
| Item | Sequential line item number |
| Designator | Component reference designators |
| Description | Part description (from distributor) |
| Temperature | Operating temperature range |
| Value | Component value (resistance, capacitance, inductance) |
| Mfr. | Manufacturer name |
| Mfr. P/N | Manufacturer part number |
| Quantity Per Board | Parts needed per board |
| Number of Boards | Number of boards to build |
| Quantity Total | Qty Per Board x Number of Boards (formula) |
| Distributor | DigiKey, Mouser, or Newark |
| Dist. P/N | Distributor part number (hyperlinked) |
| Price Ea | Unit price (adjusted for bulk buy quantity) |
| Price Total Per Board | Quantity Total x Price Ea (formula) |
| Available | Current in-stock quantity |
| QTY TO BUY | Calculated purchase quantity |
| Total Buy | QTY TO BUY x Price Ea (formula) |
| Date Updated | Date the BOM was populated |
| Foot Print | Package/footprint from distributor |
| Notes | DNI status and availability notes |

## BOM Template

A blank `BOM_Template.xlsx` is included with 100 pre-formatted rows, all formulas, and column headers. Distribute to team members for manual BOM entry.

## Project Structure

```
Automate-BOM/
├── main.py                      # Entry point
├── gui/
│   ├── app.py                   # Main application window
│   └── frames/
│       ├── input_frame.py       # Input controls
│       ├── settings_frame.py    # API credential management
│       ├── qty_settings_frame.py # QTY TO BUY settings dialog
│       └── progress_frame.py    # Progress display
├── core/
│   ├── digikey_api.py           # DigiKey API v4 wrapper
│   ├── mouser_api.py            # Mouser API wrapper
│   ├── newark_api.py            # Newark/element14 API wrapper
│   ├── bom_populator.py         # BOM population engine
│   ├── bom_builder.py           # Excel workbook builder
│   ├── config.py                # Credential and settings storage
│   └── importers/
│       ├── altium_importer.py   # Altium BOM parser
│       ├── csv_importer.py      # Part number list parser
│       └── excel_importer.py    # Excel BOM validator
├── config.json                  # API credentials and settings (gitignored)
├── BOM_Template.xlsx            # Blank BOM template
├── requirements.txt             # Python dependencies
├── build.py                     # PyInstaller build script
├── GETTING_STARTED.md           # User guide
└── .gitignore
```

## Building a Standalone Executable

To distribute the app without requiring Python:

```bash
pip install pyinstaller
python build.py
```

This creates `dist/BOM_Auto_Populator/` containing the standalone application. Zip and share that folder - users just extract and run `BOM_Auto_Populator.exe`.

See [GETTING_STARTED.md](GETTING_STARTED.md) for the full user guide.
