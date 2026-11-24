"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """std before/after, correlation with `other` before/after."""
    return pd.Series({
        "std_before": round(before.std(), 4),
        "std_after": round(after.std(), 4),
        "corr_LotArea_before": round(before.corr(other), 4),
        "corr_LotArea_after": round(after.corr(other), 4),
    })


def save_hist(before: pd.Series, after: pd.Series, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(before.dropna(), bins=30, alpha=0.55, label="Observed (before)", density=True)
    ax.hist(after, bins=30, alpha=0.55, label="Imputed (after)", density=True)
    ax.set_title(title)
    ax.set_xlabel("Lot Frontage (feet)")
    ax.set_ylabel("Density")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    fig_dir = Path("reports/figures")
    res_dir = Path("reports/results")
    fig_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)

    before = df["Lot Frontage"]
    other = df["Lot Area"]

    # Strategy 1: Simple overall median
    med_fill = before.fillna(before.median())

    # Strategy 2: Group median by Neighborhood (fallback to overall median)
    grp_medians = df.groupby("Neighborhood")["Lot Frontage"].transform("median")
    grp_fill = before.fillna(grp_medians).fillna(before.median())

    results = pd.DataFrame({
        "Simple_Median": cost_table(before, med_fill, other),
        "Neighborhood_Median": cost_table(before, grp_fill, other),
    }).T

    save_hist(before, med_fill, "Lot Frontage: Simple Median Imputation", fig_dir / "lot_frontage_median.png")
    save_hist(before, grp_fill, "Lot Frontage: Neighborhood Group-Median Imputation", fig_dir / "lot_frontage_group_median.png")

    out = "=== PART 6: IMPUTATION COST TABLE ===\n" + results.to_string()
    print(out)
    (res_dir / "impute.txt").write_text(out + "\n")
