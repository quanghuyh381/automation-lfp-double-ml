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

## Input files (not included)
The script reads these files that are **not uploaded to this
repository**:

| File | Used for |
|---|---|
| `cenocc2010.xlsx` | 2010 Census occupation codes mapped to SOC codes |
| `isco_soc_crosswalk.xls` | SOC to ISCO-08 crosswalk |
| `pwt1001.xlsx` | Penn World Table 10.01 price levels (`pl_i`, `pl_c`) |
| `EMP_TEMP_SEX_OC2_NB_A-....csv` | ILOSTAT (ILO) | Employment by 2-digit ISCO-08 occupation |
| `HDR25_Composite_indices_complete_time_series.csv` | UNDP Human Development Report Office | Mean years of schooling |
| `occ2010_occ1990dd.dta` | Autor and Dorn | Occupation crosswalk |
| `rti_by_occ1990dd.csv` | (add source) | Routine task intensity by occupation |
| `relative_price_pwt.csv` | (add source) | Relative price series |

**To request these files, please email me at: quanghuyh381@gmail.com**
with the subject line "Input files request" and a short note on how
you plan to use them. I will send them to you when I can.
