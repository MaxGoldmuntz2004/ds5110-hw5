# HW5: Ames Housing quality audit

## How to run

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
```

## Provenance (Part 1)

| Item | Value |
| --- | --- |
| Source URL | https://jse.amstat.org/v19n3/decock/AmesHousing.txt |
| Downloaded on | 2026-11-23 |
| Citation | De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. Journal of Statistics Education, 19(3). |
| Data dictionary | https://jse.amstat.org/v19n3/decock/DataDocumentation.txt |
| Terms of use | Open educational dataset published in the Journal of Statistics Education for teaching and non-commercial statistical analysis (https://jse.amstat.org/v19n3/decock.pdf). |
| Rows, columns on arrival | 2,930 rows, 82 columns |

## Features used in Part 7

I picked 10 numeric columns for `NUMERIC_FEATURES`: `Lot Frontage`, `Lot Area`, `Overall Qual`, `Overall Cond`, `Year Built`, `Year Remod/Add`, `Gr Liv Area`, `Total Bsmt SF`, `1st Flr SF`, and `Garage Area`. I included `Lot Frontage` as required to test imputation leakage, and chose the other nine because they cover the main physical drivers of home value—lot size, build quality and condition, age/renovation year, and core square footage (living area, basement, first floor, and garage).

## AI assistance

I used Google Gemini for debugging and code scaffolding across `src/`.
