# Automation Exposure and Labor Force Participation (Double Machine Learning)

This project estimates the effect of automation exposure on labor force participation across 59 countries (2012 to 2023), using Double Machine Learning (DML) and benchmarking the results against a two-way fixed-effects model.

**Status:** In progress. Results are preliminary.

## Research Question

Does automation exposure affect labor force participation, and does the effect differ between high-income and other countries?

## Data

- 59-country panel, 2012 to 2023
- Macroeconomic and labor data collected through APIs
- Automation exposure measure built from occupational routine-task intensity scores and relative capital prices

## Method

1. **Data processing (Python, Pandas):** Collect data via APIs, clean it, and build the country-year panel and the exposure measure.
2. **Estimation (Stata):** Double Machine Learning under a conditional exogeneity assumption, with country-clustered cross-fitting. Learners: Random Forest, Lasso, and Gradient Boosting.
3. **Benchmark:** Two-way fixed-effects (TWFE) model.
4. **Heterogeneity:** Comparison of high-income countries versus other countries.

## Preliminary Findings

- A positive effect of automation exposure on labor force participation, consistent with the TWFE benchmark.
- Differences between income groups are still being tested.
