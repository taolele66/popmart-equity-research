"""泡泡玛特（9992.HK）盈利预测与估值模型：2026E–2028E 预测、PE 目标价与 DCF 敏感性。
运行：python3 valuation_model.py
"""
fx=0.91 # HKD->CNY
shares=1.31 # bn
px=151.6
mcap_cny=px*shares*10*fx # 亿元 (151.6*1.31bn = 198.6bn HKD = 1986亿HKD)
print("mcap 亿元",round(mcap_cny))
h1_25=171.73/1.238; h2_25=371.2-h1_25
adj_h1_25=51.56/1.095; adj_h2_25=130.8-adj_h1_25
print("H1/H2 25 rev",round(h1_25,1),round(h2_25,1),"adj",round(adj_h1_25,1),round(adj_h2_25,1),"H2 margin",round(adj_h2_25/h2_25,3))
h2_26=h2_25*0.96
r26=171.73+h2_26; np26=51.56+h2_26*0.31
r27=r26*1.15; np27=r27*0.30
r28=r27*1.14; np28=r28*0.30
for y,r,n,prev in [(2026,r26,np26,371.2),(2027,r27,np27,r26),(2028,r28,np28,r27)]:
  print(y,"rev",round(r,1),"g",round(r/prev-1,3),"adjNP",round(n,1),"PE",round(mcap_cny/n,1),"EPS HKD",round(n/shares/10/fx*1,2))
print("H2 26 rev",round(h2_26,1))
# target
for pe in (15,18,22):
  tp=np27*pe/fx/(shares*10)
  print("PE",pe,"TP HKD",round(tp,1),"upside",round(tp/px-1,3))
# DCF
wacc=0.10;g=0.03
fcf=[np26*0.9,np27*0.9,np28*0.9,np28*1.10*0.9,np28*1.10*1.08*0.9]
pv=sum(f/(1+wacc)**(i+0.25) for i,f in enumerate(fcf))  # approx
tv=fcf[-1]*(1+g)/(wacc-g); pvtv=tv/(1+wacc)**4.25
cash=124
ev=pv+pvtv; eq=ev+cash
print("DCF eq 亿元",round(eq),"TP HKD",round(eq/fx/(shares*10),1))
for w in (0.09,0.10,0.11):
  for gg in (0.02,0.03,0.04):
    pv=sum(f/(1+w)**(i+0.25) for i,f in enumerate(fcf)); tv=fcf[-1]*(1+gg)/(w-gg)
    e=pv+tv/(1+w)**4.25+cash
    print(w,gg,round(e/fx/(shares*10),0))
