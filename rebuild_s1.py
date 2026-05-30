"""
Rebuild Section 1 — Chi So Hieu Suat Chinh (KPI)
10 KPI tinh tu data goc, 5 cot x 2 hang, logical grouping.
Khong hard-code so lieu.
"""

import pandas as pd
import sys

TARGET = "bitcoin_dashboard copy 2.html"
CSV    = "bitcoin_data/btc_daily.csv"

# ── 1. Load & prepare data ────────────────────────────────────────────────────
print("[+] Loading data...")
df = pd.read_csv(CSV, parse_dates=["open_time"])
df = df.rename(columns={
    "open_time": "Date",
    "open":  "Open",
    "high":  "High",
    "low":   "Low",
    "close": "Close",
})
df = df[["Date","Open","High","Low","Close"]]
df = df[(df["Date"] >= "2018-01-01") & (df["Date"] <= "2026-05-31")]
df = df.sort_values("Date").reset_index(drop=True)
print(f"    Rows: {len(df)}  ({df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()})")

# ── 2. Compute KPIs ───────────────────────────────────────────────────────────

# 1. Gia BTC moi nhat
latest_price = df["Close"].iloc[-1]
latest_date  = df["Date"].iloc[-1].strftime("%Y-%m-%d")

# 2. Dinh cao nhat (All-Time High)
ath_idx   = df["High"].idxmax()
ath_price = df.loc[ath_idx, "High"]
ath_date  = df.loc[ath_idx, "Date"].strftime("%Y-%m-%d")

# 3. Day thap nhat (All-Time Low)
atl_idx   = df["Low"].idxmin()
atl_price = df.loc[atl_idx, "Low"]
atl_date  = df.loc[atl_idx, "Date"].strftime("%Y-%m-%d")

# 4. Tong tang truong
first_close = df["Close"].iloc[0]
last_close  = df["Close"].iloc[-1]
first_date  = df["Date"].iloc[0].strftime("%Y-%m-%d")
total_growth = (last_close / first_close - 1) * 100

# 5 & 6 & 10. Monthly returns
monthly_close = df.set_index("Date")["Close"].resample("MS").last()
monthly_ret   = monthly_close.pct_change().dropna() * 100

best_month_ret  = monthly_ret.max()
best_month_lbl  = monthly_ret.idxmax().strftime("%Y-%m")
worst_month_ret = monthly_ret.min()
worst_month_lbl = monthly_ret.idxmin().strftime("%Y-%m")
avg_monthly_ret = monthly_ret.mean()

# 7 & 8. Yearly returns
yearly_close = df.set_index("Date")["Close"].resample("YS").last()
yearly_ret   = yearly_close.pct_change().dropna() * 100

best_year_ret = yearly_ret.max()
best_year_lbl = str(yearly_ret.idxmax().year)
worst_year_ret = yearly_ret.min()
worst_year_lbl = str(yearly_ret.idxmin().year)

# 9. Max Drawdown
running_max = df["Close"].cummax()
drawdown    = (df["Close"] / running_max - 1) * 100
max_dd      = drawdown.min()
max_dd_date = df.loc[drawdown.idxmin(), "Date"].strftime("%Y-%m-%d")

print(f"    Latest: ${latest_price:,.0f}  ATH: ${ath_price:,.0f}  ATL: ${atl_price:,.0f}")
print(f"    Growth: {total_growth:+.1f}%  Max DD: {max_dd:.1f}%")
print(f"    Best month: {best_month_ret:+.1f}% ({best_month_lbl})  "
      f"Worst: {worst_month_ret:+.1f}% ({worst_month_lbl})")
print(f"    Best year: {best_year_ret:+.1f}% ({best_year_lbl})  "
      f"Worst: {worst_year_ret:+.1f}% ({worst_year_lbl})")
print(f"    Avg monthly: {avg_monthly_ret:+.1f}%")

# ── 3. Format helpers ─────────────────────────────────────────────────────────
def fp(v):
    return f"${v:,.0f}"

def fpc(v):
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}%"

# ── 4. Card builder ───────────────────────────────────────────────────────────
FONT = "'Segoe UI', system-ui, -apple-system, sans-serif"

def kpi_card(bar_color, label, value, val_color, subtitle):
    return (
        f'<div class="kpi1-card">'
        f'<div class="kpi1-bar" style="background:{bar_color};">{label}</div>'
        f'<div class="kpi1-body">'
        f'<div class="kpi1-val" style="color:{val_color};">{value}</div>'
        f'<div class="kpi1-sub">{subtitle}</div>'
        f'</div>'
        f'</div>'
    )

