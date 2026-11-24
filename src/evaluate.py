"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline

NUMERIC_FEATURES: list[str] = [
    "Lot Frontage", "Lot Area", "Overall Qual", "Overall Cond",
    "Year Built", "Year Remod/Add", "Gr Liv Area", "Total Bsmt SF",
    "1st Flr SF", "Garage Area",
]   # 8 to 15 columns, including "Lot Frontage"
CV = KFold(n_splits=5, shuffle=True, random_state=5110)


class NeighborhoodMedianImputer(BaseEstimator, TransformerMixin):
    """Fit Neighborhood medians for Lot Frontage and column medians on train fold only."""

    def __init__(self, numeric_cols: list[str], group_col: str = "Neighborhood"):
        self.numeric_cols = numeric_cols
        self.group_col = group_col

    def fit(self, X: pd.DataFrame, y=None):
        self.group_medians_ = X.groupby(self.group_col)["Lot Frontage"].median().to_dict()
        self.col_medians_ = X[self.numeric_cols].median().to_dict()
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        out = X[self.numeric_cols].copy()
        out["Lot Frontage"] = out["Lot Frontage"].fillna(X[self.group_col].map(self.group_medians_))
        for col in self.numeric_cols:
            out[col] = out[col].fillna(self.col_medians_[col])
        return out.to_numpy()


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error").mean()


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    y = np.log(df["SalePrice"])

    # Variant A: median Lot Frontage within each quintile of SalePrice, on the full table
    df_a = df.copy()
    quintiles = pd.qcut(df_a["SalePrice"], q=5)
    df_a["Lot Frontage"] = df_a["Lot Frontage"].fillna(
        df_a.groupby(quintiles, observed=False)["Lot Frontage"].transform("median")
    )
    X_a = df_a[NUMERIC_FEATURES].fillna(df_a[NUMERIC_FEATURES].median())
    rmse_a = rmse(LinearRegression(), X_a, y)

    # Variant B: Neighborhood group-median fitted on the full table before CV
    df_b = df.copy()
    df_b["Lot Frontage"] = df_b["Lot Frontage"].fillna(
        df_b.groupby("Neighborhood")["Lot Frontage"].transform("median")
    )
    X_b = df_b[NUMERIC_FEATURES].fillna(df_b[NUMERIC_FEATURES].median())
    rmse_b = rmse(LinearRegression(), X_b, y)

    # Variant C: Neighborhood group-median inside a Pipeline
    pipe_c = Pipeline([
        ("impute", NeighborhoodMedianImputer(NUMERIC_FEATURES, group_col="Neighborhood")),
        ("model", LinearRegression()),
    ])
    X_c = df[NUMERIC_FEATURES + ["Neighborhood"]]
    rmse_c = rmse(pipe_c, X_c, y)

    lines = [
        "=== PART 7: LEAKAGE-SAFE EVALUATION ===",
        f"Variant A (target quintile, full table): {rmse_a:.6f}",
        f"Variant B (group median, before CV):     {rmse_b:.6f}",
        f"Variant C (group median, in Pipeline):   {rmse_c:.6f}",
        f"Difference (C - B):                      {rmse_c - rmse_b:+.6f}",
    ]
    output = "\n".join(lines)
    print(output)
    out_dir = Path("reports/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evaluate.txt").write_text(output + "\n")
