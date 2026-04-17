# Getting Started with BOM Auto-Populator

This guide will get you up and running with the BOM Auto-Populator in under 10 minutes.

## Option A: Run the Standalone Application (No Python Required)

If you received the BOM Auto-Populator as a `.zip` file or installer:

1. **Extract** the zip file to any location (e.g., `C:\BOM-Auto-Populator\`)
2. **Run** `BOM_Auto_Populator.exe`
3. Skip to [First-Time Setup](#first-time-setup) below

## Option B: Run from Source (Developer Setup)

### Prerequisites

- Python 3.10 or newer: https://www.python.org/downloads/
- Git (optional): https://git-scm.com/downloads

### Install

```bash
git clone https://github.com/Avery-Digital/Automate-BOM.git
cd Automate-BOM
pip install -r requirements.txt
```

### Launch

```bash
python main.py
```

---

## First-Time Setup

When you launch the app for the first time, you need to configure your distributor API keys.

### Step 1: Get Your API Keys

You need at least one distributor API key. All three are free.

**DigiKey** (recommended):
1. Go to https://developer.digikey.com/
2. Create an account and register a new app
3. Select "Product Information" API
4. Choose "Client Credentials" as the OAuth type
5. Copy your **Client ID** and **Client Secret**

**Mouser:**
1. Go to https://www.mouser.com/api-hub/
2. Sign in or create an account
3. Register for the **Search API**
4. Copy your **API Key**

**Newark:**
1. Go to https://partner.element14.com/member/register
2. Register with your Newark/element14 account
3. Go to My Account > Account Summary > Register for API Key
4. Copy your **API Key**

### Step 2: Enter Credentials in the App

1. Click the **API Settings** button in the top-right of the app
2. Enter your API credentials for each distributor
3. Click **Test DigiKey**, **Test Mouser**, or **Test Newark** to verify each works
4. Click **Save** — credentials are stored locally and persist between sessions

---

## Running Your First BOM

### Step 1: Enter BOM Details

- **BOM Name**: Enter a name for your BOM (e.g., "DMF Control Board Rev2"). This becomes the title in the output spreadsheet and the output filename.
- **Date**: Auto-filled with today's date.

### Step 2: Choose a Distributor Mode

| Mode | Behavior |
|------|----------|
| **DigiKey** | Search DigiKey only |
| **Mouser** | Search Mouser only |
| **Newark** | Search Newark only |
| **DigiKey 1st** | Search DigiKey first. If a part is unavailable, try Mouser, then Newark |
| **Mouser 1st** | Search Mouser first. If unavailable, try DigiKey, then Newark |
| **Newark 1st** | Search Newark first. If unavailable, try Mouser, then DigiKey |

The "1st" modes are recommended - they find the best availability across all distributors.

### Step 3: Configure QTY Settings (Optional)

Click **QTY Settings** to customize bulk buying rules:
- **Overhead %**: Extra percentage added above the needed quantity (default 10%)
- **Per-category settings** (Resistors, Capacitors, Ferrite Beads, Inductors):
  - Enable/disable bulk buying for each category
  - Step size (e.g., buy in increments of 50 for resistors)
  - Max quantity (e.g., never buy more than 1,000)
  - Max budget (e.g., never spend more than $25 on extras)

These settings persist between sessions.

### Step 4: Set Number of Boards

Enter the number of boards you plan to build. Defaults to 1. This multiplies with the quantity-per-board to calculate total quantities.

### Step 5: Select Input Mode and File

| Input Mode | Use When | File Type |
|------------|----------|-----------|
| **Excel BOM** | You have an existing BOM spreadsheet with Mfr. P/N column | `.xlsx` |
| **Altium BOM** | You exported a BOM from Altium Designer | `.csv` or `.xlsx` |
| **Part Number List** | You have a simple list of manufacturer part numbers | `.csv` or `.xlsx` |

Click **Browse** to select your file.

### Step 6: Run

Click **Run**. The progress area will show real-time status for each part lookup. You can click **Cancel** at any time to stop.

### Step 7: Review Output

The output file is saved in the same directory as the app, named `<BOM Name>_Populated.xlsx`.

**Row colors:**
- **Green**: Found by your primary distributor
- **Light Blue**: Found by the secondary (fallback) distributor
- **Light Purple**: Found by the tertiary distributor
- **Red**: Not found, out of stock, or marked DNI (Do Not Install)

### Step 8: Export Cart (Optional)

After a successful run, three export buttons become active:

- **Export DigiKey Cart** - Creates a CSV for DigiKey BOM Manager
- **Export Mouser Cart** - Creates a CSV for Mouser BOM Tool
- **Export Newark Cart** - Creates a CSV for Newark BOM Tool

Each export only includes parts sourced from that specific distributor and excludes out-of-stock items. Upload the CSV to the distributor's website to auto-fill your shopping cart.

---

## Input File Formats

### Excel BOM

A standard `.xlsx` file with a header row containing at minimum a "Mfr. P/N" column. The tool auto-detects all other columns. This is the format used in the included `BOM_Template.xlsx`.

Example:
```
| Item | Designator | Description | Mfr. P/N        | Quantity Per Board |
|------|------------|-------------|------------------|--------------------|
| 1    | R1, R2     |             | CRCW080510K0FKEA | 2                  |
| 2    | C1, C2, C3 |             | KGM21NR71H104KT  | 3                  |
| 3    | U1         |             | STM32H735IGT6    | 1                  |
```

### Altium BOM

Exported from Altium Designer. The tool expects these columns (order doesn't matter):
- **Designator** - Component references
- **Description** - Part description
- **MFR PN** - Manufacturer part number
- **Quantity** - Number of parts
- **Value** - Component value (optional)
- **Comment** - Altium comment field (optional)

### Part Number List

The simplest format - just a list of manufacturer part numbers:

```
CRCW080510K0FKEA
KGM21NR71H104KT
STM32H735IGT6
DAC80508ZRTER
```

Or with headers and quantities:

```
MFR PN, Quantity
CRCW080510K0FKEA, 24
KGM21NR71H104KT, 48
STM32H735IGT6, 1
```

---

## Understanding the Output

### Column Reference

| Column | Description | Auto-Populated? |
|--------|-------------|-----------------|
| Item | Sequential line number | Yes |
| Designator | Component references (e.g., R1, R2) | From input file |
| Description | Part description | Yes (from distributor) |
| Temperature | Operating temperature range | Yes (DigiKey/Newark) |
| Value | Component value (10K, 0.1uF, etc.) | Yes (DigiKey/Newark) |
| Mfr. | Manufacturer name | Yes |
| Mfr. P/N | Manufacturer part number | From input file |
| Quantity Per Board | Parts needed per board | From input file |
| Number of Boards | Boards to build | From GUI input |
| Quantity Total | Qty Per Board x Num Boards | Formula |
| Distributor | Which distributor was used | Yes |
| Dist. P/N | Distributor's part number (clickable link) | Yes |
| Price Ea | Unit price (adjusted for bulk qty) | Yes |
| Price Total Per Board | Qty Total x Price Ea | Formula |
| Available | Current in-stock quantity | Yes |
| QTY TO BUY | Recommended purchase quantity | Yes (calculated) |
| Total Buy | QTY TO BUY x Price Ea | Formula |
| Date Updated | Date the BOM was populated | Yes |
| Foot Print | Package/footprint (e.g., 0805) | Yes (DigiKey/Newark) |
| Notes | DNI status, availability notes | Yes |

### QTY TO BUY Logic

The tool intelligently calculates how many parts to order. All settings are configurable via the **QTY Settings** button in the GUI.

- **Resistors**: Buys in steps of 50 (default) up to 1,000 pieces, as long as the total stays under $25. This takes advantage of price breaks on cheap passives.
- **Capacitors & Ferrite Beads**: Same logic but in steps of 5 (default).
- **Inductors**: Same logic as capacitors — steps of 5 (default), max 1,000 qty, $25 budget.
- **All other parts**: Quantity Total + overhead % (default 10%, rounded up) as a safety margin.
- If the minimum needed already costs more than the budget limit, it just buys the minimum + overhead %.

Each category can be individually enabled/disabled, and step size, max quantity, and max budget are all configurable per category. Click **QTY Settings** to customize.

The **Price Ea** column is updated to reflect the price break at the quantity being purchased.

### DNI (Do Not Install) Parts

If a part has "DNI" in the Notes column, it will be:
- Highlighted red
- Skipped from distributor lookups (saves time and API calls)
- Left in the BOM for reference

---

## BOM Template

A blank `BOM_Template.xlsx` is included with:
- 100 pre-formatted rows with formulas
- All column headers
- Number of Boards defaulted to 1
- Quantity Total, Price Total, and Total Buy formulas pre-built
- SUM totals at the bottom

Distribute this template to team members who need to create BOMs manually.

---

## Tips

- **DigiKey 1st mode** is best for getting complete data (temperature, footprint, value) since DigiKey's API is the most detailed.
- **Mouser 1st mode** is useful when Mouser is your preferred vendor. Missing detail data (temp, footprint) will be automatically fetched from DigiKey or Newark.
- Use the **Part Number List** mode for quick lookups when you just have a list of part numbers.
- The tool handles part number format variations (dashes, leading zeros) automatically.
- Check the log output for any parts that weren't found — you may need to verify the part number.
- Adjust **QTY Settings** to match your purchasing habits. For example, increase resistor step size to 100 if you prefer buying in larger increments, or lower the budget cap for tighter cost control.
- DigiKey's API can be slow for certain parts (30+ seconds). This is a DigiKey server-side issue, not a tool problem.

---

## Troubleshooting

**"Authentication failed"**: Check your API credentials in Settings. Use the Test buttons to verify.

**Parts not found**: The part number may differ from how the distributor lists it. Check the distributor's website manually. The tool handles common variations (dashes, leading zeros) but some parts may need the exact format.

**Slow processing**: Some DigiKey searches take 10-30 seconds per part. This is normal for certain part numbers. The tool will continue processing.

**Missing temperature/footprint**: Mouser's API doesn't provide detailed specs. Use a "1st" mode (DigiKey 1st or Newark 1st) to get complete data, or the tool will supplement automatically.

**Rate limiting**: Mouser allows 30 requests/minute. For large BOMs (45+ parts), you may briefly hit the limit. The tool automatically waits and retries.
