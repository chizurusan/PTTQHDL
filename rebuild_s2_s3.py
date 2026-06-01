"""
Rebuild Section 2 (Price Trend) va Section 3 (Animated Timeline)
trong "bitcoin_dashboard copy 2.html".

v2 — Animated chart cap nhat:
  - Truc Y dong theo tung frame (y_max = max_price_so_far * 1.2)
  - Marker moc gia $10K/$20K/$40K/$60K/$80K/$100K (vang/cam, tam giac)
  - Viet hoa toan bo: title, legend, tooltip, annotation, Play/Pause
  - Annotation hien toi thieu 3 thang (khong bien mat ngay)
  - Toc do cham hon: 1100ms/frame, 550ms transition
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import warnings
warnings.filterwarnings("ignore")

TARGET = "bitcoin_dashboard copy 2.html"

# ============================================================
# CONSTANTS — Light theme
# ============================================================
C_WHITE    = "#FFFFFF"
C_BG       = "#F8FAFC"
C_TEXT     = "#334155"
C_TITLE    = "#0F172A"
C_MUTED    = "#64748B"
C_GRID     = "rgba(148,163,184,0.25)"
C_ZERO     = "rgba(148,163,184,0.35)"
C_BORDER   = "#CBD5E1"
C_CARD     = "#E2E8F0"
C_BTC      = "#F59E0B"    # cam Bitcoin
C_MA30     = "#2563EB"    # xanh
C_MA200    = "#DC2626"    # do
C_NAVY     = "#0F4C81"    # xanh dam (vien marker su kien)
C_MILESTONE = "#D97706"   # vang/cam dam (marker moc gia)

FONT = "'Segoe UI', system-ui, -apple-system, sans-serif"

HOVER_STYLE = dict(
    bgcolor=C_WHITE,
    bordercolor=C_BORDER,
    font=dict(color=C_TITLE, size=12, family=FONT),
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

df_raw["MA30"]      = df_raw["Close"].rolling(30).mean()
df_raw["MA200"]     = df_raw["Close"].rolling(200).mean()
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

# ── Events — Tieng Viet ──────────────────────────────────────
_raw_events = [
    # date                 ten su kien                           loai           tam_quan  mo_ta
    ("2018-01-08","Dinh cuc bo $17,527",                 "Dinh moi",    3,"Dinh dau thang 1 truoc mua dong crypto"),
    ("2020-11-30","Lay lai dinh 2017",                   "Dinh moi",    4,"BTC vuot $19,860 sau 3 nam"),
    ("2021-04-14","Dinh moi $64,899",                    "Dinh moi",    5,"Ngay IPO Coinbase — BTC ATH $64,899"),
    ("2021-11-10","Dinh moi $69,000",                    "Dinh moi",    5,"Dinh bull run 2021"),
    ("2024-03-14","Dinh moi $73,750",                    "Dinh moi",    5,"ATH moi truoc halving lan 4"),
    ("2024-12-17","Dinh moi $108,353",                   "Dinh moi",    5,"Dinh moi sau bau cu My"),
    ("2025-01-20","Dinh moi $126,199",                   "Dinh moi",    5,"Dinh cao nhat sau le nhau chuc"),
    ("2018-02-06","Mua dong Crypto bat dau",             "Giam manh",   5,"BTC giam -65% tu dinh, gau bat dau"),
    ("2018-11-14","Giam do phan nhanh BCH",              "Giam manh",   4,"Chien tranh Bitcoin Cash — BTC -50%"),
    ("2020-03-12","Thu Nam Den Toi",                     "Giam manh",   5,"Hoang loan COVID — BTC -50% trong 24h"),
    ("2021-05-19","TQ siet khai thac Bitcoin",           "Giam manh",   4,"Trung Quoc cam khai thac — BTC -30%"),
    ("2022-05-12","LUNA/UST sup do",                     "Giam manh",   5,"He sinh thai Terra sup do, BTC -30%"),
    ("2022-06-18","Three Arrows Capital vo no",          "Giam manh",   4,"Lay lan tu Three Arrows Capital"),
    ("2022-11-09","FTX sup do",                          "Giam manh",   5,"FTX pha san — BTC ve $15,700"),
    ("2020-05-11","Halving lan 3 (6.25 BTC)",            "Halving",     5,"Phan thuong block: 12.5 -> 6.25 BTC"),
    ("2024-04-20","Halving lan 4 (3.125 BTC)",           "Halving",     5,"Phan thuong block: 6.25 -> 3.125 BTC"),
    ("2021-10-19","ETF Futures BTC (BITO)",              "ETF",         4,"ProShares BITO ra mat tren NYSE"),
    ("2024-01-11","SEC phe duyet ETF Bitcoin",           "ETF",         5,"BlackRock & 10 quy duoc SEC chap thuan"),
    ("2020-08-11","MicroStrategy mua $250M BTC",         "To chuc",     4,"Quy du tru BTC doanh nghiep dau tien"),
    ("2020-10-21","PayPal cho phep mua BTC",             "To chuc",     4,"346M nguoi dung PayPal co the mua BTC"),
    ("2021-02-08","Tesla mua $1.5 ty BTC",               "To chuc",     4,"Tesla dua BTC vao bang can doi ke toan"),
    ("2025-03-07","My lap du tru Bitcoin chien luoc",    "To chuc",     5,"Trump ky sac lenh hanh phap"),
    ("2021-09-07","El Salvador: BTC hop phap",           "Phap ly",     4,"Quoc gia dau tien cong nhan BTC la tien"),
    ("2023-06-05","SEC kien Binance & Coinbase",         "Phap ly",     4,"SEC khoi kien lon ve tien ma hoa"),
    ("2023-08-29","Grayscale thang kien SEC",            "Phap ly",     4,"Toa an mo duong cho ETF giao ngay"),
    ("2020-12-16","BTC vuot $20,000",                    "Moc gia",     4,"Pha vo nguong tam ly $20,000"),
    ("2021-02-16","BTC vuot $50,000",                    "Moc gia",     3,"Moc $50,000"),
    ("2024-11-22","BTC tien sat $100K",                  "Moc gia",     4,"Pha nguong $99,000"),
    ("2024-12-05","BTC vuot $100,000",                   "Moc gia",     5,"Cot moc lich su $100,000"),
]

# Phien ban Unicode day du cho hien thi
_display_events = [
    ("2018-01-08",u"Đỉnh cục bộ $17,527",               u"Đỉnh mới",   3,u"Đỉnh đầu tháng 1 trước mùa đông crypto"),
    ("2020-11-30",u"Lấy lại đỉnh 2017",                 u"Đỉnh mới",   4,u"BTC vượt $19,860 sau 3 năm"),
    ("2021-04-14",u"Đỉnh mới $64,899",                  u"Đỉnh mới",   5,u"Ngày IPO Coinbase — BTC đỉnh $64,899"),
    ("2021-11-10",u"Đỉnh mới $69,000",                  u"Đỉnh mới",   5,u"Đỉnh bull run 2021"),
    ("2024-03-14",u"Đỉnh mới $73,750",                  u"Đỉnh mới",   5,u"ATH mới trước halving lần 4"),
    ("2024-12-17",u"Đỉnh mới $108,353",                 u"Đỉnh mới",   5,u"Đỉnh mới sau bầu cử Mỹ"),
    ("2025-01-20",u"Đỉnh mới $126,199",                 u"Đỉnh mới",   5,u"Đỉnh cao nhất sau lễ nhậm chức"),
    ("2018-02-06",u"Mùa đông Crypto bắt đầu",           u"Giảm mạnh",  5,u"BTC giảm -65% từ đỉnh, gấu bắt đầu"),
    ("2018-11-14",u"Giảm do phân nhánh BCH",            u"Giảm mạnh",  4,u"Chiến tranh Bitcoin Cash — BTC -50%"),
    ("2020-03-12",u"Thứ Năm Đen Tối",                   u"Giảm mạnh",  5,u"Hoảng loạn COVID — BTC -50% trong 24h"),
    ("2021-05-19",u"TQ siết khai thác Bitcoin",         u"Giảm mạnh",  4,u"Trung Quốc cấm khai thác — BTC -30%"),
    ("2022-05-12",u"LUNA/UST sụp đổ",                   u"Giảm mạnh",  5,u"Hệ sinh thái Terra sụp đổ, BTC -30%"),
    ("2022-06-18",u"Three Arrows Capital vỡ nợ",        u"Giảm mạnh",  4,u"Lây lan từ Three Arrows Capital"),
    ("2022-11-09",u"FTX sụp đổ",                        u"Giảm mạnh",  5,u"FTX phá sản — BTC về $15,700"),
    ("2020-05-11",u"Halving lần 3 (6.25 BTC)",          u"Halving",    5,u"Phần thưởng block: 12.5 → 6.25 BTC"),
    ("2024-04-20",u"Halving lần 4 (3.125 BTC)",         u"Halving",    5,u"Phần thưởng block: 6.25 → 3.125 BTC"),
    ("2021-10-19",u"ETF Futures BTC (BITO)",            u"ETF",        4,u"ProShares BITO ra mắt trên NYSE"),
    ("2024-01-11",u"SEC phê duyệt ETF Bitcoin",         u"ETF",        5,u"BlackRock & 10 quỹ được SEC chấp thuận"),
    ("2020-08-11",u"MicroStrategy mua $250M BTC",       u"Tổ chức",    4,u"Quỹ dự trữ BTC doanh nghiệp đầu tiên"),
    ("2020-10-21",u"PayPal cho phép mua BTC",           u"Tổ chức",    4,u"346M người dùng PayPal có thể mua BTC"),
    ("2021-02-08",u"Tesla mua $1.5 tỷ BTC",             u"Tổ chức",    4,u"Tesla đưa BTC vào bảng cân đối kế toán"),
    ("2025-03-07",u"Mỹ lập dự trữ Bitcoin chiến lược", u"Tổ chức",    5,u"Trump ký sắc lệnh hành pháp"),
    ("2021-09-07",u"El Salvador: BTC hợp pháp",         u"Pháp lý",    4,u"Quốc gia đầu tiên công nhận BTC là tiền"),
    ("2023-06-05",u"SEC kiện Binance & Coinbase",       u"Pháp lý",    4,u"SEC khởi kiện lớn về tiền mã hóa"),
    ("2023-08-29",u"Grayscale thắng kiện SEC",          u"Pháp lý",    4,u"Tòa án mở đường cho ETF giao ngay"),
    ("2020-12-16",u"BTC vượt $20,000",                  u"Mốc giá",    4,u"Phá vỡ ngưỡng tâm lý $20,000"),
    ("2021-02-16",u"BTC vượt $50,000",                  u"Mốc giá",    3,u"Mốc $50,000"),
    ("2024-11-22",u"BTC tiến sát $100K",                u"Mốc giá",    4,u"Phá ngưỡng $99,000"),
    ("2024-12-05",u"BTC vượt $100,000",                 u"Mốc giá",    5,u"Cột mốc lịch sử $100,000"),
]

events_df = pd.DataFrame(_display_events,
    columns=["Date","Event","Type","Importance","Note"])
events_df["Date"]      = pd.to_datetime(events_df["Date"])
events_df["YearMonth"] = events_df["Date"].dt.to_period("M").astype(str)
events_df["Year"]      = events_df["Date"].dt.year

print(f"    daily: {len(daily_df)} | monthly: {len(monthly_df)} | events: {len(events_df)}")


# ============================================================
# SECTION 2: HELPER FUNCTIONS
# ============================================================

def prepare_events_with_price_daily(daily_df, events_df):
    daily  = daily_df[["Date","Close"]].copy().sort_values("Date")
    events = events_df.copy().sort_values("Date")
    events = events[events["Date"] >= daily["Date"].min()]
    return pd.merge_asof(events, daily, on="Date", direction="nearest")


def prepare_events_with_price_monthly(monthly_df, events_df):
    ym_map = monthly_df.set_index("YearMonth")
    rows = []
    for _, ev in events_df.iterrows():
        ym = ev["YearMonth"]
        if ym in ym_map.index:
            row = ev.to_dict()
            row["Close"]    = ym_map.loc[ym, "Close"]
            row["PlotDate"] = ym_map.loc[ym, "Date"]
            rows.append(row)
    return pd.DataFrame(rows).reset_index(drop=True)


# ============================================================
# SECTION 3: PRICE TREND CHART (Section 2 cua dashboard)
# ============================================================

def create_price_trend_chart(daily_df, events_with_price):
    df = daily_df.copy()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Close"],
        mode="lines", name=u"Giá BTC",
        line=dict(color=C_BTC, width=3),
        hovertemplate=(
            u"<b>Giá BTC</b><br>"
            u"Ngày: %{x|%d/%m/%Y}<br>"
            u"Giá: $%{y:,.0f}"
            "<extra></extra>"
        ),
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA30"],
        mode="lines", name="MA 30",
        line=dict(color=C_MA30, width=1.6, dash="dot"),
        hovertemplate=(
            "<b>MA 30</b><br>"
            u"Ngày: %{x|%d/%m/%Y}<br>"
            u"Giá trị: $%{y:,.0f}"
            "<extra></extra>"
        ),
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA200"],
        mode="lines", name="MA 200",
        line=dict(color=C_MA200, width=1.6, dash="dash"),
        hovertemplate=(
            "<b>MA 200</b><br>"
            u"Ngày: %{x|%d/%m/%Y}<br>"
            u"Giá trị: $%{y:,.0f}"
            "<extra></extra>"
        ),
    ))

    ev = events_with_price.copy()
    ev["NoteShort"] = ev["Note"].str[:65] + ev["Note"].str[65:].apply(
        lambda x: "..." if x else "")

    fig.add_trace(go.Scatter(
        x=ev["Date"], y=ev["Close"],
        mode="markers", name=u"Sự kiện quan trọng",
        marker=dict(symbol="circle", size=11, color=C_WHITE,
                    line=dict(color=C_NAVY, width=2.2), opacity=0.95),
        customdata=ev[["Event","Type","NoteShort"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            u"Loại: %{customdata[1]}<br>"
            u"Ngày: %{x|%d/%m/%Y}<br>"
            u"Giá BTC: $%{y:,.0f}<br>"
            "<i>%{customdata[2]}</i>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(
            text=u"Xu Hướng Giá Bitcoin (2018–2026)",
            font=dict(size=20, color=C_TITLE, family=FONT),
            x=0.0, xanchor="left",
        ),
        paper_bgcolor=C_WHITE, plot_bgcolor=C_WHITE,
        font=dict(color=C_TEXT, size=13, family=FONT),
        hovermode="closest", hoverlabel=HOVER_STYLE,
        height=520,
        margin=dict(l=70, r=30, t=80, b=60),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=C_CARD, borderwidth=1,
            font=dict(color=C_TEXT, size=13),
        ),
        xaxis=dict(
            title=dict(text=u"Thời gian", font=dict(color=C_MUTED, size=12)),
            showgrid=True, gridcolor=C_GRID,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color=C_MUTED),
            rangeslider=dict(visible=True, bgcolor=C_BG, thickness=0.05),
            rangeselector=dict(
                bgcolor=C_WHITE, bordercolor=C_BORDER, borderwidth=1,
                activecolor=C_BTC,
                font=dict(color=C_TEXT, size=12),
                buttons=[
                    dict(count=1,  label=u"1 năm",  step="year", stepmode="backward"),
                    dict(count=3,  label=u"3 năm",  step="year", stepmode="backward"),
                    dict(count=5,  label=u"5 năm",  step="year", stepmode="backward"),
                    dict(step="all", label=u"Tất cả"),
                ],
            ),
        ),
        yaxis=dict(
            title=dict(text=u"Giá (USD)", font=dict(color=C_MUTED, size=12)),
            showgrid=True, gridcolor=C_GRID,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color=C_MUTED),
            tickprefix="$", separatethousands=True,
            zerolinecolor=C_ZERO,
        ),
    )
    return fig


# ============================================================
# SECTION 4: ANIMATED MONTHLY EVENT TIMELINE (Section 3)
# ============================================================

def create_animated_monthly_event_timeline(monthly_df, events_mp):
    x_min = monthly_df["Date"].min()
    x_max = monthly_df["Date"].max()
    all_months = sorted(monthly_df["YearMonth"].tolist())

    # ── Moc gia ──────────────────────────────────────────────
    PRICE_MILESTONES = [10_000, 20_000, 40_000, 60_000, 80_000, 100_000]
    milestone_crossings = {}   # {price: {"ym":..., "date":..., "close":...}}
    for ms in PRICE_MILESTONES:
        crossed = monthly_df[monthly_df["Close"] >= ms]
        if len(crossed) > 0:
            row = crossed.iloc[0]
            milestone_crossings[ms] = {
                "ym":    row["YearMonth"],
                "date":  row["Date"],
                "close": row["Close"],
            }

    # ── Helpers ───────────────────────────────────────────────

    # Truc Y chi thay doi tai 3 nguong → toi da 2 lan "jump" trong 101 frames
    # $20K  : BTC <$16.7K   (2018-01 → ~2020-11, ~35 frames, rat on dinh)
    # $80K  : BTC <$66.7K   (2020-12 → ~2024-02, ~39 frames)
    # $155K : BTC <$129K    (2024-03 tro di)
    Y_STEPS = [20_000, 80_000, 155_000]

    def _dyn_ymax(ym_cutoff):
        sub = monthly_df[monthly_df["YearMonth"] <= ym_cutoff]
        if len(sub) == 0:
            return Y_STEPS[0]
        max_price = sub["Close"].max()
        for step in Y_STEPS:
            if max_price < step / 1.2:
                return step
        return round(max_price * 1.25 / 5000) * 5000

    def _price_trace(ym_cutoff):
        sub = monthly_df[monthly_df["YearMonth"] <= ym_cutoff].copy()
        cdata = sub["Monthly_Return"].fillna(0).round(1).values
        return go.Scatter(
            x=sub["Date"], y=sub["Close"],
            mode="lines",
            name=u"Giá đóng cửa BTC theo tháng",
            line=dict(color=C_BTC, width=3),
            showlegend=True,
            customdata=cdata,
            hovertemplate=(
                u"Tháng: %{x|%m/%Y}<br>"
                u"Giá đóng cửa: $%{y:,.0f}<br>"
                u"Biến động tháng: %{customdata:+.1f}%"
                "<extra></extra>"
            ),
        )

    def _event_trace(ym_cutoff):
        sub = events_mp[
            (events_mp["YearMonth"] <= ym_cutoff) &
            (events_mp["Type"] != u"Mốc giá")
        ].copy()
        if len(sub) > 0:
            note_arr = (sub["Note"].str[:55] + sub["Note"].str[55:].apply(
                lambda x: "..." if x else "")).values
            cdata = np.column_stack([
                sub["Event"].values,
                sub["Type"].values,
                sub["Date"].dt.strftime("%d/%m/%Y").values,
                note_arr,
            ])
            xs = sub["PlotDate"].values
            ys = sub["Close"].values
        else:
            cdata = np.empty((0, 4), dtype=object)
            xs, ys = [], []

        return go.Scatter(
            x=xs, y=ys,
            mode="markers",
            name=u"Sự kiện quan trọng",
            marker=dict(symbol="circle", size=11, color=C_WHITE,
                        line=dict(color=C_NAVY, width=2.2), opacity=0.95),
            customdata=cdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                u"Loại: %{customdata[1]}<br>"
                u"Ngày: %{customdata[2]}<br>"
                "BTC: $%{y:,.0f}<br>"
                "<i>%{customdata[3]}</i>"
                "<extra></extra>"
            ),
            showlegend=True,
        )

    def _milestone_trace(ym_cutoff):
        rows = [
            {
                "date":  info["date"],
                "close": info["close"],
                "label": u"Vượt mốc ${}K".format(ms // 1000),
            }
            for ms, info in milestone_crossings.items()
            if info["ym"] <= ym_cutoff
        ]
        empty_scatter = go.Scatter(
            x=[], y=[],
            mode="markers",
            name=u"Mốc giá mới",
            marker=dict(color=C_MILESTONE, size=14, symbol="triangle-up",
                        line=dict(color=C_WHITE, width=1.5)),
            showlegend=True,
            hovertemplate="<extra></extra>",
        )
        if not rows:
            return empty_scatter

        mdf = pd.DataFrame(rows)
        return go.Scatter(
            x=mdf["date"], y=mdf["close"],
            mode="markers",
            name=u"Mốc giá mới",
            marker=dict(color=C_MILESTONE, size=14, symbol="triangle-up",
                        line=dict(color=C_WHITE, width=1.5)),
            customdata=mdf["label"].values,
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                u"Tháng: %{x|%m/%Y}<br>"
                "BTC: $%{y:,.0f}"
                "<extra></extra>"
            ),
            showlegend=True,
        )

    def _get_recent_events(ym, n_months=3):
        """Tra ve cac su kien trong cua so n_months thang tinh den ym."""
        ym_idx = all_months.index(ym)
        start_idx = max(0, ym_idx - (n_months - 1))
        window = set(all_months[start_idx:ym_idx + 1])
        return events_mp[
            events_mp["YearMonth"].isin(window) &
            (events_mp["Type"] != u"Mốc giá")
        ].copy()

    def _annotations(ym, y_max):
        anns = []
        cur_row = monthly_df[monthly_df["YearMonth"] == ym]
        ym_idx  = all_months.index(ym)
        median_date = monthly_df["Date"].median()

        # ── Info box dong (paper coords, khong tranh voi title/legend) ──
        _cur_price   = cur_row["Close"].iloc[0] if len(cur_row) > 0 else 0
        _cur_ret_raw = cur_row["Monthly_Return"].iloc[0] if len(cur_row) > 0 else None
        _date_disp   = pd.to_datetime(ym + "-01").strftime("%m/%Y")
        if _cur_ret_raw is None or (isinstance(_cur_ret_raw, float) and np.isnan(_cur_ret_raw)):
            _ret_str = u"—"
        else:
            _sign = "+" if _cur_ret_raw >= 0 else ""
            _ret_str = u"{}{}%".format(_sign, round(_cur_ret_raw, 1))
        anns.append(dict(
            x=0.995, y=0.975,
            xref="paper", yref="paper",
            xanchor="right", yanchor="top",
            text=(u"<b>Tháng {}</b>  |  ${:,.0f}  |  {}".format(
                _date_disp, _cur_price, _ret_str)),
            showarrow=False,
            font=dict(size=12, color=C_TITLE, family=FONT),
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="#D1D5DB",
            borderwidth=1, borderpad=7,
            opacity=0.96,
        ))

        # ── Annotation su kien quan trong (cua so 3 thang) ───
        recent  = _get_recent_events(ym, n_months=3)
        high_ev = recent[recent["Importance"] >= 4].copy()

        if len(high_ev) > 0:
            high_ev = high_ev.sort_values(
                ["Importance", "Date"], ascending=[False, False]
            ).head(2)

            for i, (_, ev) in enumerate(high_ev.iterrows()):
                price_ratio = ev["Close"] / y_max if y_max > 0 else 0.5
                ay = -80 if price_ratio > 0.45 else 80
                ax = 95 if ev["PlotDate"] < median_date else -95
                if i == 1:
                    ay = -ay         # annotation thu 2 doi huong doc
                    ax = ax * -1     # va doi huong ngang

                note_txt = str(ev["Note"])[:55]
                if len(str(ev["Note"])) > 55:
                    note_txt += "..."
                ann_text = (
                    "<b>{}</b><br>{} · {}<br>BTC: ${:,.0f}<br><i>{}</i>".format(
                        ev["Event"],
                        ev["Type"],
                        ev["Date"].strftime("%d/%m/%Y"),
                        ev["Close"],
                        note_txt,
                    )
                )
                anns.append(dict(
                    x=ev["PlotDate"], y=ev["Close"],
                    xref="x", yref="y",
                    text=ann_text,
                    showarrow=True,
                    arrowhead=2, arrowwidth=1.5, arrowcolor=C_NAVY,
                    ax=ax, ay=ay,
                    align="left",
                    font=dict(size=11, color=C_TITLE, family=FONT),
                    bgcolor="rgba(255,255,255,0.97)",
                    bordercolor=C_NAVY,
                    borderwidth=1.5, borderpad=8,
                    opacity=0.97,
                ))

        # ── Annotation moc gia (cua so 3 thang) ──────────────
        window_months = set(all_months[max(0, ym_idx - 2):ym_idx + 1])
        for ms, info in milestone_crossings.items():
            if info["ym"] in window_months and len(anns) < 2:
                price_ratio = info["close"] / y_max if y_max > 0 else 0.5
                ay_ms = -65 if price_ratio > 0.45 else 65
                label_ms = u"BTC vượt mốc ${}K!".format(ms // 1000)
                anns.append(dict(
                    x=info["date"], y=info["close"],
                    xref="x", yref="y",
                    text="<b>{}</b>".format(label_ms),
                    showarrow=True,
                    arrowhead=2, arrowwidth=1.5, arrowcolor=C_MILESTONE,
                    ax=0, ay=ay_ms,
                    align="center",
                    font=dict(size=12, color="#7C2D12", family=FONT),
                    bgcolor="rgba(253,230,138,0.97)",
                    bordercolor=C_MILESTONE,
                    borderwidth=1.5, borderpad=7,
                    opacity=0.97,
                ))

        # ── Fallback: bubble gia dong cua ────────────────────
        if len(anns) == 0 and len(cur_row) > 0:
            cur_price = cur_row["Close"].iloc[0]
            cur_date  = cur_row["Date"].iloc[0]
            anns.append(dict(
                x=cur_date, y=cur_price,
                xref="x", yref="y",
                text="${:,.0f}".format(cur_price),
                showarrow=True,
                arrowhead=1, arrowwidth=1, arrowcolor=C_MUTED,
                ax=36, ay=-30,
                font=dict(size=11, color=C_TEXT, family=FONT),
                bgcolor="rgba(255,255,255,0.90)",
                bordercolor=C_BORDER,
                borderwidth=1, borderpad=5,
                opacity=0.92,
            ))

        return anns

    # ── Build frames ──────────────────────────────────────────
    print("    Building {} animation frames...".format(len(all_months)))
    frames = []
    for ym in all_months:
        ymax = _dyn_ymax(ym)
        frames.append(go.Frame(
            data=[_price_trace(ym), _event_trace(ym), _milestone_trace(ym)],
            layout=go.Layout(
                annotations=_annotations(ym, ymax),
                yaxis=dict(range=[0, ymax], fixedrange=True),
            ),
            name=ym,
        ))

    # ── Initial figure ────────────────────────────────────────
    init_ym    = all_months[0]
    init_row   = monthly_df[monthly_df["YearMonth"] == init_ym]
    init_price = init_row["Close"].iloc[0]
    init_ymax  = _dyn_ymax(init_ym)
    init_date  = pd.to_datetime(init_ym + "-01").strftime("%m/%Y")

    init_title = u"<b>Lịch sử giá Bitcoin theo tháng 2018–2026</b>"

    # Play / Pause
    updatemenus = [dict(
        type="buttons", showactive=False,
        x=0.0, y=-0.12, xanchor="left", yanchor="top",
        bgcolor=C_WHITE, bordercolor=C_BORDER, borderwidth=1,
        font=dict(color=C_TEXT, size=13, family=FONT),
        buttons=[
            dict(
                label=u"▶ Chạy",
                method="animate",
                args=[None, dict(
                    frame=dict(duration=1100, redraw=True),
                    fromcurrent=True,
                    transition=dict(duration=0),
                )],
            ),
            dict(
                label=u"⏸ Tạm dừng",
                method="animate",
                args=[[None], dict(
                    frame=dict(duration=0, redraw=False),
                    mode="immediate",
                    transition=dict(duration=0),
                )],
            ),
        ],
    )]

    # Slider thang
    sliders = [dict(
        active=0,
        currentvalue=dict(
            prefix=u"Tháng: ",
            visible=True,
            font=dict(color=C_TEXT, size=12, family=FONT),
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
                    frame=dict(duration=1100, redraw=True),
                    mode="immediate",
                    transition=dict(duration=0),
                )],
                label=ym,
                method="animate",
            )
            for ym in all_months
        ],
    )]

    fig = go.Figure(
        data=[_price_trace(init_ym), _event_trace(init_ym), _milestone_trace(init_ym)],
        frames=frames,
    )

    fig.update_layout(
        title=dict(
            text=init_title,
            font=dict(size=17, color="#D97706", family=FONT),
            x=0.5,
            y=0.985,
            xanchor="center", yanchor="top",
        ),
        paper_bgcolor=C_WHITE,
        plot_bgcolor=C_WHITE,
        font=dict(color=C_TEXT, size=12, family=FONT),
        height=600,
        margin=dict(l=70, r=30, t=105, b=155),
        hoverlabel=dict(
            bgcolor=C_WHITE,
            bordercolor=C_BORDER,
            font=dict(color=C_TITLE, size=12, family=FONT),
        ),
        hovermode="closest",

        xaxis=dict(
            range=[x_min, x_max],
            showgrid=True, gridcolor=C_GRID, gridwidth=1,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color="#475569", size=14),
            title=dict(text=u"Thời gian", font=dict(color="#475569", size=13)),
            fixedrange=True,
            tickformat="%Y", dtick="M12",
        ),
        yaxis=dict(
            range=[0, init_ymax],
            showgrid=True, gridcolor=C_GRID, gridwidth=1,
            linecolor=C_BORDER, zeroline=False,
            tickfont=dict(color="#475569", size=14),
            tickprefix="$", separatethousands=True,
            title=dict(text=u"Giá (USD)", font=dict(color="#475569", size=13)),
            fixedrange=True,
        ),

        # Legend ngang, o phia duoi title, phia tren chart area
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.01,  # sat ngay tren chart area
            xanchor="right",  x=1.0,   # can phai — tranh voi title ben trai
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#D1D5DB",
            borderwidth=1,
            font=dict(color=C_TEXT, size=12, family=FONT),
            traceorder="normal",
            itemwidth=40,
        ),

        annotations=_annotations(init_ym, init_ymax),
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
print("    events_daily: {} | events_monthly: {}".format(
    len(events_daily), len(events_monthly)))

print("[+] Creating price trend chart (Section 2)...")
fig_trend = create_price_trend_chart(daily_df, events_daily)

print("[+] Creating animation (Section 3)...")
fig_anim = create_animated_monthly_event_timeline(monthly_df, events_monthly)

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

NEW_S2 = u"""<!-- Section 2: Price Trend -->
  <div class="section">
    <div class="section-title">Section 2 — Xu Hướng Giá &amp; Đường Trung Bình</div>
    <p style="color:#64748B;font-size:.85em;margin-bottom:14px;">
      Di chuột vào các chấm tròn để xem thông tin sự kiện.
      Dùng range selector hoặc range slider phía dưới để phóng to.
    </p>
    {}
  </div>""".format(div_trend)

NEW_S3 = u"""<!-- Section 3: Animated Timeline -->
  <div class="section">
    <div class="section-title">Section 3 &mdash; L&#7883;ch S&#7917; Gi&aacute; Bitcoin Theo Th&aacute;ng (Animation)</div>
    <p style="color:#64748B;font-size:.85em;margin-bottom:14px;">
      Nh&#7845;n <strong style="color:#F59E0B">&#9654; Ch&#7841;y</strong> &#273;&#7875; xem l&#7883;ch s&#7917; gi&aacute; Bitcoin
      t&#7915;ng th&aacute;ng t&#7915; 2018 &#273;&#7871;n 2026.
      Tr&#7909;c Y m&#7903; r&#7897;ng theo t&#7915;ng giai &#273;o&#7841;n t&#259;ng tr&#432;&#7903;ng &mdash;
      tam gi&aacute;c v&agrave;ng &#273;&aacute;nh d&#7845;u m&#7889;c gi&aacute; m&#7899;i.
      K&eacute;o slider &#273;&#7875; chuy&#7875;n &#273;&#7871;n b&#7845;t k&#7923; th&aacute;ng n&agrave;o.
    </p>
    {chart}
    <script>
    /* Warmup: khoi dong Plotly animation engine ngay khi load trang,
       tranh cold-start giat khi user bam Chay lan dau */
    (function () {{
        var _t = 0;
        function _wu() {{
            var el = document.getElementById('chart-anim-v2');
            if (!el || !el.layout) {{
                if (_t++ < 20) setTimeout(_wu, 300);
                return;
            }}
            try {{
                Plotly.animate(el, ['2018-01'], {{
                    frame: {{duration: 0, redraw: true}},
                    transition: {{duration: 0}},
                    mode: 'immediate'
                }});
            }} catch (e) {{}}
        }}
        setTimeout(_wu, 900);
    }})();
    </script>
  </div>""".format(chart=div_anim)


# ============================================================
# SECTION 7: INJECT INTO HTML FILE
# ============================================================
print("[+] Reading {}...".format(TARGET))
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()


def replace_section(html, start_marker, end_marker, new_content):
    s = html.find(start_marker)
    e = html.find(end_marker, s)
    if s == -1 or e == -1:
        raise ValueError("Marker not found: '{}' or '{}'".format(
            start_marker, end_marker))
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
print(u"\n[OK] Saved: {}  ({:.1f} MB)".format(TARGET, size_mb))
print("     Ctrl+Shift+R to refresh")
