"""
Rebuild Section 7 — Tom Tat & Nhan Xet
7 KPI card dong bo voi Section 1 (tai su dung class kpi1-*) + card nhan xet tong quan.
"""

import pandas as pd
import subprocess, sys, shutil

TARGET = "bitcoin_dashboard copy 2.html"
CSV    = "bitcoin_data/btc_daily.csv"

FONT    = "'Segoe UI', system-ui, -apple-system, sans-serif"
C_GREEN = "#16A34A"
C_RED   = "#DC2626"
C_NAVY  = "#0F4C81"

# ── 1. Load & compute metrics ─────────────────────────────────────────────────
print("[+] Loading data...")
df = pd.read_csv(CSV, parse_dates=["open_time"])
df = df.rename(columns={"open_time": "Date", "close": "Close"})
df = df[["Date", "Close"]]
df = df[(df["Date"] >= "2018-01-01") & (df["Date"] <= "2026-05-31")]
df = df.sort_values("Date").reset_index(drop=True)

# Yearly returns — anchor to first data point so 2018 is included
# (dataset starts Jan 2018 → no prior year → 2018 would be NaN without this fix)
_ref_price   = df["Close"].iloc[0]    # Jan 1 2018 close as baseline
yearly_close = df.set_index("Date")["Close"].resample("YS").last()
_ref_series  = pd.Series(
    [_ref_price],
    index=pd.DatetimeIndex(["2017-01-01"]),
)
yearly_ret   = pd.concat([_ref_series, yearly_close]).pct_change().dropna() * 100
best_yr_val  = round(yearly_ret.max(), 1)
best_yr      = str(yearly_ret.idxmax().year)
worst_yr_val = round(yearly_ret.min(), 1)
worst_yr     = str(yearly_ret.idxmin().year)

# Monthly returns
monthly_close = df.set_index("Date")["Close"].resample("MS").last()
monthly_ret   = monthly_close.pct_change().dropna() * 100
best_mo_val   = round(monthly_ret.max(), 1)
best_mo       = monthly_ret.idxmax().strftime("%Y-%m")
worst_mo_val  = round(monthly_ret.min(), 1)
worst_mo      = monthly_ret.idxmin().strftime("%Y-%m")

# Max Drawdown
running_max = df["Close"].cummax()
drawdown    = (df["Close"] / running_max - 1) * 100
max_dd      = round(drawdown.min(), 1)
max_dd_date = df.loc[drawdown.idxmin(), "Date"].strftime("%Y-%m-%d")

# CAGR + growth factor
n_years  = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
growth_x = round(df["Close"].iloc[-1] / df["Close"].iloc[0], 1)
cagr_pct = round((growth_x ** (1 / n_years) - 1) * 100, 1)

# Bull months
bull_months  = int((monthly_ret > 0).sum())
total_months = int(len(monthly_ret))
bull_pct     = round(bull_months / total_months * 100, 1)

def fpc(v):
    return f"{'+' if v >= 0 else ''}{v:.1f}%"

print(f"    Best year:   {best_yr}     {best_yr_val:+.1f}%")
print(f"    Worst year:  {worst_yr}     {worst_yr_val:+.1f}%")
print(f"    Best month:  {best_mo}  {best_mo_val:+.1f}%")
print(f"    Worst month: {worst_mo}  {worst_mo_val:+.1f}%")
print(f"    Max DD:      {max_dd:.1f}%  ({max_dd_date})")
print(f"    CAGR:        {cagr_pct:+.1f}%  ({growth_x}x)")
print(f"    Bull months: {bull_pct}%  ({bull_months}/{total_months})")

# ── 2. KPI card builder ───────────────────────────────────────────────────────
# Tai su dung .kpi1-card, .kpi1-bar, .kpi1-body, .kpi1-sub tu Section 1.
# Chi override font-size cua gia tri chinh len 34px (Section 1 dung 30px).
def kpi_card(bar_color, label, value, val_color, subtitle):
    return (
        f'<div class="kpi1-card">'
        f'<div class="kpi1-bar" style="background:{bar_color};">{label}</div>'
        f'<div class="kpi1-body">'
        f'<div class="kpi1-val" style="color:{val_color};font-size:34px;">'
        f'{value}</div>'
        f'<div class="kpi1-sub">{subtitle}</div>'
        f'</div>'
        f'</div>'
    )

