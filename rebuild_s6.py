"""
Rebuild Section 6 — Phan tich rui ro & bien dong gia BTC
1 card lon duy nhat chua 3 bieu do:
  Row 1 (2 cot): Bien dong lan 30 ngay | Muc sut giam tu dinh
  Row 2 (full width): Phan phoi loi suat ngay theo nam (box plot)
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import subprocess, sys

TARGET = "bitcoin_dashboard copy 2.html"
CSV    = "bitcoin_data/btc_daily.csv"

# ── Colors ─────────────────────────────────────────────────────────────────────
C_WHITE  = "#FFFFFF"
C_TEXT   = "#111827"
C_MUTED  = "#6B7280"
C_GRID   = "#F1F5F9"
C_BORDER = "#E5E7EB"
C_VOL    = "#3B82F6"   # blue
C_DD     = "#EF4444"   # red
FONT     = "'Segoe UI', system-ui, -apple-system, sans-serif"

TICK_FONT = dict(color="#475569", size=13, family=FONT)

def base_layout(height=290, hovermode="x unified", margin=None):
    m = margin or dict(l=52, r=20, t=14, b=44)
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

# ── 1. Load data ───────────────────────────────────────────────────────────────
print("[+] Loading data...")
df = pd.read_csv(CSV, parse_dates=["open_time"])
df = df.rename(columns={"open_time": "Date", "close": "Close"})
df = df[["Date", "Close"]]
df = df[(df["Date"] >= "2018-01-01") & (df["Date"] <= "2026-05-31")]
df = df.sort_values("Date").reset_index(drop=True)

df["DailyReturn"] = df["Close"].pct_change() * 100
df["RollingVol"]  = df["DailyReturn"].rolling(30).std()
df["RunningMax"]  = df["Close"].cummax()
df["Drawdown"]    = (df["Close"] - df["RunningMax"]) / df["RunningMax"] * 100
df["Year"]        = df["Date"].dt.year

df_vol = df.dropna(subset=["RollingVol"]).copy()
df_ret = df.dropna(subset=["DailyReturn"]).copy()

# Metrics
cur_vol      = round(df_vol["RollingVol"].iloc[-1], 2)
avg_vol      = round(df_vol["RollingVol"].mean(), 2)
max_vol      = round(df_vol["RollingVol"].max(), 2)
max_vol_date = df_vol.loc[df_vol["RollingVol"].idxmax(), "Date"].strftime("%d/%m/%Y")
max_dd       = round(df["Drawdown"].min(), 1)
cur_dd       = round(df["Drawdown"].iloc[-1], 1)
max_dd_date  = df.loc[df["Drawdown"].idxmin(), "Date"].strftime("%d/%m/%Y")

print(f"    Vol: cur={cur_vol}%  avg={avg_vol}%  max={max_vol}%  ({max_vol_date})")
print(f"    DD:  max={max_dd}%   cur={cur_dd}%   ({max_dd_date})")

# ── CHART 1: Bien dong lan 30 ngay ────────────────────────────────────────────
print("[+] Building Chart 1 — Bien dong lan 30 ngay...")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=df_vol["Date"],
    y=df_vol["RollingVol"],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(59,130,246,0.10)",
    line=dict(color=C_VOL, width=2),
    hovertemplate=(
        u"<b>Ngày %{x|%d/%m/%Y}</b><br>"
        u"Biến động 30 ngày: %{y:.2f}%"
        "<extra></extra>"
    ),
))

fig1.add_hline(
    y=avg_vol,
    line=dict(color="#94A3B8", width=1, dash="dot"),
    annotation_text=u"Trung bình {:.2f}%".format(avg_vol),
    annotation_position="top left",
    annotation_font=dict(size=10, color="#64748B", family=FONT),
)

fig1.update_layout(**base_layout(height=290))
fig1.update_xaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=TICK_FONT, zeroline=False,
)
fig1.update_yaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=TICK_FONT,
    ticksuffix="%", rangemode="tozero",
    zeroline=True, zerolinecolor=C_GRID, zerolinewidth=1,
)

# ── CHART 2: Muc sut giam tu dinh ─────────────────────────────────────────────
print("[+] Building Chart 2 — Sut giam tu dinh...")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df["Date"],
    y=df["Drawdown"],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(239,68,68,0.11)",
    line=dict(color=C_DD, width=1.5),
    hovertemplate=(
        u"<b>Ngày %{x|%d/%m/%Y}</b><br>"
        u"Mức sụt giảm: %{y:.1f}%"
        "<extra></extra>"
    ),
))

# Duong tham chieu voi mo ta tieng Viet
for lvl, lbl in [
    (-20, u"−20%  ·  Điều chỉnh mạnh"),
    (-50, u"−50%  ·  Suy giảm sâu"),
    (-70, u"−70%  ·  Rủi ro cực cao"),
]:
    fig2.add_hline(
        y=lvl,
        line=dict(color="#CBD5E1", width=1, dash="dot"),
        annotation_text=lbl,
        annotation_position="top right",
        annotation_font=dict(size=9, color="#94A3B8", family=FONT),
    )

# Annotation max drawdown
max_dd_idx = df["Drawdown"].idxmin()
fig2.add_annotation(
    x=df.loc[max_dd_idx, "Date"],
    y=max_dd,
    text=u"<b>Sụt giảm lớn nhất: {:.1f}%</b>".format(max_dd),
    showarrow=True,
    arrowhead=2, arrowwidth=1.5, arrowcolor=C_DD,
    ax=72, ay=-28,
    font=dict(size=11, color=C_DD, family=FONT),
    bgcolor=C_WHITE,
    bordercolor=C_DD, borderwidth=1.5, borderpad=6,
    opacity=0.95,
)

fig2.update_layout(**base_layout(height=290))
fig2.update_xaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=TICK_FONT, zeroline=False,
)
fig2.update_yaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=TICK_FONT,
    ticksuffix="%",
    zeroline=True, zerolinecolor="#CBD5E1", zerolinewidth=1.5,
)

# ── CHART 3: Phan phoi loi suat ngay theo nam (box plot) ──────────────────────
print("[+] Building Chart 3 — Box Plot loi suat...")

years = sorted(df_ret["Year"].unique())
n     = len(years)

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def interp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return (int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

fig3 = go.Figure()

for i, yr in enumerate(years):
    yr_data = df_ret[df_ret["Year"] == yr]["DailyReturn"].dropna()
    t       = i / max(n - 1, 1)
    r, g, b = interp_color("#A78BFA", "#3B82F6", t)
    clr       = f"rgb({r},{g},{b})"
    clr_light = f"rgba({r},{g},{b},0.22)"

    fig3.add_trace(go.Box(
        y=yr_data,
        name=str(yr),
        boxpoints="outliers",
        marker=dict(color=clr, size=3, opacity=0.40),
        line=dict(color=clr, width=1.5),
        fillcolor=clr_light,
        whiskerwidth=0.6,
        hovertemplate=(
            u"<b>Năm {}</b><br>".format(yr)
            + u"Trung vị: %{median:.2f}%<br>"
            u"Khoảng giữa: %{q1:.2f}% – %{q3:.2f}%<br>"
            u"Biên dưới: %{lowerfence:.2f}%<br>"
            u"Biên trên: %{upperfence:.2f}%"
            "<extra></extra>"
        ),
    ))

# Duong 0% co nhan
fig3.add_hline(
    y=0,
    line=dict(color="#94A3B8", width=1.5, dash="dash"),
    annotation_text=u"Mốc 0%",
    annotation_position="top left",
    annotation_font=dict(size=10, color="#94A3B8", family=FONT),
)

fig3.update_layout(**base_layout(
    height=278,
    hovermode="closest",
    margin=dict(l=52, r=20, t=16, b=44),
))
fig3.update_xaxes(
    linecolor=C_BORDER, tickfont=TICK_FONT,
    showgrid=False, zeroline=False,
)
fig3.update_yaxes(
    showgrid=True, gridcolor=C_GRID, gridwidth=1,
    linecolor=C_BORDER, tickfont=TICK_FONT,
    ticksuffix="%", zeroline=False,
)

# ── Export divs ────────────────────────────────────────────────────────────────
print("[+] Exporting HTML divs...")

CFG_NONE = {"displayModeBar": False, "responsive": True}
CFG_ZOOM = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "toImage", "lasso2d", "select2d", "autoScale2d",
    ],
    "responsive": True,
}

div1 = pio.to_html(fig1, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s6-vol")
div2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False,
                   config=CFG_NONE, div_id="chart-s6-dd")
div3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False,
                   config=CFG_ZOOM, div_id="chart-s6-box")

# ── Badge builder ──────────────────────────────────────────────────────────────
def badge(label, value, color, bg, border):
    return (
        f'<span style="display:inline-block;font-size:.78em;font-family:{FONT};'
        f'padding:3px 11px;border-radius:20px;font-weight:600;'
        f'border:1px solid {border};background:{bg};color:{color};'
        f'margin-right:6px;margin-bottom:6px;">'
        f'{label}:&nbsp;<strong>{value}</strong></span>'
    )

badges_vol = (
    badge(u"Biến động hiện tại",
          f"{cur_vol:.2f}%", "#1D4ED8", "#EFF6FF", "#BFDBFE")
    + badge(u"Trung bình",
            f"{avg_vol:.2f}%", "#374151", "#F9FAFB", "#E5E7EB")
    + badge(u"Cao nhất",
            f"{max_vol:.2f}%", "#7C3AED", "#F5F3FF", "#DDD6FE")
)
badges_dd = (
    badge(u"Sụt giảm lớn nhất",
          f"{max_dd:.1f}%", "#B91C1C", "#FEF2F2", "#FCA5A5")
    + badge(u"Sụt giảm hiện tại",
            f"{cur_dd:.1f}%", "#374151", "#F9FAFB", "#E5E7EB")
    + badge(u"Ngày",
            max_dd_date, "#6B7280", "#F9FAFB", "#E5E7EB")
)

# ── CSS constants ──────────────────────────────────────────────────────────────
INNER_TITLE = (
    f"font-size:15px;font-weight:700;color:#D97706;"
    f"margin-bottom:4px;font-family:{FONT};"
)
INNER_SUB = (
    f"font-size:13px;color:#64748B;line-height:1.5;"
    f"margin-bottom:8px;font-family:{FONT};"
)
BIG_CARD = (
    "background:#FFFFFF;border:1px solid #E5E7EB;border-radius:18px;"
    "padding:24px;box-shadow:0 4px 16px rgba(0,0,0,0.05);"
)

# ── Build section HTML ─────────────────────────────────────────────────────────
NEW_SECTION = f"""<!-- Section 6: Risk -->
  <style>
    .s6-row1 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }}
    @media (max-width: 820px) {{
      .s6-row1 {{ grid-template-columns: 1fr; }}
    }}
  </style>

  <div class="section">
    <div class="section-title">
      Section 6 &mdash; Ph&#226;n t&#237;ch r&#7911;i ro &amp; bi&#7871;n &#273;&#7897;ng
    </div>

    <!-- 1 card lon duy nhat -->
    <div style="{BIG_CARD}">

      <!-- Tieu de + mo ta chung -->
      <div style="font-size:20px;font-weight:700;color:#D97706;
                  margin-bottom:4px;font-family:{FONT};">
        Ph&#226;n t&#237;ch r&#7911;i ro &amp; bi&#7871;n &#273;&#7897;ng gi&#225; BTC
      </div>
      <div style="font-size:13px;color:#6B7280;margin-bottom:20px;
                  line-height:1.5;font-family:{FONT};">
        Theo d&#245;i m&#7913;c bi&#7871;n &#273;&#7897;ng, drawdown v&#224;
        ph&#226;n ph&#7889;i l&#7907;i su&#7845;t theo t&#7915;ng n&#259;m.
      </div>

      <!-- Hang tren: 2 cot -->
      <div class="s6-row1">

        <!-- Cot trai: Bien dong lan -->
        <div>
          <div style="{INNER_TITLE}">
            Bi&#7871;n &#273;&#7897;ng l&#259;n 30 ng&#224;y
          </div>
          <div style="margin-bottom:6px;">{badges_vol}</div>
          <div style="{INNER_SUB}">
            &#272;&#7897; l&#7879;ch chu&#7849;n l&#259;n 30 ng&#224;y c&#7911;a l&#7907;i su&#7845;t ng&#224;y
            &mdash; gi&#225; tr&#7883; c&#224;ng cao ngh&#297;a l&#224; th&#7883; tr&#432;&#7901;ng
            c&#224;ng bi&#7871;n &#273;&#7897;ng m&#7841;nh.
          </div>
          {div1}
        </div>

        <!-- Cot phai: Sut giam tu dinh -->
        <div>
          <div style="{INNER_TITLE}">
            M&#7913;c s&#7909;t gi&#7843;m t&#7915; &#273;&#7881;nh
          </div>
          <div style="margin-bottom:6px;">{badges_dd}</div>
          <div style="{INNER_SUB}">
            Ph&#7847;n tr&#259;m gi&#7843;m so v&#7899;i &#273;&#7881;nh gi&#225; g&#7847;n nh&#7845;t
            &mdash; c&#224;ng s&#226;u ngh&#297;a l&#224; r&#7911;i ro
            th&#7883; tr&#432;&#7901;ng c&#224;ng cao.
          </div>
          {div2}
        </div>

      </div><!-- /s6-row1 -->

      <!-- Hang duoi: Box Plot full width -->
      <div style="border-top:1px solid #F1F5F9;padding-top:20px;">
        <div style="{INNER_TITLE}">
          Ph&#226;n ph&#7889;i l&#7907;i su&#7845;t ng&#224;y theo n&#259;m
        </div>
        <div style="{INNER_SUB}">
          Box plot l&#7907;i su&#7845;t ng&#224;y theo t&#7915;ng n&#259;m &mdash;
          h&#7897;p c&#224;ng r&#7897;ng ngh&#297;a l&#224; n&#259;m &#273;&#243;
          bi&#7871;n &#273;&#7897;ng c&#224;ng m&#7841;nh.
          C&#225;c &#273;i&#7875;m r&#7901;i l&#224; ng&#224;y b&#7845;t th&#432;&#7901;ng.
        </div>
        {div3}
      </div>

    </div><!-- /big card -->

  </div><!-- /section -->

  """

# ── Inject into HTML ───────────────────────────────────────────────────────────
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

S_MARK = "<!-- Section 6: Risk -->"
E_MARK = "<!-- Section 7: Insights -->"

s = html.find(S_MARK)
e = html.find(E_MARK, s)

if s == -1 or e == -1:
    print(f"[ERROR] Markers not found  (s={s}, e={e})")
    sys.exit(1)

html = html[:s] + NEW_SECTION + html[e:]
print(f"    Injected Section 6  (s={s})")

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")

# ── Fix bdata ──────────────────────────────────────────────────────────────────
print("[+] Running fix_bdata.py...")
subprocess.run([sys.executable, "fix_bdata.py"], check=True)
print("[+] Running fix_heatmap.py...")
subprocess.run([sys.executable, "fix_heatmap.py"], check=True)

# ── Sync to index.html (Vercel entry point) ────────────────────────────────────
import shutil
shutil.copy(TARGET, "index.html")
print("[+] Synced to index.html")

print(f"\n[DONE] Section 6 rebuilt.")
print(f"  Vol: cur={cur_vol}%  avg={avg_vol}%  max={max_vol}%  ({max_vol_date})")
print(f"  DD:  max={max_dd}%  cur={cur_dd}%  ({max_dd_date})")
print("Ctrl+Shift+R to refresh browser.")
