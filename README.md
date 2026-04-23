# SSYK Translation Utility

Utility for translating Swedish SSYK occupation titles (96 and 2012 versions) into English.

## Usage

1. **Setup**: Run `uv sync` to install required dependencies.
2. **Run**: Execute `python translation.py`.
3. **Results**: Translated CSV files will be generated in `03_translated_files/`.

## Folder Organization

- `01_original_data/`: Place your source Excel workbooks here.
- `02_translation_files/`: Contains the English title mappings for lookup.
- `03_translated_files/`: Output directory for the generated results.

## Behavior
The script processes SSYK columns across levels 1–4. When a code matches the mapping table, the cell is updated to `"{code} {English title}"`. If a match is not found, the original value is preserved to ensure no data is lost during processing.

## Data Sources
- **SSYK 2012**: [SCB Documentation](https://www.scb.se/dokumentation/klassifikationer-och-standarder/standard-for-svensk-yrkesklassificering-ssyk/)
- **SSYK 96**: [SCB Archive](https://share.scb.se/ov9993/data/publikationer/statistik/_publikationer/ov9999_1998a01_br_x70%C3%B6p9803.pdf)
