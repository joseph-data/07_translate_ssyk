# SSYK Translation Helper Utility

## Introduction

This repository provides utility tools for translating SSYK 2012 and SSYK 96 occupation titles into English, using the DAIOE indices published at [this Github Link](https://github.com/joseph-data/daioe_dataset/tree/v1.0.0).

Use this when English Occupation titles are preferred.

## Source files 

The translation files contained in `02_translation_files` are obtained from 

 1. `ssyk2012_en.xlsx` ➡️ [SCB](https://www.scb.se/dokumentation/klassifikationer-och-standarder/standard-for-svensk-yrkesklassificering-ssyk/)

 2. `ssyk96_en.xlsx` [SCB](https://share.scb.se/ov9993/data/publikationer/statistik/_publikationer/ov9999_1998a01_br_x70%C3%B6p9803.pdf) extracted via AI PDF→Excel conversion and then manually verified for codes and titles; spot-check if you need absolute accuracy (current data version: all codes matched).

## What is in the repository?

- Two translated CSVs in `03_translated_files/` for SSYK96 and SSYK2012.
- A per-level coverage report printed to the console showing how many codes translated and any unmatched codes (with the bundled data, all levels currently report full matches).
- Original column names preserved; values become `"<code> <english title>"` when a match is found, otherwise the original cell is left untouched.


## How to use the helper?

### Prerequisites

- Python 3.14+ (aligned with `pyproject.toml` / `uv.lock`)
- `uv` (recommended) or `pip`
- The bundled Excel files in (already included here; keep names/paths unchanged if you replace them):
  - `01_original_data/daioe_ssyk96.xlsx`
  - `01_original_data/daioe_ssyk2012.xlsx`
  - `02_translation_files/ssyk96_en.xlsx`
  - `02_translation_files/ssyk2012_en.xlsx`

## Quick start

Using `uv` (recommended):
```bash
uv venv .venv
source .venv/bin/activate
uv sync
python translation.py
```

Using `pip`:
```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas openpyxl pathlib
python translation.py
```

Sample output:
```
SSYK96 translation:
  Level 1: translated 9 / 9 (missing 0) | all codes matched
  ...
Wrote: 03_translated_files/daioe_ssyk96_translated.csv
SSYK2012 translation:
  Level 1: translated 9 / 9 (missing 0) | all codes matched
  ...
Wrote: 03_translated_files/daioe_ssyk2012_translated.csv
```

## Project layout

- `translation.py`: main script; loads inputs, applies translations per level, writes outputs and coverage stats.
- `01_original_data/`: source Excel workbooks to be translated.
- `02_translation_files/`: lookup tables with English titles.
- `03_translated_files/`: generated CSVs, created on run (existing files are overwritten).
- `pyproject.toml`: project metadata and dependency declarations.
- `uv.lock`: pinned dependency lock file for reproducible `uv` installs.

## How it works

- Each SSYK level column (`ssyk96_1`..`ssyk96_4`, `ssyk2012_1`..`ssyk2012_4`) is scanned, numeric codes are normalized, and matched against the translation tables.
- When a match exists, the cell is replaced with `code + space + English title`; blanks or unknown codes stay as-is so downstream processing can decide what to do.

## Tips

- If you update any Excel sources, re-run `translation.py` to regenerate the CSVs.
- To translate refreshed source data, swap in new Excel files with the same filenames/structure in `01_original_data/` and `02_translation_files/`, then run `translation.py`.
- To inspect unmatched codes, read the console output or open the CSVs and filter for cells without a space after the code.
