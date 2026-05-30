"""
Rebuild Section 2 (Price Trend) va Section 3 (Animated Timeline)
trong "bitcoin_dashboard copy 2.html".

Khong doi data logic, khong cham section khac.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import re
import warnings
warnings.filterwarnings("ignore")

TARGET = "bitcoin_dashboard copy 2.html"

# ============================================================
# CONSTANTS — Light theme (Business Analytics)
# ============================================================
C_WHITE   = "#FFFFFF"
C_BG      = "#F8FAFC"
C_TEXT    = "#334155"
C_TITLE   = "#0F172A"
C_MUTED   = "#64748B"
C_GRID    = "rgba(148,163,184,0.25)"
C_ZERO    = "rgba(148,163,184,0.35)"
C_BORDER  = "#CBD5E1"
C_CARD    = "#E2E8F0"

C_BTC     = "#F59E0B"   # Bitcoin amber
C_MA30    = "#2563EB"   # Blue
C_MA200   = "#DC2626"   # Red
C_NAVY    = "#0F4C81"   # Event marker border

HOVER_STYLE = dict(
    bgcolor=C_WHITE,
    bordercolor=C_BORDER,
    font=dict(color=C_TITLE, size=12),
)

# ============================================================
# SECTION 1: LOAD DATA
# ============================================================
print("[+] Loading data...")

df_raw = pd.read_csv("bitcoin_data/btc_daily.csv")
df_raw["Date"] = pd.to_datetime(df_raw["open_time"])
df_raw = df_raw.rename(columns={"open":"Open","high":"High","low":"Low",
                                  "close":"Close","volume":"Volume"})
df_raw = df_raw[["Date","Open","High","Low","Close","Volume"]]
df_raw = df_raw.sort_values("Date").reset_index(drop=True)

# Ensure derived columns
if "MA30" not in df_raw.columns:
    df_raw["MA30"] = df_raw["Close"].rolling(30).mean()
if "MA200" not in df_raw.columns:
    df_raw["MA200"] = df_raw["Close"].rolling(200).mean()
if "YearMonth" not in df_raw.columns:
    df_raw["YearMonth"] = df_raw["Date"].dt.to_period("M").astype(str)

daily_df = df_raw.copy()

# Monthly aggregation
monthly_df = (
    daily_df.groupby("YearMonth", as_index=False)
    .agg(Date=("Date","first"), Open=("Open","first"),
         High=("High","max"), Low=("Low","min"),
         Close=("Close","last"), Volume=("Volume","sum"))
    .sort_values("Date").reset_index(drop=True)
)
monthly_df["Monthly_Return"] = monthly_df["Close"].pct_change() * 100

# Events
_raw_events = [
    ("2018-01-08","Local Peak $17,527",           "ATH",         3,"Early Jan peak before crypto winter"),
    ("2020-11-30","Reclaims 2017 ATH $19,860",    "ATH",         4,"BTC surpasses 2017 ATH after 3 years"),
    ("2021-04-14","ATH $64,899",                  "ATH",         5,"Coinbase IPO day — BTC ATH $64,899"),
    ("2021-11-10","ATH $69,000",                  "ATH",         5,"Peak of 2021 bull run"),
    ("2024-03-14","ATH $73,750",                  "ATH",         5,"New ATH before 4th halving"),
    ("2024-12-17","ATH $108,353",                 "ATH",         5,"Post-election rally ATH"),
    ("2025-01-20","ATH $126,199",                 "ATH",         5,"Post-inauguration all-time high"),
    ("2018-02-06","Crypto Winter Begins",         "Crash",       5,"BTC -65% from ATH, bear market starts"),
    ("2018-11-14","BCH Fork Crash",               "Crash",       4,"Bitcoin Cash war — BTC -50%"),
    ("2020-03-12","Black Thursday",               "Crash",       5,"COVID panic — BTC -50% in 24h"),
    ("2021-05-19","China Mining Ban",             "Crash",       4,"BTC -30% on China crackdown"),
    ("2022-05-12","LUNA/UST Collapse",            "Crash",       5,"Terra ecosystem collapse, BTC -30%"),
    ("2022-06-18","3AC Insolvency",               "Crash",       4,"Three Arrows Capital contagion"),
    ("2022-11-09","FTX Collapse",                 "Crash",       5,"FTX bankruptcy — BTC hits $15,700"),
    ("2020-05-11","3rd Halving (6.25 BTC)",       "Halving",     5,"Block reward reduced 12.5 to 6.25 BTC"),
    ("2024-04-20","4th Halving (3.125 BTC)",      "Halving",     5,"Block reward reduced 6.25 to 3.125 BTC"),
    ("2021-10-19","BTC Futures ETF (BITO)",       "ETF",         4,"ProShares BITO launches on NYSE"),
    ("2024-01-11","Spot BTC ETF Approved",        "ETF",         5,"SEC approves BlackRock & 10 others"),
    ("2020-08-11","MicroStrategy Buys $250M",     "Institutional",4,"First major corporate BTC treasury"),
    ("2020-10-21","PayPal Enables Crypto",        "Institutional",4,"346M PayPal users can buy BTC"),
    ("2021-02-08","Tesla Buys $1.5B BTC",         "Institutional",4,"Tesla adds BTC to balance sheet"),
    ("2025-03-07","US Strategic BTC Reserve",     "Institutional",5,"Trump signs executive order"),
    ("2021-09-07","El Salvador: BTC Legal Tender","Regulation",  4,"First country to adopt BTC as currency"),
    ("2023-06-05","SEC vs Binance & Coinbase",    "Regulation",  4,"SEC files major crypto lawsuits"),
    ("2023-08-29","Grayscale Wins vs SEC",        "Regulation",  4,"Court ruling paves way for spot ETF"),
    ("2020-12-16","BTC Crosses $20,000",          "Milestone",   4,"Historic psychological barrier broken"),
    ("2021-02-16","BTC Crosses $50,000",          "Milestone",   3,"$50K milestone"),
    ("2024-11-22","BTC Approaches $100K",         "Milestone",   4,"Breaks $99,000 barrier"),
    ("2024-12-05","BTC Crosses $100,000",         "Milestone",   5,"Historic $100K milestone"),
]
events_df = pd.DataFrame(_raw_events,
    columns=["Date","Event","Type","Importance","Note"])
events_df["Date"]      = pd.to_datetime(events_df["Date"])
events_df["YearMonth"] = events_df["Date"].dt.to_period("M").astype(str)
events_df["Year"]      = events_df["Date"].dt.year

print(f"    daily: {len(daily_df)} | monthly: {len(monthly_df)} | events: {len(events_df)}")

# ============================================================
# SECTION 2: HELPER FUNCTIONS (Part E)
# ============================================================

def prepare_events_with_price_daily(daily_df, events_df):
    """Merge events voi daily close bang merge_asof (nearest date)."""
    daily  = daily_df[["Date","Close"]].copy().sort_values("Date")
    events = events_df.copy().sort_values("Date")
    events = events[events["Date"] >= daily["Date"].min()]

    merged = pd.merge_asof(
        events,
        daily,
        on="Date",
        direction="nearest",
    )
    return merged


def prepare_events_with_price_monthly(monthly_df, events_df):
    """
    Map events vao monthly_df theo YearMonth.
    Dung Close cuoi thang de dat marker tren bieu do thang.
    """
    ym_map = monthly_df.set_index("YearMonth")
    rows = []
    for _, ev in events_df.iterrows():
        ym = ev["YearMonth"]
        if ym in ym_map.index:
            row = ev.to_dict()
            row["Close"]    = ym_map.loc[ym, "Close"]
            row["PlotDate"] = ym_map.loc[ym, "Date"]
            rows.append(row)
    result = pd.DataFrame(rows).reset_index(drop=True)
    return result


# ============================================================
# SECTION 3: PRICE TREND CHART (Part A)
# ============================================================

def create_price_trend_chart(daily_df, events_with_price):
    """
    Bieu do gia Bitcoin sach, phu hop light theme BA dashboard.
    4 traces: BTC Close, MA30, MA200, Key Events (1 trace duy nhat).
    """
    df = daily_df.copy()
    if "MA30" not in df.columns:
        df["MA30"] = df["Close"].rolling(30).mean()
    if "MA200" not in df.columns:
        df["MA200"] = df["Close"].rolling(200).mean()

    fig = go.Figure()

    # --- Trace 1: BTC Close ---
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Close"],
        mode="lines",
        name="BTC Close",
        line=dict(color=C_BTC, width=3),
        hovertemplate=(
            "<b>BTC Close</b><br>"
            "Date: %{x|%Y-%m-%d}<br>"
            "Price: $%{y:,.0f}"
            "<extra></extra>"
        ),
    ))

    # --- Trace 2: MA30 ---
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA30"],
        mode="lines",
        name="MA 30",
        line=dict(color=C_MA30, width=1.6, dash="dot"),
        hovertemplate=(
            "<b>MA 30</b><br>"
            "Date: %{x|%Y-%m-%d}<br>"
            "Value: $%{y:,.0f}"
            "<extra></extra>"
        ),
    ))

    # --- Trace 3: MA200 ---
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA200"],
        mode="lines",
        name="MA 200",
        line=dict(color=C_MA200, width=1.6, dash="dash"),
        hovertemplate=(
            "<b>MA 200</b><br>"
            "Date: %{x|%Y-%m-%d}<br>"
            "Value: $%{y:,.0f}"
            "<extra></extra>"
        ),
    ))

    # --- Trace 4: Key Events (1 trace, 1 legend entry) ---
    ev = events_with_price.copy()
    # Rut gon Note de tooltip khong qua dai
    ev["NoteShort"] = ev["Note"].str[:65] + ev["Note"].str[65:].apply(
        lambda x: "..." if x else "")

    fig.add_trace(go.Scatter(
        x=ev["Date"], y=ev["Close"],
        mode="markers",
        name="Key Events",
        marker=dict(
            symbol="circle",
            size=11,
            color=C_WHITE,
            line=dict(color=C_NAVY, width=2.2),
            opacity=0.95,
        ),
        customdata=ev[["Event","Type","NoteShort"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Type: %{customdata[1]}<br>"
            "Date: %{x|%Y-%m-%d}<br>"
            "BTC Price: $%{y:,.0f}<br>"
            "<i>%{customdata[2]}</i>"
            "<extra></extra>"
        ),
    ))

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text="Xu Huong Gia Bitcoin (2018-2026)",
            font=dict(size=20, color=C_TITLE,
                      family="'Segoe UI', system-ui, sans-serif"),
            x=0.0, xanchor="left",
        ),
        paper_bgcolor=C_WHITE,
        plot_bgcolor=C_WHITE,
        font=dict(color=C_TEXT, size=13,
                  family="'Segoe UI', system-ui, sans-serif"),
        hovermode="closest",
        hoverlabel=HOVER_STYLE,
        height=520,
        margin=dict(l=70, r=30, t=80, b=60),

        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.04,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=C_CARD,
            borderwidth=1,
            font=dict(color=C_TEXT, size=13),
        ),

        xaxis=dict(
            title=dict(text="Thoi gian", font=dict(color=C_MUTED, size=12)),
            showgrid=True, gridcolor=C_GRID,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color=C_MUTED),
            rangeslider=dict(visible=True, bgcolor=C_BG, thickness=0.05),
            rangeselector=dict(
                bgcolor=C_WHITE, bordercolor=C_BORDER, borderwidth=1,
                activecolor=C_BTC,
                font=dict(color=C_TEXT, size=12),
                buttons=[
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=3, label="3Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
            ),
        ),

        yaxis=dict(
            title=dict(text="Gia (USD)", font=dict(color=C_MUTED, size=12)),
            showgrid=True, gridcolor=C_GRID,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color=C_MUTED),
            tickprefix="$",
            separatethousands=True,
            zerolinecolor=C_ZERO,
        ),
    )

    return fig


# ============================================================
# SECTION 4: ANIMATED MONTHLY EVENT TIMELINE (Part C)
# ============================================================

def create_animated_monthly_event_timeline(monthly_df, events_mp):
    """
    Animation chay theo tung thang tu dau den cuoi dataset.
    - Trace 0: BTC monthly close line (tich luy den thang hien tai)
    - Trace 1: Key Events markers (cac su kien da qua)
    - Annotation: bubble lon neu thang co su kien importance >= 4,
                  bubble nho cho gia Close neu khong co su kien.
    """
    # Cố định axis range
    x_min = monthly_df["Date"].min()
    x_max = monthly_df["Date"].max()
    y_min = monthly_df["Close"].min() * 0.80
    y_max = monthly_df["Close"].max() * 1.15

    all_months = sorted(monthly_df["YearMonth"].tolist())

    # ── Helper: tao traces cho mot frame ──────────────────────
    def _price_trace(ym_cutoff):
        sub = monthly_df[monthly_df["YearMonth"] <= ym_cutoff]
        return go.Scatter(
            x=sub["Date"], y=sub["Close"],
            mode="lines",
            name="BTC Monthly Close",
            line=dict(color=C_BTC, width=3),
            showlegend=True,
            hovertemplate=(
                "<b>BTC Monthly Close</b><br>"
                "%{x|%Y-%m}: $%{y:,.0f}"
                "<extra></extra>"
            ),
        )

    def _event_trace(ym_cutoff):
        sub = events_mp[events_mp["YearMonth"] <= ym_cutoff]
        note_short = (sub["Note"].str[:55] + sub["Note"].str[55:].apply(
            lambda x: "..." if x else "")).values if len(sub) else []

        cdata = np.column_stack([
            sub["Event"].values,
            sub["Type"].values,
            sub["Date"].dt.strftime("%Y-%m-%d").values,
            note_short,
        ]) if len(sub) > 0 else np.empty((0, 4), dtype=object)

        return go.Scatter(
            x=sub["PlotDate"] if len(sub) > 0 else [],
            y=sub["Close"]    if len(sub) > 0 else [],
            mode="markers",
            name="Key Events",
            marker=dict(
                symbol="circle", size=11,
                color=C_WHITE,
                line=dict(color=C_NAVY, width=2.2),
                opacity=0.95,
            ),
            customdata=cdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Type: %{customdata[1]}<br>"
                "Date: %{customdata[2]}<br>"
                "BTC: $%{y:,.0f}<br>"
                "<i>%{customdata[3]}</i>"
                "<extra></extra>"
            ),
            showlegend=True,
        )

    def _annotations(ym):
        """Annotation: bubble lon cho su kien quan trong, bubble nho cho gia."""
        anns = []
        cur_row = monthly_df[monthly_df["YearMonth"] == ym]
        cur_events = events_mp[
            (events_mp["YearMonth"] == ym) & (events_mp["Importance"] >= 4)
        ]

        if len(cur_events) > 0:
            # Bubble lon cho su kien
            for _, ev in cur_events.iterrows():
                price_ratio = ev["Close"] / y_max
                ay = -65 if price_ratio > 0.5 else 65
                ax = 80 if ev["PlotDate"] < monthly_df["Date"].median() else -80
                # Rut gon note
                note_txt = ev["Note"][:55] + ("..." if len(ev["Note"]) > 55 else "")
                ann_text = (
                    f"<b>{ev['Event']}</b><br>"
                    f"{ev['Type']} · {ev['Date'].strftime('%Y-%m-%d')}<br>"
                    f"BTC: ${ev['Close']:,.0f}<br>"
                    f"<i>{note_txt}</i>"
                )
                anns.append(dict(
                    x=ev["PlotDate"], y=ev["Close"],
                    xref="x", yref="y",
                    text=ann_text,
                    showarrow=True,
                    arrowhead=2, arrowwidth=1.5,
                    arrowcolor=C_BTC,
                    ax=ax, ay=ay,
                    align="left",
                    font=dict(size=12, color=C_TITLE),
                    bgcolor=C_WHITE,
                    bordercolor=C_BTC,
                    borderwidth=1.5,
                    borderpad=8,
                    opacity=0.97,
                ))
        elif len(cur_row) > 0:
            # Bubble nho cho gia Close thang hien tai
            cur_price = cur_row["Close"].iloc[0]
            cur_date  = cur_row["Date"].iloc[0]
            anns.append(dict(
                x=cur_date, y=cur_price,
                xref="x", yref="y",
                text=f"${cur_price:,.0f}",
                showarrow=True,
                arrowhead=1, arrowwidth=1,
                arrowcolor=C_MUTED,
                ax=36, ay=-28,
                font=dict(size=11, color=C_TEXT),
                bgcolor=C_WHITE,
                bordercolor=C_BORDER,
                borderwidth=1,
                borderpad=5,
                opacity=0.92,
            ))
        return anns

    # ── Build frames ──────────────────────────────────────────
    print(f"    Building {len(all_months)} animation frames...")
    frames = []
    for ym in all_months:
        cur_row   = monthly_df[monthly_df["YearMonth"] == ym]
        cur_price = cur_row["Close"].iloc[0] if len(cur_row) > 0 else 0
        cur_ret   = cur_row["Monthly_Return"].iloc[0] if len(cur_row) > 0 else 0
        sign      = "+" if cur_ret >= 0 else ""
        title_txt = (
            f"Animated Bitcoin Monthly Event Timeline (2018-2026)"
            f"   |   {ym}   |   ${cur_price:,.0f}   ({sign}{cur_ret:.1f}%)"
        )
        frames.append(go.Frame(
            data=[_price_trace(ym), _event_trace(ym)],
            layout=go.Layout(
                title_text=title_txt,
                annotations=_annotations(ym),
            ),
            name=ym,
        ))

    # ── Initial figure ────────────────────────────────────────
    init_row   = monthly_df[monthly_df["YearMonth"] == all_months[0]]
    init_price = init_row["Close"].iloc[0]

    fig = go.Figure(
        data=[_price_trace(all_months[0]), _event_trace(all_months[0])],
        frames=frames,
    )

    # Play / Pause
    updatemenus = [dict(
        type="buttons", showactive=False,
        x=0.0, y=-0.12, xanchor="left", yanchor="top",
        bgcolor=C_BG, bordercolor=C_BORDER, borderwidth=1,
        font=dict(color=C_TEXT, size=13),
        buttons=[
            dict(
                label="Play",
                method="animate",
                args=[None, dict(
                    frame=dict(duration=500, redraw=True),
                    fromcurrent=True,
                    transition=dict(duration=200, easing="linear"),
                )],
            ),
            dict(
                label="Pause",
                method="animate",
                args=[[None], dict(
                    frame=dict(duration=0, redraw=False),
                    mode="immediate",
                    transition=dict(duration=0),
                )],
            ),
        ],
    )]

    # Month slider
    sliders = [dict(
        active=0,
        currentvalue=dict(
            prefix="Month: ",
            visible=True,
            font=dict(color=C_TEXT, size=12),
            xanchor="left",
        ),
        pad=dict(t=52, b=8),
        len=1.0, x=0.0,
        bgcolor=C_BG,
        bordercolor=C_BORDER, borderwidth=1,
        tickcolor=C_MUTED,
        font=dict(color=C_MUTED, size=8),
        minorticklen=0,
        steps=[
            dict(
                args=[[ym], dict(
                    frame=dict(duration=500, redraw=True),
                    mode="immediate",
                    transition=dict(duration=200),
                )],
                label=ym,
                method="animate",
            )
            for ym in all_months
        ],
    )]

    fig.update_layout(
        title=dict(
            text=(
                f"Animated Bitcoin Monthly Event Timeline (2018-2026)"
                f"   |   {all_months[0]}   |   ${init_price:,.0f}"
            ),
            font=dict(size=15, color=C_TITLE,
                      family="'Segoe UI', system-ui, sans-serif"),
            x=0.02,
        ),
        paper_bgcolor=C_WHITE,
        plot_bgcolor=C_WHITE,
        font=dict(color=C_TEXT, size=12,
                  family="'Segoe UI', system-ui, sans-serif"),
        height=560,
        margin=dict(l=70, r=30, t=65, b=140),
        hoverlabel=HOVER_STYLE,
        hovermode="closest",

        # Fixed axis ranges
        xaxis=dict(
            range=[x_min, x_max],
            showgrid=True, gridcolor=C_GRID,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color=C_MUTED),
            title=dict(text="Date", font=dict(color=C_MUTED, size=12)),
            fixedrange=True,
        ),
        yaxis=dict(
            range=[y_min, y_max],
            showgrid=True, gridcolor=C_GRID,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color=C_MUTED),
            tickprefix="$",
            separatethousands=True,
            title=dict(text="Price (USDT)", font=dict(color=C_MUTED, size=12)),
            fixedrange=True,
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.03,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=C_CARD, borderwidth=1,
            font=dict(color=C_TEXT, size=12),
        ),

        annotations=_annotations(all_months[0]),
        updatemenus=updatemenus,
        sliders=sliders,
    )

    return fig


# ============================================================
# SECTION 5: BUILD CHARTS & EXTRACT DIVS
# ============================================================
print("[+] Preparing event data...")
events_daily   = prepare_events_with_price_daily(daily_df, events_df)
events_monthly = prepare_events_with_price_monthly(monthly_df, events_df)
print(f"    events_daily: {len(events_daily)} | events_monthly: {len(events_monthly)}")

print("[+] Creating price trend chart (Section 2)...")
fig_trend = create_price_trend_chart(daily_df, events_daily)

print("[+] Creating animation (Section 3)...")
fig_anim = create_animated_monthly_event_timeline(monthly_df, events_monthly)

# Export divs (Plotly.js already loaded in page)
_cfg = dict(displayModeBar=True, displaylogo=False,
            modeBarButtonsToRemove=["lasso2d","select2d","autoScale2d"],
            scrollZoom=False)

div_trend = pio.to_html(fig_trend, full_html=False, include_plotlyjs=False,
                         div_id="chart-trend-v2", config=_cfg)
div_anim  = pio.to_html(fig_anim,  full_html=False, include_plotlyjs=False,
                         div_id="chart-anim-v2",  config=_cfg)

print("    Divs generated")

# ============================================================
# SECTION 6: BUILD NEW SECTION HTML
# ============================================================

# Section 2: Price Trend (khong co legend-badges nua)
NEW_S2 = f"""<!-- Section 2: Price Trend -->
  <div class="section">
    <div class="section-title">Section 2 — Price Trend & Moving Averages</div>
    <p style="color:#64748B;font-size:.85em;margin-bottom:14px;">
      Hover vao cac chấm tron tren duong gia de xem thong tin su kien.
      Dung range selector hoac range slider phia duoi de phong to.
    </p>
    {div_trend}
  </div>"""

# Section 3: Animated Timeline
NEW_S3 = f"""<!-- Section 3: Animated Timeline -->
  <div class="section">
    <div class="section-title">Section 3 — Animated Monthly Event Timeline</div>
    <p style="color:#64748B;font-size:.85em;margin-bottom:14px;">
      Bam Play de xem lich su gia Bitcoin tung thang tu 2018 den 2026.
      Su kien quan trong hien bubble annotation khi animation chay den thang do.
    </p>
    {div_anim}
  </div>"""

# ============================================================
# SECTION 7: INJECT INTO HTML FILE
# ============================================================
print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

def replace_section(html, start_marker, end_marker, new_content):
    """Thay the noi dung giua start_marker va end_marker."""
    s = html.find(start_marker)
    e = html.find(end_marker, s)
    if s == -1 or e == -1:
        raise ValueError(f"Marker not found: '{start_marker}' or '{end_marker}'")
    return html[:s] + new_content + "\n\n  " + html[e:]

html = replace_section(html,
    "<!-- Section 2: Price Trend -->",
    "<!-- Section 3: Animated Timeline -->",
    NEW_S2)

html = replace_section(html,
    "<!-- Section 3: Animated Timeline -->",
    "<!-- Section 4: Financial Charts -->",
    NEW_S3)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"\n[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")
print("     Ctrl+Shift+R to refresh")
