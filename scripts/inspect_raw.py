"""Compact inventory of data/raw -> docs/data_inventory.md (sheets, shape, header rows, dtypes, head).
Run once after adding raw files; agents read the .md instead of opening binaries (saves tokens).
Usage: python scripts/inspect_raw.py [--rows 8]"""
import sys, argparse
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from htd.config import RAW, ROOT

ap = argparse.ArgumentParser(); ap.add_argument("--rows", type=int, default=8)
a = ap.parse_args()
pd.set_option("display.width", 200, "display.max_columns", 30, "display.max_colwidth", 25)


def sheets(p: Path) -> dict:
    ext = p.suffix.lower()
    if ext == ".csv":
        for enc in ("utf-8", "cp1250"):
            try:
                first = p.open(encoding=enc).readline()
                sep = ";" if first.count(";") >= first.count(",") else ","
                return {f"csv enc={enc} sep='{sep}'": pd.read_csv(p, sep=sep, encoding=enc, header=None, dtype=str)}
            except UnicodeDecodeError:
                continue
    eng = "xlrd" if ext == ".xls" else "openpyxl"
    return pd.read_excel(p, sheet_name=None, header=None, engine=eng, dtype=str)


out = ["# Raw data inventory (auto: scripts/inspect_raw.py)\n", "header=None -> row numbers are raw. Find real header row before loading.\n"]
files = sorted(f for f in RAW.iterdir() if f.is_file() and not f.name.startswith("."))
for f in files:
    out.append(f"\n## {f.name} ({f.stat().st_size // 1024} KB)")
    try:
        for name, df in sheets(f).items():
            nn = df.notna().sum()
            out.append(f"\n### sheet `{name}` shape={df.shape} non-null/col={nn.tolist()[:20]}")
            out.append("```\n" + df.head(a.rows).to_string(max_cols=20) + "\n...\n" + df.tail(3).to_string(max_cols=20) + "\n```")
    except Exception as e:
        out.append(f"ERROR: {type(e).__name__}: {e}")
if not files:
    out.append("\n(no files in data/raw yet)")
dst = ROOT / "docs" / "data_inventory.md"
dst.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {dst} ({len(files)} files)")
