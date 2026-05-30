"""
Fix binary bdata trong HTML: chuyen {"dtype":"f8","bdata":"..."}
thanh JSON array thuong de Plotly.js hieu duoc.
"""
import re
import base64
import struct
import json

TARGET = "bitcoin_dashboard copy 2.html"

print(f"[+] Reading {TARGET}...")
with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

# Dem so luong bdata truoc khi fix
count_before = html.count('"bdata"')
print(f"    Found {count_before} bdata blocks to decode")

# Map dtype -> struct format (little-endian)
DTYPE_MAP = {
    "f8": ("d", 8),   # float64
    "f4": ("f", 4),   # float32
    "i4": ("i", 4),   # int32
    "i8": ("q", 8),   # int64
    "u4": ("I", 4),   # uint32
    "u8": ("Q", 8),   # uint64
}

def decode_bdata_block(match):
    dtype_str = match.group(1)
    # Base64 string co the chua / (la / bi JSON escape)
    # va = (la = bi escape). Unescape truoc khi decode.
    bdata_raw = match.group(2)
    bdata_raw = re.sub(r'\\u([0-9a-fA-F]{4})',
                       lambda m: chr(int(m.group(1), 16)), bdata_raw)

    if dtype_str not in DTYPE_MAP:
        # Khong biet dtype -> giu nguyen
        return match.group(0)

    fmt_char, byte_size = DTYPE_MAP[dtype_str]

    try:
        raw_bytes = base64.b64decode(bdata_raw)
    except Exception as e:
        print(f"    [WARN] base64 decode failed: {e}")
        return match.group(0)

    n = len(raw_bytes) // byte_size
    values = []
    for i in range(n):
        chunk = raw_bytes[i * byte_size : (i + 1) * byte_size]
        val = struct.unpack("<" + fmt_char, chunk)[0]
        # Xu ly NaN va Inf -> null trong JSON
        import math
        if math.isnan(val) or math.isinf(val):
            values.append(None)
        else:
            # Lam tron hop ly: float64 khong can qua nhieu chu so thap phan
            values.append(round(val, 6) if fmt_char in ("d", "f") else int(val))
    return json.dumps(values)

# Pattern: {"dtype":"f8","bdata":"<base64_chua_unicode_escape>"}
# bdata co the chua chu thuong, chu hoa, so, +, /, =, va \uXXXX (escape)
PATTERN = r'\{"dtype":"([^"]+)","bdata":"((?:[A-Za-z0-9+/=]|\\u[0-9a-fA-F]{4})+)"\}'

html_fixed, n_replaced = re.subn(PATTERN, decode_bdata_block, html)

print(f"    Decoded {n_replaced} bdata blocks")

if n_replaced > 0:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(html_fixed)
    size_mb = len(html_fixed.encode("utf-8")) / 1_048_576
    print(f"[OK] Saved: {TARGET}  ({size_mb:.1f} MB)")
    print(f"     Hard refresh browser: Ctrl+Shift+R")
else:
    print("[WARN] Khong tim thay bdata block nao de fix.")
