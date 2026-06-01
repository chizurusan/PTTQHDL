"""
Rebuild Section 5 — Return & Growth Analysis
4 cards rieng biet:
  Card 1: Monthly Return (%) bar chart
  Card 2: Yearly Return (%) bar chart + labels
  Card 3: Monthly Return Heatmap (year x month)
  Card 4: Cumulative Growth Index area chart
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
C_BG     = "#F8FAFC"
C_TEXT   = "#111827"
C_MUTED  = "#6B7280"
C_GRID   = "#E5E7EB"
C_BORDER = "#E5E7EB"
C_UP     = "#10B981"   # green
C_DOWN   = "#EF4444"   # red
C_BTC    = "#F59E0B"   # amber
FONT     = "'Segoe UI', system-ui, -apple-system, sans-serif"

def base_layout(height=320, extra_margin=None):
    m = dict(l=56, r=24, t=16, b=52)
    if extra_margin:
        m.update(extra_margin)
    return dict(
        paper_bgcolor=C_WHITE,
        plot_bgcolor=C_WHITE,
        font=dict(family=FONT, size=14, color=C_TEXT),
        margin=m,
        showlegend=False,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=C_WHITE, bordercolor=C_BORDER,
            font=dict(family=FONT, size=14, color=C_TEXT),
        ),
        height=height,
    )

def axis_style(tick_suffix="", dtick=None, tick_format=None):
    d = dict(
        showgrid=True, gridcolor=C_GRID, gridwidth=1,
        linecolor=C_BORDER, linewidth=1,
        tickfont=dict(color="#475569", size=14),
    )
    if tick_suffix:
        d["ticksuffix"] = tick_suffix
    if dtick:
        d["dtick"] = dtick
    if tick_format:
        d["tickformat"] = tick_format
    return d

# ── 1. Load data ──────────────────────────────────────────────────────────────
print("[+] Loading data...")
df = pd.read_csv(CSV, parse_dates=["open_time"])
df = df.rename(columns={"open_time":"Date","open":"Open","high":"High",
                         "low":"Low","close":"Close","volume":"Volume"})
df = df[["Date","Open","Close","Volume"]]
df = df[(df["Date"] >= "2018-01-01") & (df["Date"] <= "2026-05-31")]
df = df.sort_values("Date").reset_index(drop=True)
print(f"    Rows: {len(df)} ({df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()})")

# Monthly close
monthly = (
    df.set_index("Date")["Close"]
    .resample("MS").last()
    .reset_index()
    .rename(columns={"Close":"Close"})
)
monthly["Return"] = monthly["Close"].pct_change() * 100
monthly = monthly.dropna(subset=["Return"]).reset_index(drop=True)
monthly["Year"]  = monthly["Date"].dt.year
monthly["Month"] = monthly["Date"].dt.month

# Yearly close
yearly = (
    df.set_index("Date")["Close"]
    .resample("YS").last()
    .reset_index()
    .rename(columns={"Close":"Close"})
)
yearly["Return"] = yearly["Close"].pct_change() * 100
yearly = yearly.dropna(subset=["Return"]).reset_index(drop=True)
yearly["Year"] = yearly["Date"].dt.year

# Growth Index (daily cumulative)
df["DailyRet"]   = df["Close"].pct_change().fillna(0)
df["GrowthIndex"] = (1 + df["DailyRet"]).cumprod()

print(f"    Monthly: {len(monthly)} | Yearly: {len(yearly)}")

# ── CHART 1: Monthly Return Bar ───────────────────────────────────────────────
print("[+] Building Chart 1 — Monthly Return...")

colors_m = [C_UP if r >= 0 else C_DOWN for r in monthly["Return"]]

fig1 = go.Figure(go.Bar(
    x=monthly["Date"],
    y=monthly["Return"],
    marker=dict(
        color=colors_m,
        line=dict(width=0),
    ),
    hovertemplate=(
        "<b>Th&#225;ng %{x|%Y-%m}</b><br>"
        "L&#7907;i nhu&#7853;n: %{y:+.2f}%"
        "<extra></extra>"
    ),
))

fig1.update_layout(**base_layout(height=460))
fig1.update_xaxes(**axis_style(dtick="M12", tick_format="%Y"))
fig1.update_yaxes(
    **axis_style(tick_suffix="%"),
    zeroline=True, zerolinecolor="#94A3B8", zerolinewidth=1.5,
)

# ── CHART 2: Yearly Return Bar with labels ────────────────────────────────────
print("[+] Building Chart 2 — Yearly Return...")

colors_y = [C_UP if r >= 0 else C_DOWN for r in yearly["Return"]]
text_y = [f"+{r:.0f}%" if r >= 0 else f"{r:.0f}%" for r in yearly["Return"]]

y_min = yearly["Return"].min()
y_max = yearly["Return"].max()
# Asymmetric range: padding proportional to each side, not the larger one
range_lo = -100
range_hi = y_max * 1.28                        # room for label above tallest bar

fig2 = go.Figure(go.Bar(
    x=yearly["Year"].astype(str),
    y=yearly["Return"],
    marker=dict(
        color=colors_y,
        line=dict(width=0),
    ),
    text=text_y,
    textposition="outside",
    textfont=dict(size=17, color=C_TEXT, family=FONT),
    hovertemplate=(
        "<b>N&#259;m %{x}</b><br>"
        "L&#7907;i nhu&#7853;n: %{y:+.1f}%"
        "<extra></extra>"
    ),
    cliponaxis=False,
))

_lo2 = base_layout(height=460, extra_margin=dict(l=56, r=24, t=48, b=52))
_lo2["hovermode"] = "closest"
fig2.update_layout(**_lo2)
fig2.update_xaxes(
    showgrid=False,
    linecolor=C_BORDER, linewidth=1,
    tickfont=dict(color=C_MUTED, size=15),
    zeroline=False,
)
fig2.update_yaxes(
    **axis_style(tick_suffix="%"),
    zeroline=True, zerolinecolor="#94A3B8", zerolinewidth=1.5,
    range=[range_lo, range_hi],
)

# ── CHART 3: Monthly Return Heatmap ──────────────────────────────────────────
print("[+] Building Chart 3 — Monthly Return Heatmap...")

MONTH_LABELS_VN = ["Th1","Th2","Th3","Th4","Th5","Th6",
                    "Th7","Th8","Th9","Th10","Th11","Th12"]

pivot = monthly.pivot(index="Year", columns="Month", values="Return")
years_list = sorted(pivot.index.tolist())

# Original colorscale (soft diverging)
COLORSCALE_HM = [
    [0.00, "#F87171"],  # red-400   at -50%
    [0.20, "#FCA5A5"],  # red-300   at -30%
    [0.38, "#FEE2E2"],  # red-100   at -12%
    [0.50, "#F9FAFB"],  # near-white at 0%
    [0.62, "#DCFCE7"],  # green-100 at +12%
    [0.80, "#86EFAC"],  # green-300 at +30%
    [1.00, "#4ADE80"],  # green-400 at +50%
]

z_matrix  = []
txt_matrix = []
for yr in years_list:
    z_row, t_row = [], []
    for m in range(1, 13):
        if m in pivot.columns and yr in pivot.index and not pd.isna(pivot.loc[yr, m]):
            val  = round(pivot.loc[yr, m], 2)
            sign = "+" if val >= 0 else ""
            z_row.append(val)
            t_row.append(f"{sign}{val:.1f}%")
        else:
            z_row.append(None)
            t_row.append("")
    z_matrix.append(z_row)
    txt_matrix.append(t_row)

y_labels  = [str(y) for y in years_list]
n_years   = len(years_list)
hm_height = max(340, n_years * 44 + 80)

fig3 = go.Figure(go.Heatmap(
    z=z_matrix,
    x=MONTH_LABELS_VN,
    y=y_labels,
    text=txt_matrix,
    texttemplate="<b>%{text}</b>",
    textfont=dict(size=14, family=FONT, color="#111827"),
    colorscale=COLORSCALE_HM,
    zmid=0, zmin=-50, zmax=50,
    showscale=True,
    colorbar=dict(
        len=0.85, thickness=13,
        x=1.005, y=0.5,
        title=dict(text="T&#7927; su&#7845;t l&#7907;i nhu&#7853;n (%)", font=dict(size=11, color=C_MUTED)),
        tickfont=dict(size=10, color=C_MUTED),
        ticksuffix="%",
        tickvals=[-40, -20, 0, 20, 40],
    ),
    xgap=3, ygap=3,
    hoverongaps=False,
    hovertemplate=(
        "<b>N&#259;m %{y} &mdash; %{x}</b><br>"
        "L&#7907;i nhu&#7853;n: %{z:+.2f}%"
        "<extra></extra>"
    ),
))

_lo3 = base_layout(height=hm_height, extra_margin=dict(l=60, r=100, t=16, b=44))
_lo3["hovermode"] = "closest"
fig3.update_layout(**_lo3)
fig3.update_xaxes(
    side="bottom",
    linecolor=C_BORDER,
    tickfont=dict(color="#484d57", size=13),
    showgrid=False,
    fixedrange=True,
)
fig3.update_yaxes(
    autorange="reversed",
    linecolor=C_BORDER,
    tickfont=dict(color="#484d57", size=12),
    showgrid=False,
    fixedrange=True,
)

# ── CHART 4: Cumulative Growth Index ─────────────────────────────────────────
print("[+] Building Chart 4 — Growth Index...")

last_val  = round(df["GrowthIndex"].iloc[-1], 3)
last_date = df["Date"].iloc[-1]
cum_ret   = round((last_val - 1) * 100, 1)

fig4 = go.Figure()

# Shaded area
fig4.add_trace(go.Scatter(
    x=df["Date"],
    y=df["GrowthIndex"],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(245,158,11,0.10)",
    line=dict(color=C_BTC, width=2.5),
    customdata=((df["GrowthIndex"] - 1) * 100).values,
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "Ch&#7881; s&#7889; t&#259;ng tr&#432;&#7903;ng: %{y:.3f}x<br>"
        "T&#237;ch l&#361;y: +%{customdata:.1f}%"
        "<extra></extra>"
    ),
    name="Growth Index",
))

# End-point dot
fig4.add_trace(go.Scatter(
    x=[last_date],
    y=[last_val],
    mode="markers",
    marker=dict(color=C_BTC, size=9, line=dict(color=C_WHITE, width=2)),
    hoverinfo="skip",
    showlegend=False,
))

# Annotation at end point
fig4.add_annotation(
    x=last_date,
    y=last_val,
    text=f"<b>{last_val:.2f}x</b>",
    showarrow=True,
    arrowhead=2,
    arrowwidth=1.5,
    arrowcolor=C_BTC,
    ax=-60, ay=-30,
    font=dict(size=13, color=C_BTC, family=FONT),
    bgcolor=C_WHITE,
    bordercolor=C_BTC,
    borderwidth=1.5,
    borderpad=6,
    opacity=0.95,
)

# $1 reference annotation at start
fig4.add_annotation(
    x=df["Date"].iloc[0],
    y=1.0,
    text="Start: $1",
    showarrow=False,
    font=dict(size=10, color=C_MUTED, family=FONT),
    xanchor="left",
    yanchor="bottom",
    yshift=4,
)

_lo4 = base_layout(height=360, extra_margin=dict(l=52, r=40, t=16, b=44))
_lo4["hovermode"] = "x"
fig4.update_layout(**_lo4)
fig4.update_xaxes(**axis_style())
fig4.update_yaxes(
    **axis_style(tick_suffix="x"),
    tickvals=[1, 2, 3, 4, 5, 6, 7, 8],
)

# ── Export divs ───────────────────────────────────────────────────────────────
print("[+] Exporting HTML divs...")

CFG_NONE = {"displayModeBar": False, "responsive": True}
CFG_ZOOM = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "toImage","lasso2d","select2d","autoScale2d","zoom2d","pan2d",
    ],
    "responsive": True,
}

div1 = pio.to_html(fig1, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s5-monthly")
div2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s5-yearly")
div3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False,
                   config=CFG_ZOOM, div_id="chart-s5-heatmap")
div4 = pio.to_html(fig4, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s5-growth")

# ── Build section HTML ────────────────────────────────────────────────────────
FONT_CSS  = "'Segoe UI', system-ui, -apple-system, sans-serif"
C_TITLE   = f"font-size:22px;font-weight:700;color:#D97706;margin-bottom:6px;font-family:{FONT_CSS};"
C_SUB_CSS = f"font-size:15px;color:#6B7280;margin-bottom:14px;font-family:{FONT_CSS};line-height:1.5;"
CARD      = (
    "background:#FFFFFF;border:1px solid #E5E7EB;border-radius:18px;"
    "padding:24px 24px 14px;box-shadow:0 4px 12px rgba(0,0,0,0.04);"
    "margin-bottom:30px;"
)

NEW_SECTION = f"""<!-- Section 5: Returns -->
  <div class="section">
    <div class="section-title">Section 5 &mdash; Ph&#226;n t&#237;ch l&#7907;i nhu&#7853;n &amp; t&#259;ng tr&#432;&#7903;ng</div>

    <!-- Card 1: Monthly Return — full width -->
    <div style="{CARD}">
      <div style="{C_TITLE}">L&#7907;i nhu&#7853;n theo th&#225;ng (%)</div>
      <div style="{C_SUB_CSS}">
        T&#7927; su&#7845;t l&#7907;i nhu&#7853;n theo th&#225;ng giai &#273;o&#7841;n 2018&ndash;2026
        &mdash; <span style="color:#10B981;font-weight:600;">xanh l&#224; t&#259;ng</span>,
        <span style="color:#EF4444;font-weight:600;">&#273;&#7887; l&#224; gi&#7843;m</span>
      </div>
      {div1}
    </div>

    <!-- Card 2: Yearly Return — full width -->
    <div style="{CARD}">
      <div style="{C_TITLE}">L&#7907;i nhu&#7853;n theo n&#259;m (%)</div>
      <div style="{C_SUB_CSS}">
        Hi&#7879;u su&#7845;t Bitcoin theo t&#7915;ng n&#259;m, c&#243; nh&#227;n ph&#7847;n tr&#259;m tr&#234;n m&#7895;i c&#7897;t
      </div>
      {div2}
    </div>

    <!-- Card 3: Monthly Return Heatmap — full width -->
    <div style="{CARD}">
      <div style="{C_TITLE}">B&#7843;ng nhi&#7879;t &mdash; L&#7907;i nhu&#7853;n Bitcoin theo th&#225;ng</div>
      <div style="{C_SUB_CSS}">
        So s&#225;nh t&#7927; su&#7845;t l&#7907;i nhu&#7853;n theo t&#7915;ng th&#225;ng v&#224; t&#7915;ng n&#259;m.
        M&#224;u xanh l&#224; th&#225;ng t&#259;ng, m&#224;u &#273;&#7887; l&#224; th&#225;ng gi&#7843;m.
      </div>
      {div3}
    </div>

    <!-- Card 4: Growth Index — full width -->
    <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:18px;padding:24px 24px 14px;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
      <div style="{C_TITLE}">Ch&#7881; s&#7889; t&#259;ng tr&#432;&#7903;ng t&#237;ch l&#361;y</div>
      <div style="{C_SUB_CSS}">
        Gi&#225; tr&#7883; c&#7911;a $1 &#273;&#7847;u t&#432; t&#7915; th&#225;ng 1/2018 &mdash;
        hi&#7879;n t&#7841;i:
        <strong style="color:#F59E0B;">{last_val:.2f}x (+{cum_ret:.0f}%)</strong>
      </div>
      {div4}
    </div>

  </div>

  """

# ── Inject into HTML ──────────────────────────────────────────────────────────
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

S_MARK = "<!-- Section 5: Returns -->"
E_MARK = "<!-- Section 6: Risk -->"

s = html.find(S_MARK)
e = html.find(E_MARK, s)

if s == -1 or e == -1:
    print(f"[ERROR] Markers not found (s={s}, e={e})")
    sys.exit(1)

html = html[:s] + NEW_SECTION + html[e:]
print(f"    Injected Section 5 (s={s})")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"[OK] Saved: {TARGET} ({size_mb:.1f} MB)")

# ── Fix bdata ─────────────────────────────────────────────────────────────────
print("[+] Running fix_bdata.py...")
subprocess.run([sys.executable, "fix_bdata.py"], check=True)
print("[+] Running fix_heatmap.py...")
subprocess.run([sys.executable, "fix_heatmap.py"], check=True)

print(f"\n[DONE] Section 5 rebuilt — {last_val:.2f}x growth (+{cum_ret:.0f}%).")
print("Ctrl+Shift+R to refresh browser.")