cards = [
    kpi_card(
        C_GREEN,
        "N&#259;m T&#259;ng M&#7841;nh Nh&#7845;t",
        best_yr, C_GREEN,
        fpc(best_yr_val),
    ),
    kpi_card(
        C_RED,
        "N&#259;m Gi&#7843;m M&#7841;nh Nh&#7845;t",
        worst_yr, C_RED,
        fpc(worst_yr_val),
    ),
    kpi_card(
        C_GREEN,
        "Th&#225;ng T&#259;ng M&#7841;nh Nh&#7845;t",
        best_mo, C_GREEN,
        fpc(best_mo_val),
    ),
    kpi_card(
        C_RED,
        "Th&#225;ng Gi&#7843;m M&#7841;nh Nh&#7845;t",
        worst_mo, C_RED,
        fpc(worst_mo_val),
    ),
    kpi_card(
        C_RED,
        "Drawdown T&#7889;i &#272;a",
        fpc(max_dd), C_RED,
        f"Ng&#224;y&nbsp;{max_dd_date}",
    ),
    kpi_card(
        C_NAVY,
        "CAGR H&#224;ng N&#259;m",
        fpc(cagr_pct), C_GREEN,
        "T&#259;ng tr&#432;&#7903;ng k&#233;p&nbsp;/&nbsp;n&#259;m",
    ),
    kpi_card(
        C_GREEN,
        "T&#7927; L&#7879; Th&#225;ng T&#259;ng Gi&#225;",
        f"{bull_pct}%", C_GREEN,
        f"{bull_months}&nbsp;/&nbsp;{total_months}&nbsp;th&#225;ng",
    ),
]

all_cards = "".join(cards)

# ── 3. Narrative card ─────────────────────────────────────────────────────────
P = f"margin:0 0 18px;line-height:1.8;font-size:15px;color:#1E293B;font-family:{FONT};"
P_LAST = f"margin:0;line-height:1.8;font-size:15px;color:#1E293B;font-family:{FONT};"

narrative_html = (
    f'<p style="{P}">'
    f'Bitcoin giai &#273;o&#7841;n 2018&ndash;2026 ghi nh&#7853;n t&#7889;c'
    f' &#273;&#7897; t&#259;ng tr&#432;&#7903;ng k&#233;p h&#224;ng n&#259;m (CAGR)'
    f' &#7845;n t&#432;&#7907;ng'
    f' <strong style="color:{C_GREEN}">{fpc(cagr_pct)}</strong>,'
    f' bi&#7871;n m&#7897;t kho&#7843;n &#273;&#7847;u t&#432; $1 ban &#273;&#7847;u'
    f' th&#224;nh <strong style="color:{C_GREEN}">${growth_x}x</strong>.'
    f' Th&#7883; tr&#432;&#7901;ng c&#243;'
    f' <strong style="color:{C_GREEN}">{bull_pct}%</strong>'
    f' s&#7889; th&#225;ng t&#259;ng gi&#225; ({bull_months}/{total_months}&nbsp;th&#225;ng),'
    f' cho th&#7845;y xu h&#432;&#7899;ng t&#259;ng d&#224;i h&#7841;n v&#432;&#7907;t'
    f' tr&#7897;i d&#249; bi&#7871;n &#273;&#7897;ng r&#7845;t cao.'
    f'</p>'

    f'<p style="{P}">'
    f'<strong style="color:{C_GREEN}">{best_yr}</strong>'
    f' l&#224; n&#259;m b&#249;ng n&#7893; m&#7841;nh nh&#7845;t'
    f' ({fpc(best_yr_val)}), &#273;&#432;&#7907;c th&#250;c &#273;&#7849;y b&#7903;i'
    f' &#273;&#7841;i d&#7883;ch th&#250;c &#273;&#7849;y t&#237;ch l&#361;y t&#224;i'
    f' s&#7843;n s&#7889; &amp; DeFi b&#249;ng n&#7893;.'
    f' Ng&#432;&#7907;c l&#7841;i,'
    f' <strong style="color:{C_RED}">{worst_yr}</strong>'
    f' l&#224; n&#259;m t&#7879; nh&#7845;t ({fpc(worst_yr_val)})'
    f' do b&#7885;ng b&#243;ng ICO 2017 v&#7905;, th&#7883; tr&#432;&#7901;ng'
    f' &#273;i&#7873;u ch&#7881;nh s&#226;u.'
    f'</p>'

    f'<p style="{P_LAST}">'
    f'M&#7913;c drawdown t&#7889;i &#273;a'
    f' <strong style="color:{C_RED}">{fpc(max_dd)}</strong>'
    f' ph&#7843;n &#225;nh r&#7911;i ro c&#7921;c cao &mdash; tuy nhi&#234;n'
    f' m&#7895;i chu k&#7923; g&#7845;u trong l&#7883;ch s&#7917; &#273;&#7873;u'
    f' &#273;&#432;&#7907;c ti&#7871;p n&#7889;i b&#7903;i m&#7897;t &#273;&#7881;nh'
    f' m&#7899;i cao h&#417;n. C&#225;c c&#7897;t m&#7889;c quan tr&#7885;ng'
    f' nh&#432; <em>Halving</em>, <em>ETF Spot</em>'
    f' v&#224; <em>d&#7921; tr&#7919; qu&#7889;c gia</em>'
    f' &#273;&#225;nh d&#7845;u Bitcoin &#273;ang chuy&#7875;n t&#7915;'
    f' t&#224;i s&#7843;n &#273;&#7847;u c&#417; sang l&#7899;p t&#224;i s&#7843;n'
    f' ch&#237;nh th&#7889;ng to&#224;n c&#7847;u.'
    f'</p>'
)