# ── 5. Build 10 cards in grid order ──────────────────────────────────────────
#   Row 1: Latest | ATH | Best Month | Best Year | Avg Monthly
#   Row 2: Growth | ATL | Worst Month | Worst Year | Max DD

C_AMBER = "#F59E0B"
C_GREEN = "#16A34A"
C_RED   = "#DC2626"
C_NAVY  = "#0F4C81"
C_BLUE  = "#2563EB"

avg_color = C_GREEN if avg_monthly_ret >= 0 else C_RED

cards_row1 = [
    kpi_card(C_AMBER, "Gi&#225; BTC M&#417;i Nh&#7845;t",
             fp(latest_price), C_AMBER,
             latest_date),

    kpi_card(C_GREEN, "&#272;&#7881;nh Cao Nh&#7845;t",
             fp(ath_price), C_GREEN,
             ath_date),

    kpi_card(C_GREEN, "Th&#225;ng T&#259;ng T&#7889;t Nh&#7845;t",
             fpc(best_month_ret), C_GREEN,
             best_month_lbl),

    kpi_card(C_GREEN, "N&#259;m T&#259;ng T&#7889;t Nh&#7845;t",
             fpc(best_year_ret), C_GREEN,
             best_year_lbl),

    kpi_card(C_NAVY, "L&#7907;i Nhu&#7853;n TB Th&#225;ng",
             fpc(avg_monthly_ret), avg_color,
             "Trung b&#236;nh m&#7895;i th&#225;ng"),
]

cards_row2 = [
    kpi_card(C_GREEN, "T&#7893;ng T&#259;ng Tr&#432;&#7903;ng",
             fpc(total_growth), C_GREEN,
             f"T&#7915; {fp(first_close)} &rarr; {fp(last_close)}"),

    kpi_card(C_RED, "&#272;&#225;y Th&#7845;p Nh&#7845;t",
             fp(atl_price), C_RED,
             atl_date),

    kpi_card(C_RED, "Th&#225;ng Gi&#7843;m M&#7841;nh Nh&#7845;t",
             fpc(worst_month_ret), C_RED,
             worst_month_lbl),

    kpi_card(C_RED, "N&#259;m Gi&#7843;m M&#7841;nh Nh&#7845;t",
             fpc(worst_year_ret), C_RED,
             worst_year_lbl),

    kpi_card(C_RED, "Drawdown T&#7889;i &#272;a",
             fpc(max_dd), C_RED,
             max_dd_date),
]

all_cards = "".join(cards_row1) + "".join(cards_row2)

# ── 6. Build full section HTML ────────────────────────────────────────────────
NEW_SECTION = f"""<!-- Section 1: KPI -->
  <style>
    /* KPI Section 1 v3 */
    .kpi1-grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
    }}
    @media (max-width: 1100px) {{
      .kpi1-grid {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    @media (max-width: 720px) {{
      .kpi1-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
    @media (max-width: 420px) {{
      .kpi1-grid {{ grid-template-columns: 1fr; }}
    }}
    .kpi1-card {{
      background: #FFFFFF;
      border: 1px solid #E5E7EB;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0,0,0,0.04);
      transition: transform .15s, box-shadow .15s;
    }}
    .kpi1-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.09);
    }}
    .kpi1-bar {{
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12.5px;
      font-weight: 700;
      color: #FFFFFF;
      letter-spacing: 0.25px;
      padding: 0 10px;
      text-align: center;
      font-family: {FONT};
    }}
    .kpi1-body {{
      padding: 18px 12px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      min-height: 80px;
      justify-content: center;
    }}
    .kpi1-val {{
      font-size: 30px;
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.5px;
      margin-bottom: 5px;
      font-family: {FONT};
    }}
    .kpi1-sub {{
      font-size: 11.5px;
      color: #6B7280;
      text-align: center;
      font-family: {FONT};
      line-height: 1.4;
    }}
  </style>

  <div class="section">
    <div class="section-title">Section 1 &mdash; Ch&#7881; S&#7889; Hi&#7879;u Su&#7845;t Ch&#237;nh</div>
    <div class="kpi1-grid">
      {all_cards}
    </div>
  </div>

  """

# ── 7. Inject into HTML ───────────────────────────────────────────────────────
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

S_MARK = "<!-- Section 1: KPI -->"
E_MARK = "<!-- Section 2: Price Trend -->"

s = html.find(S_MARK)
e = html.find(E_MARK, s)

if s == -1 or e == -1:
    print(f"[ERROR] Markers not found (s={s}, e={e})")
    sys.exit(1)

html = html[:s] + NEW_SECTION + html[e:]
print(f"    Injected Section 1 (s={s})")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"[OK] Saved: {TARGET} ({size_mb:.1f} MB)")
print("Ctrl+Shift+R to refresh browser.")
