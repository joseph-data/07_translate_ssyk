# SSYK Translation Utility

<p align="left">
  <img src="logos/lab.svg" alt="AI-Econ Lab logo" width="200" height="">
</p>

This repository contains the script and lookup files used to translate Swedish
SSYK occupation classification labels in DAIOE data into English.

The utility supports both SSYK 96 and SSYK 2012. It reads the original Excel
workbooks, matches SSYK codes at levels 1-4 against English translation tables,
and writes translated CSV files.

## Repository Structure

```text
.
├── 01_original_data/
│   ├── daioe_ssyk96.xlsx
│   └── daioe_ssyk2012.xlsx
├── 02_translation_files/
│   ├── ssyk96_en.xlsx
│   └── ssyk2012_en.xlsx
├── 03_translated_files/
│   ├── daioe_ssyk96_translated.csv
│   └── daioe_ssyk2012_translated.csv
├── translation.py
├── pyproject.toml
└── uv.lock
```

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management

Project dependencies are managed in `pyproject.toml` and `uv.lock`.

## Usage

Install dependencies:

```bash
uv sync
```

Run the translation script:

```bash
uv run python translation.py
```

Translated outputs are written to:

- `03_translated_files/daioe_ssyk96_translated.csv`
- `03_translated_files/daioe_ssyk2012_translated.csv`

The script also prints match statistics for each SSYK level so unmatched codes
can be checked after running.

## Input Files

The script expects the original DAIOE Excel files to be stored in
`01_original_data/`:

- `daioe_ssyk96.xlsx`
- `daioe_ssyk2012.xlsx`

It expects English SSYK translation lookup workbooks in
`02_translation_files/`:

- `ssyk96_en.xlsx`
- `ssyk2012_en.xlsx`

## Translation Behavior

For each taxonomy, the script processes SSYK columns named by taxonomy and
level:

- `ssyk96_1`, `ssyk96_2`, `ssyk96_3`, `ssyk96_4`
- `ssyk2012_1`, `ssyk2012_2`, `ssyk2012_3`, `ssyk2012_4`

Each value is normalized by extracting the leading numeric code, trimming
whitespace, and zero-padding it to the expected level length. When a matching
English title is found, the original cell is replaced with:

```text
{code} {English title}
```

If no matching translation is found, the original value is preserved. This keeps
the data complete while still enriching all matched SSYK labels.

## Translation Sources

- SSYK 2012: [Statistics Sweden SSYK documentation](https://www.scb.se/dokumentation/klassifikationer-och-standarder/standard-for-svensk-yrkesklassificering-ssyk/)
- SSYK 96: [Statistics Sweden archive PDF](https://share.scb.se/ov9993/data/publikationer/statistik/_publikationer/ov9999_1998a01_br_x70%C3%B6p9803.pdf)

## Notes

- Existing files in `03_translated_files/` are overwritten when the script is
  run.
- Missing input files are reported in the terminal and skipped.
- Temporary normalization columns are used internally and are not included in
  the final CSV outputs.
