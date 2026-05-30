"""Fix heatmap bdata: {"dtype":"f8","bdata":"...","shape":"9, 12"}"""
import re, base64, struct, math, json

with open("bitcoin_dashboard copy 2.html", "r", encoding="utf-8") as f:
    html = f.read()

print(f"bdata blocks: {html.count('\"bdata\"')}")

# Pattern: matches shape as STRING "rows, cols"
PATTERN = (
    r'\{"dtype":"([^"]+)","bdata":"'
    r'((?:[A-Za-z0-9+/=]|\\u[0-9a-fA-F]{4})+)'
    r'"(?:,"shape":"([^"]*)")?\}'
)

FMT = {"f8":("d",8), "f4":("f",4), "i4":("i",4), "i8":("q",8), "u4":("I",4)}

def decode_match(m):
    dtype_str = m.group(1)
    bdata_raw = m.group(2)
    shape_str = m.group(3)   # e.g. "9, 12" or None

    bdata_raw = re.sub(r"\\u([0-9a-fA-F]{4})",
                       lambda x: chr(int(x.group(1),16)), bdata_raw)

    fmt_char, byte_size = FMT.get(dtype_str, ("d", 8))
    raw  = base64.b64decode(bdata_raw)
    n    = len(raw) // byte_size
    flat = []
    for i in range(n):
        v = struct.unpack("<" + fmt_char, raw[i*byte_size:(i+1)*byte_size])[0]
        flat.append(None if (math.isnan(v) or math.isinf(v)) else round(float(v), 4))

    # Reshape to 2D if shape provided
    if shape_str:
        dims = [int(x.strip()) for x in shape_str.split(",") if x.strip()]
        if len(dims) == 2:
            rows, cols = dims
            matrix = [flat[i*cols:(i+1)*cols] for i in range(rows)]
            return json.dumps(matrix)

    return json.dumps(flat)

fixed, n = re.subn(PATTERN, decode_match, html)
print(f"Decoded: {n} | bdata remaining: {fixed.count('\"bdata\"')}")

with open("bitcoin_dashboard copy 2.html", "w", encoding="utf-8") as f:
    f.write(fixed)
print(f"[OK] {len(fixed.encode())/1e6:.1f} MB")
