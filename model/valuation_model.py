"""泡泡玛特（9992.HK）盈利预测与估值模型

估值基准日 2026-06-30（中报资产负债表日），现金流按年中折现。
数据来源：2026 年中期业绩公告（港交所，2026-08-20）、2025 年年报。单位：亿元人民币，除非注明。
运行：python3 valuation_model.py
"""

FX = 0.91          # 1 港元 = 0.91 元人民币
SHARES = 13.1      # 亿股，当前总股本（已扣除 2026 年回购注销）
PRICE = 151.6      # 港元，2026-10-08 收盘

# ---------- 1H26 实际数据（中期公告） ----------
OCF_1H26 = 36.373          # 经营活动现金流净额
CAPEX_1H26 = 7.241         # 购买物业厂房设备 6.736 + 无形资产 0.506
LEASE_PAY_1H26 = 4.519 + 0.811   # 使用权资产折旧 + 租赁利息，近似租赁现金支出
CASH = 124.421             # 现金及现金等价物
TERM_DEPOSITS = 15.202 + 2.018   # 一年内 + 一年以上定期存款
BORROWINGS = 0.0           # 无银行借款
NET_CASH = CASH + TERM_DEPOSITS - BORROWINGS
FCF_1H26 = OCF_1H26 - CAPEX_1H26 - LEASE_PAY_1H26

# ---------- 盈利预测 ----------
REV_1H26, ADJ_NP_1H26 = 171.729, 51.558
REV_H2_25 = 371.2 - 138.763
SBC_HALF = 1.2             # 股份支付，经调整净利润与归母净利润之差（半年）

rev = {}
adj_np = {}
rev_h2_26 = REV_H2_25 * (1 - 0.04)
rev[2026] = REV_1H26 + rev_h2_26
adj_np_h2_26 = rev_h2_26 * 0.31
adj_np[2026] = ADJ_NP_1H26 + adj_np_h2_26
growth = {2027: 0.15, 2028: 0.14, 2029: 0.10, 2030: 0.08}
for y, g in growth.items():
    rev[y] = rev[y - 1] * (1 + g)
    adj_np[y] = rev[y] * 0.30

DA_PCT = 0.020                                   # 物业厂房设备折旧 + 无形资产摊销 / 收入（1H26 为 2.1%）
CAPEX_PCT = {2027: 0.035, 2028: 0.030, 2029: 0.025, 2030: 0.025}   # 1H26 为 4.2%，开店放缓后回落
NWC_PCT_OF_DREV = 0.10                           # 营运资本增量 / 收入增量


def fcf(year):
    """自由现金流 = 归母净利润 + 折旧摊销 − 资本开支 − 营运资本增加。
    使用权资产折旧与租赁本息支出近似抵消，因此租赁负债不再从股权价值中扣除。"""
    np_ifrs = adj_np[year] - 2 * SBC_HALF
    da = rev[year] * DA_PCT
    capex = rev[year] * CAPEX_PCT[year]
    dnwc = (rev[year] - rev[year - 1]) * NWC_PCT_OF_DREV
    return np_ifrs + da - capex - dnwc, dict(np=np_ifrs, da=da, capex=capex, dnwc=dnwc)


# 2026 下半年：库存已在上半年备足，假设营运资本不再增加
fcf_h2_26 = (adj_np_h2_26 - SBC_HALF) + rev_h2_26 * DA_PCT - CAPEX_1H26


def dcf(wacc, g):
    flows = [(0.25, fcf_h2_26)] + [(y - 2026.0, fcf(y)[0]) for y in range(2027, 2031)]
    pv = sum(cf / (1 + wacc) ** t for t, cf in flows)
    tv = fcf(2030)[0] * (1 + g) / (wacc - g)
    pv_tv = tv / (1 + wacc) ** 4.5
    equity = pv + pv_tv + NET_CASH
    return equity / FX / SHARES, dict(pv=pv, pv_tv=pv_tv, equity=equity)


if __name__ == "__main__":
    print(f"1H26 自由现金流 {FCF_1H26:.1f} 亿元，占经调整净利润 {FCF_1H26 / ADJ_NP_1H26:.0%}")
    print(f"净现金（现金 + 定期存款 − 借款） {NET_CASH:.1f} 亿元\n")
    print("年份  营收   经调整净利润  折旧摊销  资本开支  营运资本  自由现金流  FCF/净利润")
    print(f"2H26  {rev_h2_26:6.1f} {adj_np_h2_26:9.1f}        —          —         —      {fcf_h2_26:6.1f}")
    for y in range(2027, 2031):
        f, d = fcf(y)
        print(f"{y}  {rev[y]:6.1f} {adj_np[y]:9.1f} {d['da']:9.1f} {d['capex']:9.1f} {d['dnwc']:9.1f} {f:10.1f} {f / adj_np[y]:9.0%}")
    tp_dcf, parts = dcf(0.10, 0.03)
    print(f"\nDCF（WACC 10%，g 3%）：显性期现值 {parts['pv']:.0f}，终值现值 {parts['pv_tv']:.0f}，"
          f"净现金 {NET_CASH:.0f}，股权价值 {parts['equity']:.0f} 亿元 → {tp_dcf:.1f} 港元/股"
          f"（终值占 {parts['pv_tv'] / (parts['pv'] + parts['pv_tv']):.0%}）")
    print("\n敏感性（港元/股）  g=2%   g=3%   g=4%")
    for w in (0.09, 0.10, 0.11):
        print(f"  WACC {w:.0%}        " + "  ".join(f"{dcf(w, g)[0]:5.0f}" for g in (0.02, 0.03, 0.04)))
    print("\nPE 法（2027E 经调整净利润）")
    eps27 = adj_np[2027] / FX / SHARES
    for pe in (15, 18, 22):
        print(f"  {pe} 倍 → {eps27 * pe:.0f} 港元")
    tp = round(eps27 * 18 / 5) * 5
    print(f"\n目标价（PE 法为主）：{tp} 港元，上行空间 {tp / PRICE - 1:.0%}；DCF 交叉验证 {tp_dcf:.0f} 港元")
