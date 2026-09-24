"""One-shot UI sweep: raw slate/emerald/red utility classes -> semantic tokens.

Order of operations per file:
1. literal light+dark pair collapses (longest first),
2. dark:- and dark:hover:/focus: compounds,
3. hover:/focus:/group-hover: compounds (guarded so they don't double-hit),
4. standalone utilities (guarded so dark:/hover: remnants never re-match),
5. button pass: text-white -> text-primary-foreground on bg-primary lines.

Every replacement is a plain string — no regex group interpolation, so an
absent alpha suffix can never produce "None" or "bg-primary/" artifacts.
"""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "client" / "src"

# ---------------------------------------------------------------- 1. literal pairs
PAIRS = [
    ("text-slate-900 dark:text-white", "text-foreground"),
    ("text-slate-800 dark:text-white", "text-foreground"),
    ("text-slate-700 dark:text-white", "text-foreground"),
    ("text-slate-700 dark:text-slate-200", "text-secondary-foreground"),
    ("text-slate-700 dark:text-slate-300", "text-secondary-foreground"),
    ("text-slate-600 dark:text-slate-200", "text-secondary-foreground"),
    ("text-slate-600 dark:text-slate-300", "text-muted-foreground"),
    ("text-slate-600 dark:text-slate-400", "text-muted-foreground"),
    ("text-slate-500 dark:text-slate-300", "text-muted-foreground"),
    ("text-slate-500 dark:text-slate-400", "text-muted-foreground"),
    ("text-emerald-700 dark:text-emerald-300", "text-primary"),
    ("text-emerald-700 dark:text-emerald-400", "text-primary"),
    ("text-emerald-800 dark:text-emerald-300", "text-primary"),
    ("text-emerald-800 dark:text-emerald-400", "text-primary"),
    ("bg-emerald-100 dark:bg-emerald-950", "bg-primary/10 dark:bg-primary/20"),
    ("bg-emerald-50 dark:bg-emerald-950", "bg-primary/8 dark:bg-primary/20"),
    ("bg-emerald-100 dark:bg-emerald-950/70", "bg-primary/10 dark:bg-primary/20"),
    ("bg-emerald-100/80 dark:bg-emerald-950", "bg-primary/10 dark:bg-primary/20"),
    ("text-emerald-800 dark:text-emerald-200", "text-primary"),
]

# ------------------------------------------------- 2. dark: and dark:hover: compounds
DARK = [
    (r"dark:text-emerald-\d+(/\d+)?", "dark:text-primary"),
    (r"dark:text-slate-(?:600|700|800|900)(/\d+)?", "dark:text-foreground"),
    (r"dark:text-slate-\d+(/\d+)?", "dark:text-muted-foreground"),
    (r"(?<!\w)dark:text-white\b", "dark:text-foreground"),
    (r"dark:bg-emerald-950(/\d+)?", "dark:bg-primary/20"),
    (r"dark:bg-emerald-(?:50|100)(/\d+)?", "dark:bg-primary/15"),
    (r"dark:bg-emerald-(?:200|300)(/\d+)?", "dark:bg-primary/20"),
    (r"dark:bg-emerald-(?:400|500|600|700|800|900)(/\d+)?", "dark:bg-primary"),
    (r"dark:border-emerald-\d+(/\d+)?", "dark:border-primary/25"),
    (r"dark:hover:bg-emerald-\d+(/\d+)?", "dark:hover:bg-primary/20"),
    (r"dark:hover:text-emerald-\d+(/\d+)?", "dark:hover:text-primary"),
    (r"dark:hover:bg-red-950(/\d+)?", "dark:hover:bg-destructive/15"),
    (r"dark:bg-red-950(/\d+)?", "dark:bg-destructive/15"),
    (r"dark:border-red-\d+(/\d+)?", "dark:border-destructive/30"),
    (r"dark:text-red-\d+(/\d+)?", "dark:text-destructive"),
    (r"dark:bg-slate-700(/\d+)?", "dark:bg-white/15"),
    (r"dark:bg-slate-800(/\d+)?", "dark:bg-white/10"),
    (r"dark:bg-slate-900(/\d+)?", "dark:bg-white/5"),
    (r"dark:bg-slate-950(/\d+)?", "dark:bg-neutral-900"),
    (r"dark:border-slate-\d+(/\d+)?", "dark:border-white/10"),
]

# ------------------------------------------------- 3. interaction compounds (no dark:)
COMPOUND = [
    (r"(?<![-\w])hover:bg-emerald-50(/\d+)?", "hover:bg-primary/8"),
    (r"(?<![-\w])hover:bg-emerald-100(/\d+)?", "hover:bg-primary/10"),
    (r"(?<![-\w])hover:bg-emerald-200(/\d+)?", "hover:bg-primary/20"),
    (r"(?<![-\w])hover:bg-emerald-(?:300|400)(/\d+)?", "hover:bg-primary/30"),
    (r"(?<![-\w])hover:bg-emerald-500(/\d+)?", "hover:bg-primary/85"),
    (r"(?<![-\w])hover:bg-emerald-(?:600|700)(/\d+)?", "hover:bg-primary/90"),
    (r"(?<![-\w])hover:bg-emerald-(?:800|900)(/\d+)?", "hover:bg-primary"),
    (r"(?<![-\w])hover:bg-slate-100(/\d+)?", "hover:bg-muted"),
    (r"(?<![-\w])hover:bg-slate-200(/\d+)?", "hover:bg-muted"),
    (r"(?<![-\w])hover:bg-slate-50(/\d+)?", "hover:bg-muted/50"),
    (r"(?<![-\w])hover:text-slate-(?:900|800)(/\d+)?", "hover:text-foreground"),
    (r"(?<![-\w])hover:text-emerald-\d+(/\d+)?", "hover:text-primary"),
    (r"(?<![-\w])hover:border-emerald-\d+(/\d+)?", "hover:border-primary"),
    (r"(?<![-\w])hover:bg-red-50(/\d+)?", "hover:bg-destructive/10"),
    (r"(?<![-\w])hover:bg-red-100(/\d+)?", "hover:bg-destructive/15"),
    (r"(?<![-\w])hover:text-red-\d+(/\d+)?", "hover:text-destructive"),
    (r"(?<![-\w])focus:border-emerald-\d+(/\d+)?", "focus:border-primary"),
    (r"(?<![-\w])focus:ring-emerald-\d+(/\d+)?", "focus:ring-ring/30"),
    (r"(?<![-\w])group-hover:text-emerald-\d+(/\d+)?", "group-hover:text-primary"),
]

