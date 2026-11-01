"""
Single pipeline: RTI (ISCO 2-digit) -> country RTI -> panel + World Bank controls
-> HDR schooling -> PWT price ratios -> automation exposure variables.
Run once:  pip install pandas numpy wbgapi openpyxl xlrd
"""
import re
import numpy as np
import pandas as pd
import wbgapi as wb

REF_YEAR, MIN_COV = 2012, 0.80
YEARS = range(2012, 2024)

#1. RTI by ISCO 2-digit
rti = pd.read_csv("rti_by_occ1990dd.csv")
a8 = pd.read_stata("occ2010_occ1990dd.dta")[["occ", "occ1990dd"]].copy()
a8["occ"] = a8["occ"].astype(str).str.strip().str.zfill(4)
a8["occ1990dd"] = a8["occ1990dd"].astype("Int64")
rti["occ1990dd"] = rti["occ1990dd"].astype("Int64")

cs = pd.read_excel("cenocc2010.xlsx", header=None, dtype=str, skiprows=7,
                   usecols=[0, 1, 2], names=["census_title", "occ", "soc_raw"]).dropna(subset=["occ", "soc_raw"])
cs = cs.apply(lambda c: c.str.strip())
cs = cs[cs["occ"].str.fullmatch(r"\d{4}")].copy()
cs["soc2010"] = cs["soc_raw"].apply(lambda s: re.findall(r"\d{2}-\d{4}", s))
cs = cs.explode("soc2010").dropna(subset=["soc2010"])

m = (a8.merge(rti[["occ1990dd", "RTI"]], on="occ1990dd", how="left")
       .merge(cs[["occ", "soc2010"]], on="occ", how="left")
       .dropna(subset=["RTI", "soc2010"]))
m["RTI"] = m["RTI"].astype(float)

x = pd.read_excel("isco_soc_crosswalk.xls", header=None, dtype=str).iloc[7:, [0, 3]].dropna()
x.columns = ["isco08", "soc2010"]
x = x.apply(lambda c: c.str.strip()).drop_duplicates()
x["isco08"] = x["isco08"].str.zfill(4)

def isco_of(soc):                       # broad SOC groups (e.g. 25-1000) match on the prefix
    for k in range(4):
        hit = x[x["soc2010"].str.startswith(soc[:len(soc) - k])]
        if len(hit):
            return list(hit["isco08"])
    return []

m["isco08"] = m["soc2010"].apply(isco_of)
m = m.explode("isco08").dropna(subset=["isco08"])
m = m[~m["isco08"].str[:2].isin(["01", "02", "03"])]               # drop armed forces

isco2 = (m.groupby("isco08")["RTI"].mean().reset_index()
           .assign(isco2=lambda d: d["isco08"].str[:2].astype(int))
           .groupby("isco2", as_index=False)["RTI"].mean())
isco2["RTI_z"] = (isco2["RTI"] - isco2["RTI"].mean()) / isco2["RTI"].std()
isco2.to_csv("rti_by_isco2.csv", index=False)

#2. Country-level RTI_i
emp = pd.read_csv("EMP_TEMP_SEX_OC2_NB_A-20261004T0844.csv", low_memory=False)
emp = emp[(emp["sex"] == "SEX_T") & emp["classif1"].str.startswith("OC2_ISCO08_", na=False)
          & ~emp["classif1"].isin(["OC2_ISCO08_TOTAL", "OC2_ISCO08_X"]) & (emp["time"] == REF_YEAR)].copy()
emp["isco2"] = emp["classif1"].str.replace("OC2_ISCO08_", "", regex=False).astype(int)
emp["ok"] = emp["isco2"].isin(isco2["isco2"])

cov = emp[emp["ok"]].groupby("ref_area")["obs_value"].sum() / emp.groupby("ref_area")["obs_value"].sum()
keep = cov[cov >= MIN_COV].index                                   # coverage threshold
e = emp[emp["ok"] & emp["ref_area"].isin(keep)].merge(isco2, on="isco2")
e["w"] = e["obs_value"] / e.groupby("ref_area")["obs_value"].transform("sum")
rti_c = (e.assign(RTI_i=e["w"] * e["RTI"], RTI_i_z=e["w"] * e["RTI_z"])
          .groupby("ref_area")
          .agg(RTI_i=("RTI_i", "sum"), RTI_i_z=("RTI_i_z", "sum"), n_occupations_matched=("isco2", "nunique"))
          .reset_index().rename(columns={"ref_area": "country_code"}))
rti_c.to_csv("rti_by_country.csv", index=False)

#3. Base panel (RTI x relative price)
panel = pd.read_csv("relative_price_pwt.csv").merge(rti_c, on="country_code", how="inner")
panel["Auto"] = panel["RTI_i"] * panel["relative_price"]
panel = panel[panel["year"].isin(YEARS)].copy()
countries = sorted(panel["country_code"].unique())

