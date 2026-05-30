"""
Rebuild Section 4 — Financial Charts (Candlestick / OHLC / Volume)
Tach thanh 2 card rieng biet:
  Card 1: Candlestick + Volume (2 row subplots, shared x)
  Card 2: OHLC + Volume (2 row subplots, shared x)
Time-filter dropdown: Daily / Weekly / Monthly / Yearly
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import subprocess, sys

TARGET  = "bitcoin_dashboard copy 2.html"
CSV     = "bitcoin_data/btc_daily.csv"

# ── Colors ────────────────────────────────────────────────────────────────────
C_WHITE  = "#FFFFFF"
C_BG     = "#F8FAFC"
C_TEXT   = "#334155"
C_TITLE  = "#0F172A"
C_MUTED  = "#64748B"
C_GRID   = "rgba(148,163,184,0.25)"
C_BORDER = "#CBD5E1"
C_BTC    = "#F59E0B"
C_UP     = "#16A34A"   # green candle / volume up
C_DOWN   = "#DC2626"   # red candle / volume down

FONT_FAMILY = "'Segoe UI', system-ui, -apple-system, sans-serif"

# ── 1. Load & filter data ─────────────────────────────────────────────────────
print("[+] Loading data...")
df = pd.read_csv(CSV, parse_dates=["open_time"])
df = df.rename(columns={
    "open_time": "Date",
    "open":  "Open",
    "high":  "High",
    "low":   "Low",
    "close": "Close",
    "volume": "Volume",
})
df = df[["Date","Open","High","Low","Close","Volume"]].copy()
df["Date"] = pd.to_datetime(df["Date"])
df = df[(df["Date"] >= "2018-01-01") & (df["Date"] <= "2026-05-31")]
df = df.sort_values("Date").reset_index(drop=True)
print(f"    Daily rows: {len(df)}  ({df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()})")

# ── 2. Resample helper ────────────────────────────────────────────────────────
def resample_ohlcv(df_in, rule):
    rs = df_in.set_index("Date").resample(rule).agg(
        Open=("Open","first"),
        High=("High","max"),
        Low=("Low","min"),
        Close=("Close","last"),
        Volume=("Volume","sum"),
    ).dropna(subset=["Open"]).reset_index()
    return rs

weekly  = resample_ohlcv(df, "W-MON")
monthly = resample_ohlcv(df, "MS")
yearly  = resample_ohlcv(df, "YS")
print(f"    Weekly: {len(weekly)} | Monthly: {len(monthly)} | Yearly: {len(yearly)}")

# ── 3. Volume bar colors ───────────────────────────────────────────────────────
def vol_colors(d):
    return [C_UP if c >= o else C_DOWN for o, c in zip(d["Open"], d["Close"])]

FRAMES = [
    ("Daily",   df),
    ("Weekly",  weekly),
    ("Monthly", monthly),
    ("Yearly",  yearly),
]

# ── 4. Format helpers for hover ───────────────────────────────────────────────
def fmt_price(s):
    return [f"${v:,.0f}" for v in s]

def fmt_vol(s):
    out = []
    for v in s:
        if v >= 1e9:
            out.append(f"{v/1e9:.2f}B")
        elif v >= 1e6:
            out.append(f"{v/1e6:.2f}M")
        elif v >= 1e3:
            out.append(f"{v/1e3:.1f}K")
        else:
            out.append(f"{v:.0f}")
    return out

def hover_candle(d, lbl):
    dates = d["Date"].dt.strftime("%Y-%m-%d")
    texts = []
    for i, row in d.iterrows():
        texts.append(
            f"<b>{dates.iloc[i]}</b><br>"
            f"Open:  ${row.Open:,.0f}<br>"
            f"High:  ${row.High:,.0f}<br>"
            f"Low:   ${row.Low:,.0f}<br>"
            f"Close: ${row.Close:,.0f}"
        )
    return texts

def hover_vol(d):
    vols = fmt_vol(d["Volume"])
    dates = d["Date"].dt.strftime("%Y-%m-%d")
    return [f"<b>{dates.iloc[i]}</b><br>Volume: {vols[i]}" for i in range(len(d))]

# ── 5. BASE LAYOUT HELPER ─────────────────────────────────────────────────────
_LEGEND = dict(
    orientation="h",
    x=0, y=1.04,
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor=C_BORDER,
    borderwidth=1,
    font=dict(family=FONT_FAMILY, size=11, color=C_TEXT),
)

def apply_layout(fig, title_text, rows=2):
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(family=FONT_FAMILY, size=16, color=C_TITLE),
            x=0.5, xanchor="center",
        ),
        paper_bgcolor=C_WHITE,
        plot_bgcolor=C_WHITE,
        font=dict(family=FONT_FAMILY, size=11, color=C_TEXT),
        legend=_LEGEND,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=C_WHITE,
            bordercolor=C_BORDER,
            font=dict(family=FONT_FAMILY, size=11, color=C_TITLE),
        ),
        margin=dict(l=60, r=30, t=80, b=50),
    )
    for r in range(1, rows + 1):
        fig.update_xaxes(
            row=r,
            showgrid=True, gridcolor=C_GRID, gridwidth=1,
            linecolor=C_BORDER, linewidth=1,
            tickcolor=C_BORDER,
            tickfont=dict(family=FONT_FAMILY, size=10, color=C_MUTED),
            rangeslider_visible=False,
        )
        fig.update_yaxes(
            row=r,
            showgrid=True, gridcolor=C_GRID, gridwidth=1,
            linecolor=C_BORDER, linewidth=1,
            tickcolor=C_BORDER,
            tickfont=dict(family=FONT_FAMILY, size=10, color=C_MUTED),
            zerolinecolor=C_BORDER,
        )
    # Price axis: $ prefix
    fig.update_yaxes(row=1, tickprefix="$", separatethousands=True)

# ── 6. Build dropdown ─────────────────────────────────────────────────────────
# Traces order:  [daily_candle, daily_vol, weekly_candle, weekly_vol,
#                 monthly_candle, monthly_vol, yearly_candle, yearly_vol]
# visibility list for each button: True/False per trace

def make_visibility(active_idx, n_tf=4):
    """active_idx 0-3, each tf has 2 traces (candle/ohlc + vol)"""
    vis = []
    for i in range(n_tf):
        vis += [i == active_idx, i == active_idx]
    return vis

DROPDOWN_BUTTONS = []
for idx, (label, _) in enumerate(FRAMES):
    DROPDOWN_BUTTONS.append(dict(
        label=label,
        method="update",
        args=[{"visible": make_visibility(idx)}],
    ))

UPDATEMENUS = [dict(
    type="dropdown",
    direction="down",
    x=0.01, y=1.12,
    xanchor="left", yanchor="top",
    bgcolor=C_WHITE,
    bordercolor=C_BORDER,
    font=dict(family=FONT_FAMILY, size=12, color=C_TEXT),
    buttons=DROPDOWN_BUTTONS,
    active=0,
)]

# ── 7. Build CANDLESTICK figure ───────────────────────────────────────────────
print("[+] Building Candlestick + Volume figure...")

fig_candle = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    row_heights=[0.72, 0.28],
    vertical_spacing=0.04,
    subplot_titles=["", ""],  # titles via annotations
)

for i, (label, d) in enumerate(FRAMES):
    visible = (i == 0)
    vc = vol_colors(d)

    # Candlestick
    fig_candle.add_trace(go.Candlestick(
        x=d["Date"],
        open=d["Open"], high=d["High"],
        low=d["Low"],   close=d["Close"],
        increasing=dict(line=dict(color=C_UP, width=1), fillcolor=C_UP),
        decreasing=dict(line=dict(color=C_DOWN, width=1), fillcolor=C_DOWN),
        text=hover_candle(d, label),
        hoverinfo="text",
        name=f"Candle ({label})",
        visible=visible,
        showlegend=True,
    ), row=1, col=1)

    # Volume
    fig_candle.add_trace(go.Bar(
        x=d["Date"],
        y=d["Volume"],
        marker_color=vc,
        opacity=0.75,
        text=hover_vol(d),
        hoverinfo="text",
        name=f"Volume ({label})",
        visible=visible,
        showlegend=True,
    ), row=2, col=1)

apply_layout(fig_candle, "Candlestick Chart — BTC/USDT (2018–2026)")
fig_candle.update_layout(updatemenus=UPDATEMENUS)
fig_candle.update_yaxes(row=2, title_text="Volume", tickprefix="")

# Volume axis: K/M/B ticks
fig_candle.update_yaxes(row=2, tickformat=".2s")

# ── 8. Build OHLC figure ─────────────────────────────────────────────────────
print("[+] Building OHLC + Volume figure...")

fig_ohlc = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    row_heights=[0.72, 0.28],
    vertical_spacing=0.04,
    subplot_titles=["", ""],
)

for i, (label, d) in enumerate(FRAMES):
    visible = (i == 0)
    vc = vol_colors(d)

    # OHLC
    fig_ohlc.add_trace(go.Ohlc(
        x=d["Date"],
        open=d["Open"], high=d["High"],
        low=d["Low"],   close=d["Close"],
        increasing=dict(line=dict(color=C_UP, width=1.2)),
        decreasing=dict(line=dict(color=C_DOWN, width=1.2)),
        text=hover_candle(d, label),
        hoverinfo="text",
        name=f"OHLC ({label})",
        visible=visible,
        showlegend=True,
    ), row=1, col=1)

    # Volume
    fig_ohlc.add_trace(go.Bar(
        x=d["Date"],
        y=d["Volume"],
        marker_color=vc,
        opacity=0.75,
        text=hover_vol(d),
        hoverinfo="text",
        name=f"Volume ({label})",
        visible=visible,
        showlegend=True,
    ), row=2, col=1)

apply_layout(fig_ohlc, "OHLC Chart — BTC/USDT (2018–2026)")
fig_ohlc.update_layout(updatemenus=UPDATEMENUS)
fig_ohlc.update_yaxes(row=2, title_text="Volume", tickprefix="")
fig_ohlc.update_yaxes(row=2, tickformat=".2s")

# ── 9. Export HTML divs ───────────────────────────────────────────────────────
print("[+] Exporting HTML divs...")

div_candle = pio.to_html(
    fig_candle, full_html=False, include_plotlyjs=False,
    config={"responsive": True, "displayModeBar": True,
            "modeBarButtonsToRemove": ["toImage"],
            "displaylogo": False},
    div_id="chart-fin-candle",
)

div_ohlc = pio.to_html(
    fig_ohlc, full_html=False, include_plotlyjs=False,
    config={"responsive": True, "displayModeBar": True,
            "modeBarButtonsToRemove": ["toImage"],
            "displaylogo": False},
    div_id="chart-fin-ohlc",
)

# ── 10. Build new section HTML ────────────────────────────────────────────────
NEW_SECTION = f"""<!-- Section 4: Financial Charts -->
  <div class="section">
    <div class="section-title">Section 4 — Financial Charts (Candlestick / OHLC / Volume)</div>

    <!-- Card 1: Candlestick + Volume -->
    <div style="margin-bottom:24px; background:#FFFFFF; border:1px solid #E2E8F0;
                border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(15,23,42,0.07);">
      <div style="font-size:1em; font-weight:700; color:#0F4C81; margin-bottom:12px;
                  letter-spacing:0.3px;">
        Candlestick + Volume
      </div>
      <div style="height:520px;">
        {div_candle}
      </div>
    </div>

    <!-- Card 2: OHLC + Volume -->
    <div style="background:#FFFFFF; border:1px solid #E2E8F0;
                border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(15,23,42,0.07);">
      <div style="font-size:1em; font-weight:700; color:#0F4C81; margin-bottom:12px;
                  letter-spacing:0.3px;">
        OHLC + Volume
      </div>
      <div style="height:520px;">
        {div_ohlc}
      </div>
    </div>

  </div>

  """

# ── 11. Inject into HTML ──────────────────────────────────────────────────────
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

START_MARKER = "<!-- Section 4: Financial Charts -->"
END_MARKER   = "<!-- Section 5: Returns -->"

s = html.find(START_MARKER)
e = html.find(END_MARKER, s)

if s == -1 or e == -1:
    print(f"[ERROR] Could not locate Section 4 markers (s={s}, e={e})")
    sys.exit(1)

html = html[:s] + NEW_SECTION + html[e:]
print(f"    Injected Section 4  (s={s}, e={e})")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")

# ── 12. Fix bdata ─────────────────────────────────────────────────────────────
print("[+] Running fix_bdata.py...")
subprocess.run([sys.executable, "fix_bdata.py"], check=True)

print("[+] Running fix_heatmap.py...")
subprocess.run([sys.executable, "fix_heatmap.py"], check=True)

print("\n[DONE] Section 4 rebuilt. Ctrl+Shift+R to refresh browser.")
