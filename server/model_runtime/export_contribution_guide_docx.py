"""Create a plain-language Word guide for a supplied CarbonSense contribution result."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

OUTPUT = Path("/home/ubuntu/exports/CarbonSense_715kgCO2e_Contribution_Guide.docx")
GREEN = RGBColor(21, 127, 84)
DARK = RGBColor(16, 42, 45)
AMBER = "FFF4D6"

CONTRIBUTIONS = [
    ("01", "Digital use", -116.312, "The digital-use answers in this submitted profile made the model estimate lower than its internal base value. This is a strong model effect in this result."),
    ("02", "Air travel frequency", -97.489, "The selected air-travel frequency made the model estimate lower than its internal base value. This is also a strong model effect in this result."),
    ("03", "New clothing purchases", -64.540, "The entered new-clothing frequency moved the model estimate downward compared with the model’s base value."),
    ("04", "Home energy and region", 59.515, "The combined heating source, energy-efficiency answer, and electricity-grid mix moved the model estimate upward compared with its base value."),
    ("05", "Waste and recycling", -50.232, "The selected waste-bag and recycling answers moved the model estimate downward compared with its base value."),
    ("06", "Diet and grocery", 46.377, "The combination of diet and grocery-spending inputs moved the model estimate upward compared with its base value."),
    ("07", "Transport and distance", -6.587, "The transport mode and monthly distance inputs made a small downward movement in this model result."),
    ("08", "Energy efficiency", 0.225, "This is a very small upward model movement. It is close to zero and should not be treated as a meaningful ranking signal."),
    ("09", "Vehicle type", 0.045, "This is effectively zero for practical interpretation. The selected vehicle type had almost no separate movement in this particular model result."),
    ("10", "Profile fields", -0.044, "This group includes profile-coded fields such as gender and body type. Its effect is effectively zero in this result. Age is contextual in the questionnaire and is not a direct model feature."),
    ("11", "Social activity", 0.025, "This is effectively zero for practical interpretation in this result."),
    ("12", "Cooking equipment", -0.023, "This is effectively zero for practical interpretation in this result."),
    ("13", "Shower frequency", 0.002, "This is effectively zero for practical interpretation in this result."),
]


def shade_cell(cell, color: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shade = OxmlElement("w:shd")
    shade.set(qn("w:fill"), color)
    properties.append(shade)


def cell_text(cell, value: str, bold: bool = False, size: float = 8, color: RGBColor | None = None) -> None:
    cell.text = ""
    run = cell.paragraphs[0].add_run(value)
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color


def add_heading(document: Document, text: str, level: int = 1) -> None:
    paragraph = document.add_heading(text, level=level)
    for run in paragraph.runs:
        run.font.color.rgb = DARK if level == 1 else GREEN


def add_notice(document: Document, text: str) -> None:
    table = document.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    shade_cell(cell, AMBER)
    cell_text(cell, text, bold=True, size=9, color=DARK)


def meaning(value: float) -> str:
    if abs(value) < 1:
        return "Negligible in this result"
    if abs(value) < 10:
        return "Small model movement"
    if abs(value) < 50:
        return "Meaningful model movement"
    return "Strong model movement"


def build_document() -> Document:
    result = 715.0
    net_contribution = round(sum(value for _, _, value, _ in CONTRIBUTIONS), 3)
    approximate_base = round(result - net_contribution, 3)

    document = Document()
    document.core_properties.title = "CarbonSense 715 kgCO2e Contribution Guide"
    document.core_properties.author = "Manus AI"
    document.styles["Normal"].font.name = "Aptos"
    document.styles["Normal"].font.size = Pt(10)

    title = document.add_heading("Your 715 kgCO₂e Model Contribution Guide", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = DARK
    subtitle = document.add_paragraph("Plain-language explanation of the plus and minus values in your live XGBoost breakdown")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in subtitle.runs:
        run.font.italic = True
        run.font.color.rgb = GREEN

    add_notice(document, "Important: These values explain how the deployed model arrived at this estimate from your submitted answers. They are not direct emissions measurements and they do not prove causal environmental impact.")

    add_heading(document, "The simple meaning of + and −", 1)
    document.add_paragraph(
        "A plus sign (+) means that the group of answers pushed this model estimate above the model’s internal base value. A minus sign (−) means that the group of answers pushed this model estimate below the base value. It does not mean that you produced negative emissions, and it does not mean a minus answer is automatically good or a plus answer is automatically bad. It is only the direction of the model’s calculation for this submitted profile."
    )

    add_heading(document, "How the number is built", 1)
    calculation = document.add_paragraph()
    calculation.add_run("Model estimate ≈ internal base value + all signed contribution groups. ").bold = True
    calculation.add_run(f"The displayed contribution values add to {net_contribution:+.3f} kgCO₂e. Using the rounded result shown (715 kgCO₂e), this implies an approximate base value of {approximate_base:.3f} kgCO₂e. The exact internal values can differ slightly because the displayed result and contribution figures are rounded.")

    add_heading(document, "Your most important signals", 1)
    document.add_paragraph(
        "For this result, the strongest downward model movements are Digital use, Air travel frequency, New clothing purchases, and Waste and recycling. The strongest upward model movements are Home energy and region and Diet and grocery. Focus on the size of the number first: movements under about 1 kgCO₂e are practically negligible in this particular result."
    )

    document.add_page_break()
    add_heading(document, "Detailed guide for every displayed group", 1)
    table = document.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    headers = ["Rank", "Model group", "Contribution", "What the sign means here", "Plain-language interpretation"]
    for index, header in enumerate(headers):
        cell_text(table.cell(0, index), header, bold=True, size=8, color=RGBColor(255, 255, 255))
        shade_cell(table.cell(0, index), "157F54")
    for rank, label, value, explanation in CONTRIBUTIONS:
        cells = table.add_row().cells
        cell_text(cells[0], rank, size=7.5)
        cell_text(cells[1], label, bold=True, size=7.5)
        cell_text(cells[2], f"{value:+.3f} kg", bold=True, size=7.5, color=GREEN if value < 0 else RGBColor(186, 91, 61))
        cell_text(cells[3], f"{'Lowers' if value < 0 else 'Raises'} estimate relative to base\n{meaning(value)}", size=7.5)
        cell_text(cells[4], explanation, size=7.5)

    add_heading(document, "How to use this correctly", 1)
    document.add_paragraph(
        "Use the large positive groups to decide what to explore with the transparent baseline or What-if tool. In this result, Home energy and region and Diet and grocery are the clearest positive model signals to investigate. Use the large negative groups to understand why the model is lower than its base value. Do not use this chart alone to claim that one behavior caused a known amount of real emissions; use it as an explanation of this model output and compare any planned change with a new result or the transparent baseline."
    )

    add_heading(document, "What this guide does not say", 1)
    document.add_paragraph(
        "It does not say that digital use physically removes 116.312 kgCO₂e, that flying rarely guarantees a 97.489 kgCO₂e reduction, or that home energy physically adds 59.515 kgCO₂e. Those are signed contribution values from the frozen model for this one submitted profile. The target is formula-derived and synthetic, so the result is best used for indicative comparison and decision support."
    )

    source = document.add_paragraph()
    source.add_run("Source: ").bold = True
    source.add_run("The live XGBoost breakdown values supplied from the CarbonSense result: 715 kgCO₂e/month, indicative range 689–740 kgCO₂e/month.")
    return document


def main() -> None:
    document = build_document()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
