"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
from pathlib import Path
import pandas as pd


def compare_groups(df: pd.DataFrame, col: str, observed_cols: list[str]) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""
    is_missing = df[col].isna()
    rows = []
    for obs in observed_cols:
        if pd.api.types.is_numeric_dtype(df[obs]):
            rows.append({
                "column": obs,
                "type": "numeric",
                "mean_present": round(df.loc[~is_missing, obs].mean(), 2),
                "mean_missing": round(df.loc[is_missing, obs].mean(), 2),
                "median_present": round(df.loc[~is_missing, obs].median(), 2),
                "median_missing": round(df.loc[is_missing, obs].median(), 2),
            })
        else:
            top_present = df.loc[~is_missing, obs].value_counts(normalize=True).head(3).round(3).to_dict()
            top_missing = df.loc[is_missing, obs].value_counts(normalize=True).head(3).round(3).to_dict()
            rows.append({
                "column": obs,
                "type": "categorical",
                "mean_present": str(top_present),
                "mean_missing": str(top_missing),
                "median_present": "",
                "median_missing": "",
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    out_dir = Path("reports/results")
    out_dir.mkdir(parents=True, exist_ok=True)

    targets = ["Lot Frontage", "Mas Vnr Area"]
    observed = ["SalePrice", "Lot Area", "Year Built", "Gr Liv Area", "Lot Config", "Neighborhood"]

    lines = ["=== PART 5: MISSINGNESS MECHANISM ==="]
    for col in targets:
        n_miss = int(df[col].isna().sum())
        pct = 100.0 * n_miss / len(df)
        lines.append(f"\n--- {col}: {n_miss} / {len(df)} missing ({pct:.2f}%) ---")
        summary = compare_groups(df, col, observed)
        lines.append(summary.to_string(index=False))

    output = "\n".join(lines)
    print(output)
    (out_dir / "missingness.txt").write_text(output + "\n")