#4. World Bank variables (one call)
wbvars = {"SL.TLF.CACT.ZS": "lfp_rate", "NE.TRD.GNFS.ZS": "trade", "BX.GSR.GNFS.CD": "exp",
          "BM.GSR.GNFS.CD": "imp", "NY.GDP.MKTP.CD": "gdp", "SP.URB.TOTL.IN.ZS": "urban",
          "SL.SRV.EMPL.ZS": "emp_services", "SL.IND.EMPL.ZS": "emp_industry", "SL.UEM.TOTL.ZS": "unemp_rate",
          "NY.GDP.PCAP.PP.KD": "gdppc_ppp", "NY.GDP.PCAP.KD": "gdppc_usd", "SP.POP.DPND": "dependency_ratio",
          "SP.DYN.TFRT.IN": "fertility_rate"}                       # total fertility, births per woman
d = (wb.data.DataFrame(list(wbvars), economy=countries, time=YEARS, index=["economy", "time"],
                       numericTimeKeys=True, labels=False).reset_index()
       .rename(columns={**wbvars, "economy": "country_code", "time": "year"}))

d["bop"] = (d["exp"] + d["imp"]) / d["gdp"] * 100                  # trade % GDP from balance of payments
d["trade_filled"] = d["trade"].isna() & d["bop"].notna()
d["trade_open"] = d["trade"].fillna(d["bop"])
d["ln_trade"] = np.log(d["trade_open"])
d["rel_service_emp"] = d["emp_services"] / d["emp_industry"]
for c in ["gdppc_ppp", "gdppc_usd"]:
    d["ln_" + c] = np.log(d[c].where(d[c] > 0))
d["ln_gdppc_ppp_sq"] = d["ln_gdppc_ppp"] ** 2
d = d.drop(columns=["trade", "exp", "imp", "gdp", "bop"])

panel = panel.merge(d, on=["country_code", "year"], how="left", validate="1:1")

#4b. Government effectiveness (Worldwide Governance Indicators, db=3)
ge = (wb.data.DataFrame("GOV_WGI_GE.EST", economy=countries, time=YEARS, db=3,
                        numericTimeKeys=True, labels=False).reset_index()
        .melt(id_vars="economy", var_name="year", value_name="government_effectiveness")
        .rename(columns={"economy": "country_code"}))
ge["year"] = ge["year"].astype(int)
panel = panel.merge(ge, on=["country_code", "year"], how="left", validate="1:1")

#5. Income groups
econ = wb.economy.DataFrame().reset_index().rename(columns={"id": "country_code"})
panel = panel.merge(econ[["country_code", "incomeLevel", "region"]], on="country_code", how="left")
panel["HighIncome"] = (panel["incomeLevel"] == "HIC").astype(int)
panel["NonHighIncome"] = 1 - panel["HighIncome"]

#6. Mean years of schooling (HDR)
h = pd.read_csv("HDR25_Composite_indices_complete_time_series.csv", encoding="latin-1")
mys = (h.filter(regex=r"^(iso3|mys_\d{4})$").melt(id_vars="iso3", var_name="year", value_name="mys")
         .assign(year=lambda t: t["year"].str[-4:].astype(int))
         .rename(columns={"iso3": "country_code"}))
panel = panel.merge(mys, on=["country_code", "year"], how="left")

#7. Exposure variables
panel["rp_avg"] = panel.groupby("year")["relative_price"].transform("mean")
panel["Auto_avg"] = panel["RTI_i"] * panel["rp_avg"]

pwt = (pd.read_excel("pwt1001.xlsx", sheet_name="Data", usecols=["countrycode", "year", "pl_i", "pl_c"])
         .rename(columns={"countrycode": "country_code"}))
pwt["rel_price_inv"] = pwt["pl_i"] / pwt["pl_c"]
panel = panel.merge(pwt, on=["country_code", "year"], how="left")

panel["rp_avg_new"] = panel.groupby("year")["rel_price_inv"].transform("mean")
panel["Auto_avg_new"] = panel["RTI_i"] * panel["rp_avg_new"]       # common price
panel["Auto_new"] = panel["RTI_i"] * panel["rel_price_inv"]        # country-specific price
panel["Auto_avg_new_x_NonHigh"] = panel["Auto_avg_new"] * panel["NonHighIncome"]
panel["Auto_new_x_NonHigh"] = panel["Auto_new"] * panel["NonHighIncome"]

panel["ln_pli_plc"] = np.log(panel["pl_i"] / panel["pl_c"])
panel["RTI_c"] = panel["RTI_i"] - panel["RTI_i"].mean()
panel["auto_log_i_c"] = panel["RTI_c"] * panel["ln_pli_plc"]       # main treatment
panel["auto_log_i_z"] = panel["RTI_i_z"] * panel["ln_pli_plc"]
panel["auto_log_i_old"] = panel["RTI_i"] * panel["ln_pli_plc"]
panel["auto_log_i_hi"] = np.where(panel["RTI_i"] > panel["RTI_i"].median(), 1, -1) * panel["ln_pli_plc"]
panel["bin3"] = (panel["year"] - panel["year"].min()) // 3
panel["auto_log_i_c_b3"] = panel.groupby(["country_code", "bin3"])["auto_log_i_c"].transform("mean")

#8. Save + diagnostics
panel.to_csv("panel_final_pli.csv", index=False)
print(panel.shape, panel["country_code"].nunique(), "countries")
print(panel.isna().sum()[lambda s: s > 0].to_string())