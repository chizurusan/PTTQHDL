"""
Chuyen dashboard tu dark theme sang light theme.
Chi thay CSS va Plotly layout colors, khong doi data / chart structure.
"""
import re

TARGET = "bitcoin_dashboard copy 2.html"

print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

# ============================================================
# PART 1 — REPLACE ENTIRE <style> BLOCK
# ============================================================
NEW_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #F8FAFC;
  color: #0F172A;
  line-height: 1.6;
}

/* ── Header ── */
.header {
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF7ED 100%);
  border-bottom: 2px solid rgba(245, 158, 11, 0.25);
  padding: 32px 40px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.06);
}
.header h1 { font-size: 2.5em; color: #F59E0B; font-weight: 800; letter-spacing: 1px; }
.header p  { color: #64748B; margin-top: 6px; font-size: 1em; }

/* ── Main container ── */
.container { max-width: 1420px; margin: 0 auto; padding: 28px 20px; }

/* ── Section box ── */
.section {
  margin-bottom: 36px;
  background: #FFFFFF;
  border-radius: 18px;
  padding: 24px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}
.section-title {
  font-size: 1.2em; font-weight: 700;
  color: #F59E0B;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #E2E8F0;
  display: flex; align-items: center; gap: 8px;
}

/* ── KPI Grid ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
  gap: 14px;
}
.kpi-card {
  background: #FFFFFF;
  border-radius: 14px;
  padding: 16px 18px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
  transition: transform .2s, box-shadow .2s, background .2s, border-color .2s;
}
.kpi-card:hover {
  transform: translateY(-2px);
  background: #FFF7ED;
  border-color: rgba(245, 158, 11, 0.35);
  box-shadow: 0 10px 28px rgba(245, 158, 11, 0.12);
}
.kpi-title { font-size: .72em; color: #64748B; text-transform: uppercase; letter-spacing: .9px; margin-bottom: 6px; }
.kpi-value { font-size: 1.25em; font-weight: 700; margin-bottom: 4px; color: #0F172A; }
.kpi-sub   { font-size: .72em; color: #94A3B8; }

/* ── Event legend badges ── */
.legend-badges { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.legend-badge  {
  padding: 3px 10px; border-radius: 20px;
  font-size: .73em; font-weight: 600; border: 1px solid;
}

/* ── Insight ── */
.insight-box { padding: 4px 0; }
.insight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 12px; margin: 18px 0;
}
.insight-item {
  background: #F8FAFC;
  border-radius: 8px; padding: 14px 18px;
  border: 1px solid #E2E8F0;
  display: flex; flex-direction: column; gap: 5px;
}
.insight-label { font-size: .82em; color: #64748B; }
.insight-value { font-size: 1.1em; font-weight: 700; color: #0F172A; }
.insight-value.positive { color: #16A34A; }
.insight-value.negative { color: #DC2626; }
.insight-narrative {
  background: #FFFBEB;
  border-radius: 8px; padding: 20px 24px;
  border-left: 4px solid #F59E0B;
  margin-top: 14px;
}
.insight-narrative p {
  margin-bottom: 12px; color: #374151; font-size: .94em;
}

/* ── Footer ── */
.footer {
  text-align: center; padding: 22px;
  color: #64748B; font-size: .8em;
  border-top: 1px solid #E2E8F0; margin-top: 10px;
}
"""

# Tim va thay the block <style>...</style>
html, n = re.subn(
    r'(<style>)(.*?)(</style>)',
    lambda m: m.group(1) + NEW_CSS + m.group(3),
    html, flags=re.DOTALL
)
print(f"    CSS block replaced: {n}")

# ============================================================
# PART 2 — KPI CARD INLINE COLORS
# Doi mau inline trong cac the HTML (KPI values, insight values)
# Khong dung replace_all vo toi vi mau nay co the co trong Plotly trace
# ============================================================
print("[+] Updating inline HTML colors...")

# Thay the mau trong KPI va insight HTML (trong .kpi-value / .insight-value inline style)
kpi_color_map = {
    # Dark muted text → light slate
    'style="color:#8892A4"':       'style="color:#64748B"',
    # Positive green (dark) → light green
    'style="color:#00C896"':       'style="color:#16A34A"',
    'style="color:#00C896;font-weight:700"': 'style="color:#16A34A;font-weight:700"',
    # Negative red (dark) → clear red
    'style="color:#FF4B4B"':       'style="color:#DC2626"',
    'style="color:#FF4B4B;font-weight:700"': 'style="color:#DC2626;font-weight:700"',
    # Drawdown orange-red
    'style="color:#FF6B35"':       'style="color:#DC2626"',
    # ATH gold → amber
    'style="color:#FFD700"':       'style="color:#D97706"',
    # Bitcoin orange — giu nguyen
    # 'style="color:#F7931A"' → giu nguyen
}
for old, new in kpi_color_map.items():
    html = html.replace(old, new)

# ============================================================
# PART 3 — EVENT LEGEND BADGES
# Thay inline style cua .legend-badge
# ============================================================
print("[+] Updating event badge colors...")

badge_map = {
    # ATH: vang nhat
    'style="color:#FFD700;border-color:#FFD700;background:#FFD70018"':
        'style="color:#D97706;border-color:#FCD34D;background:#FFFBEB"',
    # Crash: do nhat
    'style="color:#FF4B4B;border-color:#FF4B4B;background:#FF4B4B18"':
        'style="color:#DC2626;border-color:#FCA5A5;background:#FEF2F2"',
    # Halving: xanh la
    'style="color:#00C896;border-color:#00C896;background:#00C89618"':
        'style="color:#059669;border-color:#6EE7B7;background:#ECFDF5"',
    # ETF: xanh duong
    'style="color:#3498DB;border-color:#3498DB;background:#3498DB18"':
        'style="color:#0284C7;border-color:#7DD3FC;background:#F0F9FF"',
    # Institutional: tim
    'style="color:#9B59B6;border-color:#9B59B6;background:#9B59B618"':
        'style="color:#7C3AED;border-color:#C4B5FD;background:#F5F3FF"',
    # Regulation: cam dat
    'style="color:#F39C12;border-color:#F39C12;background:#F39C1218"':
        'style="color:#C2410C;border-color:#FDBA74;background:#FFF7ED"',
    # Milestone: teal
    'style="color:#1ABC9C;border-color:#1ABC9C;background:#1ABC9C18"':
        'style="color:#0F766E;border-color:#5EEAD4;background:#F0FDFA"',
}
for old, new in badge_map.items():
    html = html.replace(old, new)

# ============================================================
# PART 4 — PLOTLY CHART LAYOUT COLORS (trong JSON embedded)
# Chi thay cac mau layout (background, font, grid, axis)
# KHONG thay mau cua trace data (orange line, green/red candles, etc.)
# ============================================================
print("[+] Updating Plotly layout colors...")

# --- paper_bgcolor & plot_bgcolor ---
# Cac mau nen toi can doi sang trang
dark_bgs = [
    '"#0D1117"', '"#161B22"', '"#1A1A2E"',
    '"#0d1117"', '"#161b22"',
    '"rgba(13,17,23,1)"', '"rgba(22,27,34,1)"',
]
for dark in dark_bgs:
    html = html.replace(f'"paper_bgcolor":{dark}', '"paper_bgcolor":"#FFFFFF"')
    html = html.replace(f'"plot_bgcolor":{dark}',  '"plot_bgcolor":"#FFFFFF"')

# Fallback: bat cu paper/plot_bgcolor nao con la mau toi
html = re.sub(r'"paper_bgcolor":"#[0-9A-Fa-f]{6}"',
              '"paper_bgcolor":"#FFFFFF"', html)
html = re.sub(r'"plot_bgcolor":"#[0-9A-Fa-f]{6}"',
              '"plot_bgcolor":"#FFFFFF"', html)

# --- Grid color ---
for gc in ['"white"', '"#21262D"', '"#30363D"', '"#1E2A38"',
           '"rgba(255,255,255,0.1)"', '"rgba(255, 255, 255, 0.1)"']:
    html = html.replace(f'"gridcolor":{gc}',
                        '"gridcolor":"rgba(148,163,184,0.25)"')

# --- Axis line color ---
for lc in ['"white"', '"#30363D"', '"#21262D"', '"#E6EDF3"']:
    html = html.replace(f'"linecolor":{lc}', '"linecolor":"#CBD5E1"')

# --- Tick color ---
for tc in ['"#8892A4"', '"#8B949E"', '"#6E7681"']:
    html = html.replace(f'"tickcolor":{tc}', '"tickcolor":"#94A3B8"')

# --- Font color trong title, axis, legend (khong thay mau trace) ---
# Chi thay font color trong layout context (title.font, axis.tickfont, etc.)
# Dung pattern chon loc hon
for fc in ['"#E6EDF3"', '"#CDD6E0"', '"#8892A4"', '"#8B949E"']:
    # Thay trong cac font dict trong layout (title, tickfont, etc.)
    html = re.sub(
        r'("(?:title|tickfont|font|legend)":\{"[^}]*?"color"):' + re.escape(fc),
        r'\1:"#334155"', html)

# --- Legend background ---
for lb in ['"#161B22"', '"#1A1A2E"', '"#0D1117"',
           '"rgba(22,27,34,0.8)"', '"rgba(13,17,23,0.8)"']:
    html = html.replace(f'"bgcolor":{lb}', '"bgcolor":"rgba(255,255,255,0.92)"')

# Phong bao bat cu legend bgcolor nao con toi
html = re.sub(
    r'("bgcolor":")(#(?:0D1117|161B22|1A1A2E|0d1117|161b22))',
    r'\1rgba(255,255,255,0.92)', html)

# --- Legend border ---
for lbc in ['"#30363D"', '"#21262D"']:
    html = html.replace(f'"bordercolor":{lbc}', '"bordercolor":"#E2E8F0"')

# --- Hoverlabel ---
for hb in ['"#161B22"', '"#1A1A2E"', '"#0D1117"']:
    html = html.replace(f'"bgcolor":{hb}', '"bgcolor":"#FFFFFF"')
    # hoverlabel bordercolor
    html = html.replace(
        f'"hoverlabel":{{"bgcolor":{hb}',
        '"hoverlabel":{"bgcolor":"#FFFFFF"')

html = re.sub(r'"hoverlabel":\{"bgcolor":"#(?:161B22|1A1A2E|0D1117|161b22|0d1117)"',
              '"hoverlabel":{"bgcolor":"#FFFFFF"', html)

# Hoverlabel border
for hbc in ['"#30363D"', '"#21262D"']:
    html = re.sub(
        r'("hoverlabel":[^}]{0,200}"bordercolor"):' + re.escape(hbc),
        r'\1:"#E2E8F0"', html)

# Hoverlabel font color (text trong tooltip)
html = re.sub(
    r'("hoverlabel":[^}]{0,300}"color"):("(?:#E6EDF3|#CDD6E0|#8892A4)")',
    r'\1:"#0F172A"', html)

# --- Zero line color ---
html = re.sub(r'"zerolinecolor":"#(?:30363D|21262D|8892A4)"',
              '"zerolinecolor":"#CBD5E1"', html)

# --- Title font color (chart titles) ---
html = re.sub(r'("title":\{"text":"[^"]*","font":\{"size":\d+,"color"):"#(?:E6EDF3|CDD6E0|8892A4)"',
              r'\1:"#0F172A"', html)

# ============================================================
# PART 5 — INSIGHT TEXT & STRONG TAG COLORS
# ============================================================
print("[+] Updating insight text colors...")

html = html.replace('style="color:#00C896">', 'style="color:#16A34A">')
html = html.replace('style="color:#FF4B4B">', 'style="color:#DC2626">')
html = html.replace('color:#CDD6E0', 'color:#374151')

# ============================================================
# PART 6 — ANIMATION SECTION dark colors
# ============================================================
print("[+] Updating animation section colors...")

anim_colors = {
    # Card backgrounds trong animated section
    'background:#161B22': 'background:#FFFFFF',
    'background:#0D1117': 'background:#F8FAFC',
    'background:#1A1A2E': 'background:#F8FAFC',
    # Border colors
    'border-color:#30363D': 'border-color:#E2E8F0',
    'bordercolor:#30363D':  'bordercolor:#E2E8F0',
    # Text
    'color:#8892A4':        'color:#64748B',
    'color:#E6EDF3':        'color:#0F172A',
    # Inline style blocks trong section animation
    'background:#161B22;': 'background:#FFFFFF;',
    'background: #161B22': 'background: #FFFFFF',
    'background: #0D1117': 'background: #F8FAFC',
}
for old, new in anim_colors.items():
    html = html.replace(old, new)

# ============================================================
# PART 7 — SAVE
# ============================================================
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = len(html.encode("utf-8")) / 1_048_576
print(f"\n[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")
print("     Ctrl+Shift+R de hard refresh browser")
