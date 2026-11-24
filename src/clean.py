"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
import numpy as np
import pandas as pd

# Columns where the dictionary defines "NA" as "none" (structural absence), not "unknown".
NA_MEANS_NONE: list[str] = [
    "Alley", "Bsmt Qual", "Bsmt Cond", "Bsmt Exposure",
    "BsmtFin Type 1", "BsmtFin Type 2", "Fireplace Qu",
    "Garage Type", "Garage Finish", "Garage Qual", "Garage Cond",
    "Pool QC", "Fence", "Misc Feature",
]

NEIGHBORHOOD_NAMES = {
    "Blmngtn": "Bloomington Heights", "Blueste": "Bluestem",
    "BrDale": "Briardale", "BrkSide": "Brookside",
    "ClearCr": "Clear Creek", "CollgCr": "College Creek",
    "Crawfor": "Crawford", "Edwards": "Edwards",
    "Gilbert": "Gilbert", "Greens": "Greens",
    "GrnHill": "Green Hills", "IDOTRR": "Iowa DOT and Rail Road",
    "Landmrk": "Landmark", "MeadowV": "Meadow Village",
    "Mitchel": "Mitchell", "NAmes": "North Ames",
    "NoRidge": "Northridge", "NPkVill": "Northpark Villa",
    "NridgHt": "Northridge Heights", "NWAmes": "Northwest Ames",
    "OldTown": "Old Town", "SWISU": "South & West of Iowa State University",
    "Sawyer": "Sawyer", "SawyerW": "Sawyer West",
    "Somerst": "Somerset", "StoneBr": "Stone Brook",
    "Timber": "Timberland", "Veenker": "Veenker",
}


def load_raw(path: str) -> pd.DataFrame:
    """Load with keep_default_na=False so that 'NA' and 'None' survive as strings."""
    return pd.read_csv(path, sep="\t", keep_default_na=False, dtype=str)


def report_sentinels(raw_path: str, df_raw_str: pd.DataFrame) -> None:
    """Compare default pandas load vs keep_default_na=False for Part 3."""
    df_default = pd.read_csv(raw_path, sep="\t")
    print("=== PART 3: SENTINEL AUDIT ===")
    na_str_cols = [c for c in df_raw_str.columns if (df_raw_str[c] == "NA").any()]
    print(f"Columns containing literal 'NA' ({len(na_str_cols)}): {na_str_cols}")
    none_str_cols = [c for c in df_raw_str.columns if (df_raw_str[c] == "None").any()]
    print(f"Columns containing literal 'None' ({len(none_str_cols)}): {none_str_cols}")
    for c in none_str_cols:
        n_none = int((df_raw_str[c] == "None").sum())
        n_default_na = int(df_default[c].isna().sum())
        print(f"  {c}: {n_none} literal 'None' rows; default read_csv produced {n_default_na} NaNs")


def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Turn only true missing values into NaN, keep structural 'none', and fix documented raw errors."""
    out = df.copy()

    # 1. Structural absence: preserve 'NA' in NA_MEANS_NONE as 'Absent' (survives default read_csv)
    for col in NA_MEANS_NONE:
        out[col] = out[col].replace({"NA": "Absent", "": np.nan})

    # Preserve 'None' in Mas Vnr Type as 'NoVeneer' so default read_csv does not coerce it to NaN
    out["Mas Vnr Type"] = out["Mas Vnr Type"].replace({"None": "NoVeneer", "": np.nan, "NA": np.nan})

    # 2. All other columns: blank strings and 'NA' are true missing values
    other_cols = [c for c in out.columns if c not in NA_MEANS_NONE and c != "Mas Vnr Type"]
    for col in other_cols:
        out[col] = out[col].replace({"": np.nan, "NA": np.nan})

    # 3. Convert numeric columns to numeric dtypes
    from validate import EXPECTED_NUMERIC
    for col in EXPECTED_NUMERIC:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    # 4. Fix documented validation failures from Part 2
    # Category code discrepancies vs DataDocumentation.txt
    out["MS Zoning"] = out["MS Zoning"].replace({"A (agr)": "A", "C (all)": "C", "I (all)": "I"})
    out["Bldg Type"] = out["Bldg Type"].replace({"2fmCon": "2FmCon", "Duplex": "Duplx", "Twnhs": "TwnhsI"})

    # Garage Yr Blt typo (2207 -> NaN, unverified future year)
    out.loc[out["Garage Yr Blt"] > 2010, "Garage Yr Blt"] = np.nan

    # Cross-column fix: Year Remod/Add < Year Built -> set Year Remod/Add = Year Built
    remod_mask = out["Year Remod/Add"] < out["Year Built"]
    out.loc[remod_mask, "Year Remod/Add"] = out.loc[remod_mask, "Year Built"]

    # Cross-column fix: Year Built > Yr Sold (pre-construction sale) -> cap Year Built at Yr Sold
    built_mask = out["Year Built"] > out["Yr Sold"]
    out.loc[built_mask, "Year Built"] = out.loc[built_mask, "Yr Sold"]

    return out


def check_keys(df: pd.DataFrame) -> None:
    """Assert key uniqueness; print exact and key duplicate counts; run the many_to_one join."""
    print("=== PART 4: KEYS AND DUPLICATES ===")
    order_unique = df["Order"].is_unique
    pid_unique = df["PID"].is_unique
    exact_dups = int(df.duplicated().sum())
    order_dups = int(df["Order"].duplicated().sum())
    pid_dups = int(df["PID"].duplicated().sum())

    print(f"Order unique: {order_unique} (duplicates: {order_dups})")
    print(f"PID unique:   {pid_unique} (duplicates: {pid_dups})")
    print(f"Exact duplicate rows: {exact_dups}")
    assert order_unique, "Order is not unique!"
    assert pid_unique, "PID is not unique!"

    lookup = pd.DataFrame(
        list(NEIGHBORHOOD_NAMES.items()),
        columns=["Neighborhood", "Neighborhood_Full"],
    )
    merged = pd.merge(df, lookup, on="Neighborhood", how="left", validate="many_to_one")
    assert len(merged) == len(df), "Row count changed after many_to_one merge!"
    assert merged["Neighborhood_Full"].notna().all(), "Unmatched neighborhoods in lookup!"
    print(f"Neighborhood lookup join (many_to_one): {len(df)} -> {len(merged)} rows (0 unmatched)")


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    df_raw = load_raw(raw_path)
    report_sentinels(raw_path, df_raw)
    df_clean = decode_missing(df_raw)
    check_keys(df_clean)
    df_clean.to_csv(out_path, index=False)
    print(f"Saved cleaned dataset to {out_path} ({df_clean.shape[0]} rows, {df_clean.shape[1]} cols)")
