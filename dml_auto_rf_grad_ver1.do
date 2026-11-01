clear all
import delimited "C:\Users\LAPTOP\Documents\Labor Economics\panel_final_pli"

encode country_code, gen(cid)
xtset cid year

rename fertility_ratetotalbirthsperwoma fertility

gen ln_pl_i = ln(pl_i)
gen ln_pl_c = ln(pl_c)
gen log_diff = ln_pl_i - ln_pl_c
gen auto_log = rti_i * log_diff

gen l_ln_trade    = L1.ln_trade
gen l_unemp_rate  = L1.unemp_rate
gen ln_fertility  = ln(fertility)
gen d_AutoHigh    = highincome * auto_log
gen l_trade_unemp = l_ln_trade*l_unemp_rate
   
global D auto_log
global X ln_pl_i ln_pl_c l_unemp_rate government_effectiveness dependency_ratio mys urban l_ln_trade fertility rel_service_emp
global Y lfp_rate

egen miss = rowmiss($Y $D $X highincome)
keep if miss==0
xtset cid year

corr $Y $D $X
graph matrix $Y $D $X

reghdfe $Y $D $X, absorb(cid year) vce(cluster cid)
test ln_pl_i + ln_pl_c = 0

reghdfe $Y $D $X, absorb(cid year) vce(cluster cid) resid
predict double res, resid
gen double yhat = $Y - res                 
summ yhat
replace yhat = (yhat - r(mean)) / r(sd)
gen yhat2 = yhat^2
gen yhat3 = yhat^3
gen yhat4 = yhat^4
reghdfe $Y $D $X yhat2 yhat3 yhat4, absorb(cid year) vce(cluster cid)
test yhat2 yhat3 yhat4

foreach v in $Y $D $X {
    reghdfe `v', absorb(cid year) resid
    predict r_`v', resid
}

global rX
foreach v in $X {
    global rX $rX r_`v'
}

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(ols)
ddml E[D|X]: pystacked r_auto_log $rX, type(reg) method(ols)
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)
ddml extract, show(n)   

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(lassocv)
ddml E[D|X]: pystacked r_auto_log $rX, type(reg) method(lassocv)
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)
ddml extract, show(n)   

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(rf)
ddml E[D|X]: pystacked r_auto_log $rX, type(reg) method(rf)
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)   
ddml extract, show(n)   

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(gradboost)
ddml E[D|X]: pystacked r_auto_log $rX, type(reg) method(gradboost)
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)   
ddml extract, show(n)      

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(rf gradboost)
ddml E[D|X]: pystacked r_auto_log $rX, type(reg) method(rf gradboost)
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)
ddml extract, show(stweights) 

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(lassocv rf gradboost)
ddml E[D|X]: pystacked r_auto_log $rX, type(reg) method(lassocv rf gradboost)
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)
ddml extract, show(stweights)

clear all
import delimited "C:\Users\LAPTOP\Documents\Labor Economics\panel_final_pli"

encode country_code, gen(cid)
xtset cid year

rename fertility_ratetotalbirthsperwoma fertility

gen ln_pl_i = ln(pl_i)
gen ln_pl_c = ln(pl_c)
gen log_diff = ln_pl_i - ln_pl_c
gen auto_log = rti_i * log_diff

gen l_ln_trade = L1.ln_trade
gen l_unemp_rate = L1.unemp_rate
gen ln_fertility = ln(fertility)
gen l_trade_unemp = l_ln_trade*l_unemp_rate
   
gen d_AutoHigh = highincome * auto_log

global D2 auto_log d_AutoHigh
global X ln_pl_i ln_pl_c l_unemp_rate rel_service_emp government_effectiveness dependency_ratio mys urban l_ln_trade fertility
global Y lfp_rate

egen miss = rowmiss($Y $D2 $X highincome)
keep if miss==0
xtset cid year

reghdfe $Y $D2 $X, absorb(cid year) vce(cluster cid)
lincom auto_log + d_AutoHigh

foreach v in $Y $D2 $X {
    reghdfe `v', absorb(cid year) resid
    predict r_`v', resid
}

global rX
foreach v in $X {
    global rX $rX r_`v'
}

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(ols)
foreach d of global D2 {
    ddml E[D|X]: pystacked r_`d' $rX, type(reg) methods(ols)
}
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)   
ddml extract, show(n) 
lincom r_auto_log + r_d_AutoHigh

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(lassocv)
foreach d of global D2 {
    ddml E[D|X]: pystacked r_`d' $rX, type(reg) methods(lassocv)
}
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)   
ddml extract, show(n) 
lincom r_auto_log + r_d_AutoHigh

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(rf)
foreach d of global D2 {
    ddml E[D|X]: pystacked r_`d' $rX, type(reg) methods(rf)
}
ddml crossfit
ddml estimate, robust cluster(cid)
ddml extract, show(mse)   
ddml extract, show(n) 
lincom r_auto_log + r_d_AutoHigh

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(gradboost)
foreach d of global D2 {
    ddml E[D|X]: pystacked r_`d' $rX, type(reg) methods(gradboost)
}
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)   
ddml extract, show(n) 
lincom r_auto_log + r_d_AutoHigh

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(rf gradboost)
foreach d of global D2 {
    ddml E[D|X]: pystacked r_`d' $rX, type(reg) method(rf gradboost)
}
ddml crossfit
ddml estimate, robust cluster(cid)
ddml desc, all
ddml extract, show(mse)
ddml extract, show(stweights) 
lincom r_auto_log + r_d_AutoHigh

set seed 59328
ddml init partial, kfolds(5) reps(5) fcluster(cid)
ddml E[Y|X]: pystacked r_lfp_rate $rX, type(reg) methods(lassocv rf gradboost)
foreach d of global D2 {
    ddml E[D|X]: pystacked r_`d' $rX, type(reg) method(lassocv rf gradboost)
}
ddml crossfit
ddml desc, all
ddml extract, show(mse)
ddml extract, show(stweights) 
ddml estimate, robust cluster(cid)
lincom r_auto_log + r_d_AutoHigh