# ── 4. Build section HTML ─────────────────────────────────────────────────────
NEW_SECTION = f"""<!-- Section 7: Insights -->
  <style>
    /* KPI Section 7: 4-col grid, tai su dung .kpi1-card style */
    .kpi7-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 28px;
    }}
    @media (max-width: 1100px) {{
      .kpi7-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 500px) {{
      .kpi7-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>

  <div class="section">
    <div class="section-title">
      Section 7 &mdash; T&#243;m T&#7855;t &amp; Nh&#7853;n X&#233;t
    </div>

    <!-- 7 KPI cards — 4 col desktop -->
    <div class="kpi7-grid">
      {all_cards}
    </div>

    <!-- Card nhan xet tong quan -->
    <div style="
      background:#FFFBEB;
      border:1px solid #FDE68A;
      border-left:4px solid #F59E0B;
      border-radius:18px;
      padding:28px 32px;
      font-family:{FONT};
    ">
      <div style="
        font-size:16px;
        font-weight:700;
        color:#92400E;
        margin-bottom:20px;
        letter-spacing:0.2px;
        font-family:{FONT};
      ">
        Nh&#7853;n X&#233;t T&#7893;ng Quan
      </div>
      {narrative_html}
    </div>

  </div>

  """

# ── 5. Inject into HTML ───────────────────────────────────────────────────────
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

S_MARK = "<!-- Section 7: Insights -->"
E_MARK = "</div><!-- /container -->"

s = html.find(S_MARK)
e = html.find(E_MARK, s)

if s == -1 or e == -1:
    print(f"[ERROR] Markers not found  s={s}  e={e}")
    sys.exit(1)

html = html[:s] + NEW_SECTION + html[e:]
print(f"    Injected Section 7  (s={s})")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")

# ── 6. Fix bdata + sync to index.html ────────────────────────────────────────
print("[+] Running fix_bdata.py...")
subprocess.run([sys.executable, "fix_bdata.py"], check=True)
print("[+] Running fix_heatmap.py...")
subprocess.run([sys.executable, "fix_heatmap.py"], check=True)

shutil.copy(TARGET, "index.html")
print("[+] Synced to index.html")

print(f"\n[DONE] Section 7 rebuilt.")
print(f"  {best_yr} {best_yr_val:+.1f}%  |  {worst_yr} {worst_yr_val:+.1f}%")
print(f"  CAGR {cagr_pct:+.1f}%  |  Max DD {max_dd:.1f}%  |  Bull {bull_pct}%")
print("Ctrl+Shift+R to refresh browser.")
