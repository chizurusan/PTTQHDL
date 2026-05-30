"""
Redesign KPI cards theo Business Analytics Card Chart best practices.
Chi thay HTML cua Section 1 KPI va them CSS moi, khong doi data/logic.
"""

TARGET = "bitcoin_dashboard copy 2.html"

print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

# ============================================================
# PART 1 — NEW CSS CLASSES (them vao cuoi </style>)
# ============================================================
NEW_CSS = """
/* ══════════════════════════════════════════
   KPI CARD v2 — Business Analytics Style
   Header bar + Large value + Context text
   ══════════════════════════════════════════ */

/* Grid: 5 cards / row */
.kpi-grid-v2 {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 18px;
}
@media (max-width: 1100px) {
  .kpi-grid-v2 { grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); }
}

/* Card wrapper */
.kpi-card-v2 {
  background: #EFF6FF;
  border: 1px solid #CBD5E1;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: none;
}

/* Colored header bar */
.kpi-header-bar {
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: 0.25px;
  padding: 0 10px;
  text-align: center;
  white-space: nowrap;
}

/* Card body */
.kpi-body-v2 {
  padding: 20px 12px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 88px;
}

/* Primary value — most prominent element */
.kpi-val-v2 {
  font-size: 40px;
  font-weight: 800;
  line-height: 1.05;
  text-align: center;
  letter-spacing: -0.5px;
}

/* Context subtext */
.kpi-ctx-v2 {
  font-size: 12px;
  font-weight: 400;
  color: #64748B;
  text-align: center;
  margin-top: 7px;
  letter-spacing: 0.1px;
}
"""

html = html.replace("</style>", NEW_CSS + "\n</style>", 1)
print("    CSS classes added")

# ============================================================
# PART 2 — NEW KPI SECTION HTML
# Lay so lieu tu HTML hien tai, chi doi cau truc va nhan card.
# Header bar color:
#   Price/BTC    : #F59E0B
#   Positive/High: #16A34A
#   Negative/Risk: #DC2626
#   Neutral/Avg  : #0F4C81
# Value color theo loai (giong header bar)
# ============================================================
NEW_KPI_SECTION = """<!-- Section 1: KPI -->
  <div class="section">
    <div class="section-title">Section 1 — Key Performance Indicators</div>
    <div class="kpi-grid-v2">

      <!-- 1. Latest BTC Price -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#F59E0B;">Latest BTC Price</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#F59E0B;">$77,065</div>
          <div class="kpi-ctx-v2">2026-05-24</div>
        </div>
      </div>

      <!-- 2. All-Time High -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#16A34A;">All-Time High</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#16A34A;">$126,200</div>
          <div class="kpi-ctx-v2">2025-10-06</div>
        </div>
      </div>

      <!-- 3. All-Time Low -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#DC2626;">All-Time Low</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#DC2626;">$3,156</div>
          <div class="kpi-ctx-v2">2018-12-15</div>
        </div>
      </div>

      <!-- 4. Total Growth -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#16A34A;">Total Growth</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#16A34A;">+476.0%</div>
          <div class="kpi-ctx-v2">From $13,380</div>
        </div>
      </div>

      <!-- 5. Best Month Return -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#16A34A;">Best Month Return</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#16A34A;">+60.8%</div>
          <div class="kpi-ctx-v2">2019-05</div>
        </div>
      </div>

      <!-- 6. Worst Month Return -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#DC2626;">Worst Month Return</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#DC2626;">-37.3%</div>
          <div class="kpi-ctx-v2">2022-06</div>
        </div>
      </div>

      <!-- 7. Best Year Return -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#16A34A;">Best Year Return</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#16A34A;">+302.0%</div>
          <div class="kpi-ctx-v2">2020</div>
        </div>
      </div>

      <!-- 8. Worst Year Return -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#DC2626;">Worst Year Return</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#DC2626;">-73.0%</div>
          <div class="kpi-ctx-v2">2018</div>
        </div>
      </div>

      <!-- 9. Max Drawdown -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#DC2626;">Max Drawdown</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#DC2626;">-81.2%</div>
          <div class="kpi-ctx-v2">2018-12-15</div>
        </div>
      </div>

      <!-- 10. Avg Monthly Return -->
      <div class="kpi-card-v2">
        <div class="kpi-header-bar" style="background:#0F4C81;">Avg Monthly Return</div>
        <div class="kpi-body-v2">
          <div class="kpi-val-v2" style="color:#16A34A;">+3.8%</div>
          <div class="kpi-ctx-v2">Per month avg.</div>
        </div>
      </div>

    </div>
  </div>"""

# ============================================================
# PART 3 — INJECT: REPLACE OLD KPI SECTION
# Tim chinh xac tu <!-- Section 1: KPI --> den <!-- Section 2: -->
# ============================================================
import re

pattern = r'<!-- Section 1: KPI -->.*?(?=<!-- Section 2:)'
match = re.search(pattern, html, flags=re.DOTALL)
if match:
    html = html[:match.start()] + NEW_KPI_SECTION + "\n\n  " + html[match.end():]
    print("    KPI section replaced")
else:
    print("    [WARN] Pattern not found, trying fallback...")
    old_start = html.find("<!-- Section 1: KPI -->")
    old_end   = html.find("<!-- Section 2:", old_start)
    if old_start != -1 and old_end != -1:
        html = html[:old_start] + NEW_KPI_SECTION + "\n\n  " + html[old_end:]
        print("    KPI section replaced (fallback)")
    else:
        print("    [ERROR] Could not locate KPI section!")

# ============================================================
# PART 4 — SAVE
# ============================================================
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"\n[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")
print("     Ctrl+Shift+R to refresh browser")
