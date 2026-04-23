"""
Translate SSYK classification labels to English using Polars.

This script replaces Swedish SSYK codes/labels with English translations
from provided mapping files, preserving the original structure but
enriching specific columns.
"""

from pathlib import Path

import pandas as pd
import polars as pl

# Directory Setup
BASE_DIR = Path(__file__).resolve().parent
ORIGINAL_DIR = BASE_DIR / "01_original_data"
TRANSLATION_DIR = BASE_DIR / "02_translation_files"
OUTPUT_DIR = BASE_DIR / "03_translated_files"

# Taxonomy Configuration
# Level -> {sheet_name, digit_length, rows_to_skip}
LEVEL_SPECS = {
    "ssyk96": {
        1: {"sheet": "Level_1", "digits": 1, "skip": 0},
        2: {"sheet": "Level_2", "digits": 2, "skip": 0},
        3: {"sheet": "Level_3", "digits": 3, "skip": 0},
        4: {"sheet": "Level_4", "digits": 4, "skip": 0},
    },
    "ssyk2012": {
        1: {"sheet": "1-digit", "digits": 1, "skip": 3},
        2: {"sheet": "2-digit", "digits": 2, "skip": 3},
        3: {"sheet": "3-digit", "digits": 3, "skip": 3},
        4: {"sheet": "4-digit", "digits": 4, "skip": 3},
    },
}


def normalize_code_expr(col: str, digits: int) -> pl.Expr:
    """
    Polars expression to normalize SSYK codes.

    Extracts the leading numeric portion, strips whitespace, and zero-pads
    to the required length.
    """
    return (
        pl.col(col)
        .cast(pl.String)
        .str.strip_chars()
        .str.extract(r"^(\d+)", 1)
        .str.zfill(digits)
    )


def load_translation_map(taxonomy: str) -> dict[int, dict[str, str]]:
    """
    Load all levels of translation for a given taxonomy.

    Returns a dictionary mapping level (1-4) to a lookup table (code -> "code Title").
    """
    map_path = TRANSLATION_DIR / f"{taxonomy}_en.xlsx"
    taxonomy_lookup = {}

    for level, spec in LEVEL_SPECS[taxonomy].items():
        # Polars read_excel requires extra dependencies (fastexcel/calamine).
        # We use pandas as a reliable intermediate since it's already in the environment.
        pdf = pd.read_excel(
            map_path,
            sheet_name=spec["sheet"],
            skiprows=spec["skip"],
            usecols=[0, 1],
            names=["code", "title"],
        )

        # Convert to Polars using dict to avoid pyarrow dependency
        df = (
            pl.DataFrame(pdf.to_dict(orient="list"))
            .drop_nulls()
            .with_columns(
                norm_code=normalize_code_expr("code", spec["digits"]),
            )
            .filter(pl.col("norm_code").is_not_null())
        )

        # Build the mapping dictionary: {norm_code: "norm_code Title"}
        lookup = {
            row["norm_code"]: f"{row['norm_code']} {row['title']}"
            for row in df.select(["norm_code", "title"]).to_dicts()
        }
        taxonomy_lookup[level] = lookup

    return taxonomy_lookup


def process_taxonomy(taxonomy: str) -> None:
    """Load, translate, and save data for a specific SSYK taxonomy using LazyFrames."""
    print(f"--- Translating {taxonomy.upper()} (Lazy Mode) ---")

    # Load original data
    input_path = ORIGINAL_DIR / f"daioe_{taxonomy}.xlsx"
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        return

    # Use pandas as intermediate for Excel reading, then convert to LazyFrame
    pdf_original = pd.read_excel(input_path)
    lf = pl.DataFrame(pdf_original.to_dict(orient="list")).lazy()

    # Load translations
    translation_maps = load_translation_map(taxonomy)

    # We'll keep track of the normalized columns to calculate stats at the end
    norm_cols = []

    # Build the lazy pipeline level by level
    for level in range(1, 5):
        col_name = f"{taxonomy}_{level}"
        if col_name not in lf.collect_schema().names():
            continue

        digits = LEVEL_SPECS[taxonomy][level]["digits"]
        mapping = translation_maps.get(level, {})
        norm_col_name = f"_norm_{level}"
        norm_cols.append((level, col_name, norm_col_name, mapping))

        # 1. Create a normalized version of the column for matching/stats
        # 2. Use replace_strict to swap normalized codes with "Code Title"
        lf = lf.with_columns(
            pl.Series(norm_col_name, [None], dtype=pl.String), # Placeholder for schema
        ).with_columns(
            **{norm_col_name: normalize_code_expr(col_name, digits)},
        ).with_columns(
            **{col_name: pl.col(norm_col_name).replace_strict(mapping, default=pl.col(col_name))},
        )

    # Collect the final result
    df = lf.collect()

    # Calculate and print match statistics using the collected data
    for level, _col_name, norm_col_name, mapping in norm_cols:
        total_with_code = df.filter(pl.col(norm_col_name).is_not_null()).height
        match_keys = list(mapping.keys())
        matched_count = df.filter(pl.col(norm_col_name).is_in(match_keys)).height

        missing = total_with_code - matched_count
        print(f"  Level {level}: Matched {matched_count:4} / {total_with_code:4} (Missing: {missing})")

    # Clean up temporary normalization columns and save
    temp_cols = [nc[2] for nc in norm_cols]
    df = df.drop(temp_cols)

    # Save enriched data
    output_path = OUTPUT_DIR / f"daioe_{taxonomy}_translated.csv"
    df.write_csv(output_path)
    print(f"Result saved to: {output_path}\n")


def main() -> None:
    """Main entry point."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    process_taxonomy("ssyk96")
    process_taxonomy("ssyk2012")


if __name__ == "__main__":
    main()
