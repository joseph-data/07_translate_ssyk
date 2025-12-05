"""Translate SSYK classification labels to English and save enriched files."""

from pathlib import Path
import re

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ORIGINAL_DIR = BASE_DIR / "01_original_data"
TRANSLATION_DIR = BASE_DIR / "02_translation_files"
OUTPUT_DIR = BASE_DIR / "03_translated_files"

# Level -> (sheet name, code length)
LEVEL_SPECS = {
    "ssyk96": {1: ("Level_1", 1), 2: ("Level_2", 2), 3: ("Level_3", 3), 4: ("Level_4", 4)},
    "ssyk2012": {1: ("1-digit", 1), 2: ("2-digit", 2), 3: ("3-digit", 3), 4: ("4-digit", 4)},
}


def normalize_code(value, digits):
    """Extract numeric code prefix and zero-pad to the expected digit length."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    # Only consider the leading number chunk (before any text).
    match = re.match(r"^([0-9]+)", text)
    if not match:
        return None
    return match.group(1).zfill(digits)


def load_ssyk96_translations():
    """Load SSYK96 translations for all levels."""
    path = TRANSLATION_DIR / "ssyk96_en.xlsx"
    sheet_names = {1: "Level_1", 2: "Level_2", 3: "Level_3", 4: "Level_4"}
    mapping = {}
    for level, sheet in sheet_names.items():
        digits = LEVEL_SPECS["ssyk96"][level][1]
        df = pd.read_excel(path, sheet_name=sheet, usecols=[0, 1])
        df.columns = ["code", "occupation_title"]
        df = df.dropna(subset=["code", "occupation_title"])
        df["code"] = df["code"].apply(lambda v: normalize_code(v, digits))
        df = df.dropna(subset=["code"])
        mapping[level] = df.set_index("code")["occupation_title"].to_dict()
    return mapping


def load_ssyk2012_translations():
    """Load SSYK2012 translations for all levels."""
    path = TRANSLATION_DIR / "ssyk2012_en.xlsx"
    sheet_names = {1: "1-digit", 2: "2-digit", 3: "3-digit", 4: "4-digit"}
    mapping = {}
    for level, sheet in sheet_names.items():
        digits = LEVEL_SPECS["ssyk2012"][level][1]
        df = pd.read_excel(
            path, sheet_name=sheet, skiprows=3, names=["code", "occupation_title"], usecols=[0, 1]
        )
        df = df.dropna(subset=["code", "occupation_title"])
        df["code"] = df["code"].apply(lambda v: normalize_code(v, digits))
        df = df.dropna(subset=["code"])
        mapping[level] = df.set_index("code")["occupation_title"].to_dict()
    return mapping


def translate_dataframe(df, taxonomy, translation_map):
    """Replace SSYK level columns with English labels (same column names)."""
    df = df.copy()
    stats = {}
    for level in range(1, 5):
        col = f"{taxonomy}_{level}"
        if col not in df.columns:
            continue

        digits = LEVEL_SPECS[taxonomy][level][1]
        translated_col = []
        success = 0
        total_codes = 0
        unmatched_codes = set()

        for value in df[col]:
            code = normalize_code(value, digits)
            english = translation_map.get(level, {}).get(code)
            if code and english:
                translated_value = f"{code} {english}"
            else:
                # Keep original value if no translation to preserve data shape
                translated_value = value
            translated_col.append(translated_value)
            if code is not None:
                total_codes += 1
                if english is not None:
                    success += 1
                else:
                    unmatched_codes.add(code)

        df[col] = translated_col
        stats[level] = {
            "total_codes": total_codes,
            "translated": success,
            "missing": total_codes - success,
            "unmatched_codes": unmatched_codes,
        }

    return df, stats


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ssyk96_map = load_ssyk96_translations()
    df_96 = pd.read_excel(ORIGINAL_DIR / "daioe_ssyk96.xlsx")
    df_96, stats_96 = translate_dataframe(df_96, "ssyk96", ssyk96_map)
    out_96 = OUTPUT_DIR / "daioe_ssyk96_translated.csv"
    df_96.to_csv(out_96, index=False)
    print("SSYK96 translation:")
    for level, level_stats in sorted(stats_96.items()):
        missing = level_stats["missing"]
        unmatched = sorted(level_stats["unmatched_codes"])
        msg = (
            f"  Level {level}: translated {level_stats['translated']} / {level_stats['total_codes']} "
            f"(missing {missing})"
        )
        if missing:
            msg += f" | unmatched codes sample: {unmatched[:5]}"
        else:
            msg += " | all codes matched"
        print(msg)
    print(f"Wrote: {out_96}")

    ssyk2012_map = load_ssyk2012_translations()
    df_2012 = pd.read_excel(ORIGINAL_DIR / "daioe_ssyk2012.xlsx")
    df_2012, stats_2012 = translate_dataframe(df_2012, "ssyk2012", ssyk2012_map)
    out_2012 = OUTPUT_DIR / "daioe_ssyk2012_translated.csv"
    df_2012.to_csv(out_2012, index=False)
    print("SSYK2012 translation:")
    for level, level_stats in sorted(stats_2012.items()):
        missing = level_stats["missing"]
        unmatched = sorted(level_stats["unmatched_codes"])
        msg = (
            f"  Level {level}: translated {level_stats['translated']} / {level_stats['total_codes']} "
            f"(missing {missing})"
        )
        if missing:
            msg += f" | unmatched codes sample: {unmatched[:5]}"
        else:
            msg += " | all codes matched"
        print(msg)
    print(f"Wrote: {out_2012}")


if __name__ == "__main__":
    main()