# ------------------------------------------------- 4. standalone utilities
PLAIN = [
    (r"(?<![-\w:])text-slate-(?:900|800)(/\d+)?", "text-foreground"),
    (r"(?<![-\w:])text-slate-700(/\d+)?", "text-secondary-foreground"),
    (r"(?<![-\w:])text-slate-\d+(/\d+)?", "text-muted-foreground"),
    (r"(?<![-\w:])text-emerald-\d+(/\d+)?", "text-primary"),
    (r"(?<![-\w:])bg-emerald-50(/\d+)?", "bg-primary/8"),
    (r"(?<![-\w:])bg-emerald-100(/\d+)?", "bg-primary/10"),
    (r"(?<![-\w:])bg-emerald-200(/\d+)?", "bg-primary/20"),
    (r"(?<![-\w:])bg-emerald-300(/\d+)?", "bg-primary/35"),
    (r"(?<![-\w:])bg-emerald-400(/\d+)?", "bg-primary/50"),
    (r"(?<![-\w:])bg-emerald-500(/\d+)?", "bg-primary/70"),
    (r"(?<![-\w:])bg-emerald-600(/\d+)?", "bg-primary/90"),
    (r"(?<![-\w:])bg-emerald-(?:700|800)(/\d+)?", "bg-primary"),
    (r"(?<![-\w:])bg-emerald-900(/\d+)?", "bg-primary/85"),
    (r"(?<![-\w:])bg-emerald-950(/\d+)?", "bg-primary/10"),
    (r"(?<![-\w:])bg-slate-950/40", "bg-black/40"),
    (r"(?<![-\w:])bg-slate-(?:100|200)(/\d+)?", "bg-muted"),
    (r"(?<![-\w:])bg-slate-50(/\d+)?", "bg-muted/40"),
    (r"(?<![-\w:])border-slate-\d+(/\d+)?", "border-border"),
    (r"(?<![-\w:])border-emerald-950(/\d+)?", "border-border"),
    (r"(?<![-\w:])border-emerald-(?:50|100|200|300)(/\d+)?", "border-border"),
    (r"(?<![-\w:])border-emerald-(?:500|600|700|800|900)(/\d+)?", "border-primary"),
    (r"(?<![-\w:])border-emerald-\d+(/\d+)?", "border-primary/40"),
    (r"(?<![-\w:])ring-emerald-\d+(/\d+)?", "ring-primary/40"),
    (r"(?<![-\w:])outline-emerald-\d+(/\d+)?", "outline-primary"),
    (r"(?<![-\w:])accent-emerald-\d+(/\d+)?", "accent-primary"),
    (r"(?<![-\w:])shadow-emerald-\d+(/\d+)?", "shadow-primary/20"),
    (r"(?<![-\w:])text-red-(?:500|600|700|800|900)(/\d+)?", "text-destructive"),
    (r"(?<![-\w:])bg-red-50(/\d+)?", "bg-destructive/10"),
    (r"(?<![-\w:])bg-red-100(/\d+)?", "bg-destructive/15"),
    (r"(?<![-\w:])border-red-\d+(/\d+)?", "border-destructive/30"),
]

COMPILED = [
    (section, [(re.compile(p), r) for p, r in sec])
    for section, sec in (("dark", DARK), ("compound", COMPOUND), ("plain", PLAIN))
]


def button_pass(text: str) -> tuple[str, int]:
    """Solid primary buttons must not pair white text with a token that flips
    light/dark: switch text-white -> text-primary-foreground on those lines."""
    count = 0

    def fix_line(m: re.Match[str]) -> str:
        nonlocal count
        line = m.group(0)
        if re.search(r"\bbg-primary(/\d+)?\b", line) and "text-white" in line and "dark:" not in line:
            count += 1
            return line.replace("text-white", "text-primary-foreground")
        return line

    return re.sub(r"[^\n]*", fix_line, text), count


def sweep_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    text = original
    count = 0
    for src, dst in PAIRS:
        n = text.count(src)
        if n:
            text = text.replace(src, dst)
            count += n
    for _, rules in COMPILED:
        for pattern, repl in rules:
            text, n = pattern.subn(repl, text)
            count += n
    text, n = button_pass(text)
    count += n
    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
    return count


def main() -> None:
    targets = sorted(
        list((SRC / "pages").rglob("*.tsx"))
        + list((SRC / "pages").rglob("*.ts"))
        + list((SRC / "components").rglob("*.tsx"))
    )
    total = 0
    for f in targets:
        if ".test." in f.name or f.parent.name == "ui":
            continue
        n = sweep_file(f)
        if n:
            print(f"{n:4d}  {f.relative_to(SRC.parent)}")
        total += n
    print(f"total replacements: {total}")


if __name__ == "__main__":
    main()
