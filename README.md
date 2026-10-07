# Bank Customer Churn Analysis

An analysis of ~10,000 European bank customers testing whether **behavioral and engagement signals** (activity status, product holdings, relationship depth) explain churn better than **purely financial indicators** (balance, salary). The project includes six analysis notebooks, a set of custom retention KPIs, and an interactive Streamlit dashboard.

The full write-up is in [`research_paper.pdf`](research_paper.pdf), with a short version in [`executive_summary.pdf`](executive_summary.pdf).

## Key Findings

Overall churn rate: **20.37%**.

| Finding | Detail |
|---|---|
| Engagement beats balance as a churn signal | Churn spread by activity is 0.126 (inactive 26.9% vs active 14.3%), versus 0.092 by balance (high 25.0% vs low 15.8%). |
| High balance does not protect disengaged customers | *Inactive High-Balance* customers churn at 32.3%, the highest of any engagement profile. |
| Product count is non-monotonic | 1 product: 27.7%, **2 products: 7.6%**, 3 products: 82.7%, 4 products: 100%. The 3-4 product group is only 3.3% of customers. |
| Credit card ownership is not a retention lever | 20.8% (no card) vs 20.2% (card). |
| Age is the strongest single correlate | r = +0.29 with churn; the 46-60 band churns at 51.1%. |
| Germany stands out | 32.4% churn vs 16.2% (France) and 16.7% (Spain). |

### Caveats

- The churn spike among 3-4 product customers is **not explained** by inactivity or geography in this dataset. It is flagged as an open question.
- The *Inactive High-Balance* segment is 42% German, and Germany's standalone churn rate (32.4%) closely matches that segment's rate (32.3%), so part of the engagement effect likely overlaps with geography.
- This is descriptive analysis. No predictive model or significance testing is included, so the findings show associations, not causes.

## Engagement Profiles

Customers are split into four profiles using activity status, product count, and balance relative to the median:

| Profile | Rule | Churn Rate |
|---|---|---|
| Active Engaged | Active, 2+ products | 9.7% |
| Active Low-Product | Active, 1 product | 18.9% |
| Inactive Disengaged | Inactive, balance at or below median | 21.2% |
| Inactive High-Balance | Inactive, balance above median | 32.3% |

The *Inactive High-Balance* segment has 2,456 customers (24.6% of the base). A narrower **at-risk watchlist** (inactive, top-quartile balance and salary, not yet churned) contains 220 customers (2.2%), with an average balance of €148,165 and an average salary of €176,746.

## Retention KPIs

| KPI | Definition | Value |
|---|---|---|
| Engagement Retention Ratio | Inactive churn rate / active churn rate | 1.88 |
| Product Depth Index | Retention score by product count, weighted by segment size | 0.80 |
| High-Balance Disengagement Rate | Share of high-balance customers who are inactive | 49.1% |
| Credit Card Stickiness Score | Churn (no card) minus churn (card) | 0.006 |
| Relationship Strength Index | 0.4 × activity + 0.3 × product score + 0.1 × credit card + 0.2 × normalized tenure | correlates -0.27 with churn |

The Relationship Strength Index is lowest in Germany (0.576 vs 0.594-0.599 elsewhere), consistent with Germany's higher churn.

## Project Structure

```
├── data/
│   └── European_Bank.csv
├── notebooks/
│   ├── 01_data_validation.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_engagement_classification.ipynb
│   ├── 04_product_utilization.ipynb
│   ├── 05_financial_commitment.ipynb
│   └── 06_kpi_definitions.ipynb
├── dashboard/
│   └── app.py
├── outputs/figures/          # charts exported by the notebooks
├── executive_summary.pdf
├── research_paper.pdf
└── requirements.txt
```

| Notebook | Focus |
|---|---|
| 01 | Data validation: nulls, duplicates, constant columns, value ranges, class balance |
| 02 | Exploratory analysis: distributions, churn by geography, gender, and age band, correlation matrix |
| 03 | Engagement profile classification and confounder checks |
| 04 | Product utilization and the 3-4 product anomaly |
| 05 | Balance × activity analysis, at-risk watchlist, salary-balance mismatch group |
| 06 | KPI definitions and the Relationship Strength Index |

## Dashboard

The Streamlit dashboard (`dashboard/app.py`) loads the dataset, rebuilds the engineered features, and provides sidebar filters for engagement profile, number of products, balance range, and salary range. It has four sections:

1. **Engagement vs Churn Overview**: churn by engagement profile against the overall baseline
2. **Product Utilization Impact**: churn by product count
3. **High-Value Disengaged Customer Detector**: a live table of at-risk customers matching the watchlist criteria
4. **Retention Strength Scoring Panel**: all five KPIs, recalculated on the filtered data, plus a breakdown by geography

## Getting Started

```bash
git clone https://github.com/abhinavray07/bank_churn_project.git
cd bank_churn_project
pip install -r requirements.txt
```

Run the dashboard from the project root:

```bash
streamlit run dashboard/app.py
```

To run the notebooks, install Jupyter (`pip install jupyter`), launch it from inside the `notebooks/` folder, and run them in order. They read the data with the relative path `../data/European_Bank.csv` and save figures to `../outputs/figures/`.

The KPI notebook and dashboard use `groupby(...).apply(..., include_groups=False)`, which needs **pandas 2.2 or newer**.

## Tech Stack

Python, Pandas, Matplotlib, Seaborn, Streamlit, Jupyter Notebook