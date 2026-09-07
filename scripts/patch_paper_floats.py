"""Idempotent float fixes for the IEEE paper (written as file to avoid shell escaping)."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Carbonsense_IEEE_Paper_Updated.tex"
src = p.read_text(encoding="utf8")
changed = []

# 1) API table open -> table*
if "\\begin{table*}" not in src:
    a = ("% ---------- API TABLE ----------\n"
         "\\begin{table}[!t]\n"
         "\\caption{CarbonSense Core API Endpoints}")
    if a in src:
        src = src.replace(
            a,
            ("% ---------- API TABLE (two-column span so it never collides with figures) ----------\n"
             "\\FloatBarrier\n"
             "\\begin{table*}[!t]\n"
             "\\caption{CarbonSense Core API Endpoints}"),
            1,
        )
        changed.append("table* open")

# 2) closing tag -> \end{table*}
if src.count("\\end{table*}") == 0:
    a = ("GET  & /api/v1/admin/users & User management & Super admin \\\\\n"
         "\\bottomrule\n"
         "\\end{tabular}\n"
         "\\end{table}\n")
    if a in src:
        src = src.replace(a, a.replace("\\end{table}", "\\end{table*}"), 1)
        changed.append("table* close")

# 3) barrier between the dataflow figure and Database Schema subsection
needle = "\\end{figure}\n\n\\subsection{Database Schema}"
if needle in src and "\\end{figure}\n\n\\FloatBarrier\n\n\\subsection{Database Schema}" not in src:
    src = src.replace(needle, "\\end{figure}\n\n\\FloatBarrier\n\n\\subsection{Database Schema}", 1)
    changed.append("db barrier")

p.write_text(src, encoding="utf8", newline="")

final = p.read_text(encoding="utf8")
print("applied:", changed or "nothing needed")
print("table* open:", "\\begin{table*}[!t]" in final)
print("end table* count:", final.count("\\end{table*}"))
print("barrier count:", final.count("\\FloatBarrier"))
