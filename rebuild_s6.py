"""
Rebuild Section 6 — Risk & Volatility Analysis
3 card rieng biet:
  Card 1: Rolling Volatility 30D  (line + area)
  Card 2: Drawdown tu dinh        (area, red)
  Card 3: Daily Return Distribution by Year (box plot)
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import subprocess, sys

TARGET = "bitcoin_dashboard copy 2.html"
CSV    = "bitcoin_data/btc_daily.csv"

# ── Colors ────────────────────────────────────────────────────────────────────
C_WHITE  = "#FFFFFF"
C_TEXT   = "#111827"
C_MUTED  = "#6B7280"
C_GRID   = "#E5E7EB"
C_BORDER = "#E5E7EB"
C_VOL    = "#3B82F6"   # blue
C_DD     = "#EF4444"   # red
C_BOX    = "#8B5CF6"   # purple
C_BTC    = "#F59E0B"   # amber
FONT     = "'Segoe UI', system-ui, -apple-system, sans-serif"

CARD_STYLE = (
    "background:#FFFFFF;"
    "border:1px solid #E5E7EB;"
    "border-radius:16px;"
    "padding:22px 22px 12px;"
    "box-shadow:0 4px 12px rgba(0,0,0,0.04);"
)
CARD_TITLE = f"font-size:.95em;font-weight:700;color:{C_TEXT};margin-bottom:3px;font-family:{FONT};"
CARD_SUB   = f"font-size:.78em;color:{C_MUTED};margin-bottom:10px;font-family:{FONT};"
BADGE_BASE = (
    "display:inline-block;font-size:.75em;font-family:{font};"
    "padding:3px 10px;border-radius:20px;font-weight:600;"
    "border:1px solid {{border}};background:{{bg}};color:{{color}};"
    "margin-right:6px;margin-bottom:8px;"
).format(font=FONT)

def badge(label, value, color, bg, border):
    return (
        f'<span style="display:inline-block;font-size:.75em;'
        f'font-family:{FONT};padding:3px 10px;border-radius:20px;'
        f'font-weight:600;border:1px solid {border};'
        f'background:{bg};color:{color};margin-right:6px;margin-bottom:8px;">'
        f'{label}: <strong>{value}</strong></span>'
    )

def base_layout(height=340, hovermode="x unified",
                margin=None):
    m = margin or dict(l=56, r=24, t=16, b=48)
    return dict(
        paper_bgcolor=C_WHITE,
        plot_bgcolor=C_WHITE,
        font=dict(family=FONT, size=12, color=C_TEXT),
        margin=m,
        showlegend=False,
        hovermode=hovermode,
        hoverlabel=dict(
            bgcolor=C_WHITE, bordercolor=C_BORDER,
            font=dict(family=FONT, size=12, color=C_TEXT),
        ),
        height=height,
    )

# ── 1. Load data ──────────────────────────────────────────────────────────────
print("[+] Loading data...")
df = pd.read_csv(CSV, parse_dates=["open_time"])
df = df.rename(columns={"open_time":"Date","close":"Close"})
df = df[["Date","Close"]]
df = df[(df["Date"] >= "2018-01-01") & (df["Date"] <= "2026-05-31")]
df = df.sort_values("Date").reset_index(drop=True)

# Derived columns
df["DailyReturn"]  = df["Close"].pct_change() * 100
df["RollingVol"]   = df["DailyReturn"].rolling(30).std()
df["RunningMax"]   = df["Close"].cummax()
df["Drawdown"]     = (df["Close"] - df["RunningMax"]) / df["RunningMax"] * 100
df["Year"]         = df["Date"].dt.year

df_vol  = df.dropna(subset=["RollingVol"]).copy()
df_ret  = df.dropna(subset=["DailyReturn"]).copy()

# Metrics — Volatility
cur_vol  = round(df_vol["RollingVol"].iloc[-1], 2)
avg_vol  = round(df_vol["RollingVol"].mean(), 2)
max_vol  = round(df_vol["RollingVol"].max(), 2)
max_vol_date = df_vol.loc[df_vol["RollingVol"].idxmax(), "Date"].strftime("%Y-%m-%d")

# Metrics — Drawdown
max_dd       = round(df["Drawdown"].min(), 1)
cur_dd       = round(df["Drawdown"].iloc[-1], 1)
max_dd_date  = df.loc[df["Drawdown"].idxmin(), "Date"].strftime("%Y-%m-%d")

print(f"    Vol: cur={cur_vol}%  avg={avg_vol}%  max={max_vol}%")
print(f"    DD:  max={max_dd}%   cur={cur_dd}%  at {max_dd_date}")

# ── CHART 1: Rolling Volatility 30D ──────────────────────────────────────────
print("[+] Building Chart 1 — Rolling Volatility...")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=df_vol["Date"],
    y=df_vol["RollingVol"],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(59,130,246,0.12)",
    line=dict(color=C_VOL, width=2),
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "Rolling Vol 30D: %{y:.2f}%"
        "<extra></extra>"
    ),
))

# Avg reference line
fig1.add_hline(
    y=avg_vol,
    line=dict(color="#64748B", width=1, dash="dot"),
    annotation_text=f"Avg {avg_vol:.2f}%",
    annotation_position="top left",
    annotation_font=dict(size=10, color="#64748B"),
)

fig1.update_layout(**base_layout(height=300))
fig1.update_xaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=dict(color=C_MUTED, size=11),
    zeroline=False,
)
fig1.update_yaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=dict(color=C_MUTED, size=11),
    ticksuffix="%",
    zeroline=True, zerolinecolor=C_GRID, zerolinewidth=1,
    rangemode="tozero",
)

# ── CHART 2: Drawdown from Peak ───────────────────────────────────────────────
print("[+] Building Chart 2 — Drawdown...")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df["Date"],
    y=df["Drawdown"],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(239,68,68,0.16)",
    line=dict(color=C_DD, width=1.5),
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "Drawdown: %{y:.1f}%"
        "<extra></extra>"
    ),
))

# Reference lines at -20%, -50%, -70%
for lvl, lbl in [(-20, "-20%"), (-50, "-50%"), (-70, "-70%")]:
    fig2.add_hline(
        y=lvl,
        line=dict(color="#94A3B8", width=1, dash="dot"),
        annotation_text=lbl,
        annotation_position="top right",
        annotation_font=dict(size=10, color="#94A3B8"),
    )

# Max DD annotation
max_dd_idx = df["Drawdown"].idxmin()
fig2.add_annotation(
    x=df.loc[max_dd_idx, "Date"],
    y=max_dd,
    text=f"<b>Max DD {max_dd:.1f}%</b>",
    showarrow=True,
    arrowhead=2, arrowwidth=1.5, arrowcolor=C_DD,
    ax=60, ay=-30,
    font=dict(size=11, color=C_DD, family=FONT),
    bgcolor=C_WHITE,
    bordercolor=C_DD,
    borderwidth=1.5,
    borderpad=6,
    opacity=0.95,
)

fig2.update_layout(**base_layout(height=300))
fig2.update_xaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=dict(color=C_MUTED, size=11),
    zeroline=False,
)
fig2.update_yaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=dict(color=C_MUTED, size=11),
    ticksuffix="%",
    zeroline=True, zerolinecolor="#94A3B8", zerolinewidth=1.5,
)

# ── CHART 3: Box Plot Daily Return by Year ────────────────────────────────────
print("[+] Building Chart 3 — Box Plot by Year...")

years = sorted(df_ret["Year"].unique())

# Gradient colors: from purple-400 (#C084FC) to indigo-600 (#4F46E5)
# Interpolate over n years
n = len(years)
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def interp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return (
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )

fig3 = go.Figure()

for i, yr in enumerate(years):
    yr_data = df_ret[df_ret["Year"] == yr]["DailyReturn"].dropna()
    t = i / max(n - 1, 1)
    r, g, b = interp_color("#A78BFA", "#3B82F6", t)  # purple-400 → blue-500
    clr = f"rgb({r},{g},{b})"
    clr_light = f"rgba({r},{g},{b},0.25)"

    fig3.add_trace(go.Box(
        y=yr_data,
        name=str(yr),
        boxpoints="outliers",
        marker=dict(
            color=clr,
            size=3,
            opacity=0.45,
        ),
        line=dict(color=clr, width=1.5),
        fillcolor=clr_light,
        whiskerwidth=0.6,
        hovertemplate=(
            f"<b>{yr}</b><br>"
            "Median: %{median:.3f}%<br>"
            "Q1: %{q1:.3f}%<br>"
            "Q3: %{q3:.3f}%<br>"
            "Min: %{lowerfence:.3f}%<br>"
            "Max: %{upperfence:.3f}%"
            "<extra></extra>"
        ),
    ))

# Baseline at 0%
fig3.add_hline(
    y=0,
    line=dict(color="#94A3B8", width=1.5, dash="dash"),
)

fig3.update_layout(**base_layout(height=380, hovermode="closest"))
fig3.update_xaxes(
    linecolor=C_BORDER, tickfont=dict(color=C_MUTED, size=12),
    showgrid=False, zeroline=False,
)
fig3.update_yaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=dict(color=C_MUTED, size=11),
    ticksuffix="%",
    zeroline=False,
)

# ── Export divs ───────────────────────────────────────────────────────────────
print("[+] Exporting HTML divs...")

CFG_NONE = {"displayModeBar": False, "responsive": True}
CFG_ZOOM = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "toImage","lasso2d","select2d","autoScale2d",
    ],
    "responsive": True,
}

div1 = pio.to_html(fig1, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s6-vol")
div2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s6-dd")
div3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False,
                   config=CFG_ZOOM, div_id="chart-s6-box")

# ── Build badge HTML ──────────────────────────────────────────────────────────
badges_vol = (
    badge("Current Vol",f"{cur_vol:.2f}%","#1D4ED8","#EFF6FF","#BFDBFE") +
    badge("Avg Vol",    f"{avg_vol:.2f}%","#374151","#F9FAFB","#E5E7EB") +
    badge("Max Vol",    f"{max_vol:.2f}%","#7C3AED","#F5F3FF","#DDD6FE")
)
badges_dd = (
    badge("Max DD",     f"{max_dd:.1f}%", "#B91C1C","#FEF2F2","#FCA5A5") +
    badge("Current DD", f"{cur_dd:.1f}%", "#374151","#F9FAFB","#E5E7EB") +
    badge("Date",       max_dd_date,      "#6B7280","#F9FAFB","#E5E7EB")
)

# ── Build section HTML ────────────────────────────────────────────────────────
NEW_SECTION = f"""<!-- Section 6: Risk -->
  <style>
    .s6-grid-2col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }}
    @media (max-width: 820px) {{
      .s6-grid-2col {{ grid-template-columns: 1fr; }}
    }}
  </style>

  <div class="section">
    <div class="section-title">Section 6 &mdash; Risk &amp; Volatility</div>

    <!-- Row 1: Vol + Drawdown (2 columns) -->
    <div class="s6-grid-2col">

      <!-- Card 1: Rolling Volatility -->
      <div style="{CARD_STYLE}">
        <div style="{CARD_TITLE}">Rolling Volatility 30D</div>
        <div style="margin-bottom:8px;">{badges_vol}</div>
        <div style="{CARD_SUB}">
          30-day rolling standard deviation of daily return &mdash;
          higher = more volatile period
        </div>
        {div1}
      </div>

      <!-- Card 2: Drawdown -->
      <div style="{CARD_STYLE}">
        <div style="{CARD_TITLE}">Drawdown from Peak</div>
        <div style="margin-bottom:8px;">{badges_dd}</div>
        <div style="{CARD_SUB}">
          % decline from the most recent all-time high &mdash;
          deeper = higher risk period
        </div>
        {div2}
      </div>

    </div>

    <!-- Row 2: Box Plot (full width) -->
    <div style="{CARD_STYLE}">
      <div style="{CARD_TITLE}">Daily Return Distribution by Year</div>
      <div style="{CARD_SUB}">
        Box plot of daily returns per year &mdash; wider box = higher volatility year.
        Dots are outlier days. Dashed line at 0%.
      </div>
      {div3}
    </div>

  </div>

  """

# ── Inject into HTML ──────────────────────────────────────────────────────────
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

S_MARK = "<!-- Section 6: Risk -->"
E_MARK = "<!-- Section 7: Insights -->"

s = html.find(S_MARK)
e = html.find(E_MARK, s)

if s == -1 or e == -1:
    print(f"[ERROR] Markers not found (s={s}, e={e})")
    sys.exit(1)

html = html[:s] + NEW_SECTION + html[e:]
print(f"    Injected Section 6 (s={s})")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"[OK] Saved: {TARGET} ({size_mb:.1f} MB)")

# ── Fix bdata ─────────────────────────────────────────────────────────────────
print("[+] Running fix_bdata.py...")
subprocess.run([sys.executable, "fix_bdata.py"], check=True)
print("[+] Running fix_heatmap.py...")
subprocess.run([sys.executable, "fix_heatmap.py"], check=True)

print("\n[DONE] Section 6 rebuilt.")
print(f"  Vol: cur={cur_vol}%  avg={avg_vol}%  max={max_vol}%")
print(f"  DD:  max={max_dd}%  cur={cur_dd}%  at {max_dd_date}")
print("Ctrl+Shift+R to refresh browser.")
