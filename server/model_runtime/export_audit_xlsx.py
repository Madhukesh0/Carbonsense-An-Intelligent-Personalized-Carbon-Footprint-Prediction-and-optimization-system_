"""Export the deterministic XGBoost QA audit to a clearly labeled Excel workbook."""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parent
AUDIT_PATH = ROOT / "audits" / "xgb_deterministic_100_scenario_audit.json"
DEFAULT_OUTPUT = Path("/home/ubuntu/exports/CarbonSense_XGBoost_100_Scenario_QA.xlsx")

GREEN = "157F54"
DARK = "102A2D"
MINT = "E5F7EC"
AMBER = "FFF4D6"
WHITE = "FFFFFF"


def style_title(cell) -> None:
    cell.font = Font(size=16, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=DARK)
    cell.alignment = Alignment(vertical="center")


def style_header(row) -> None:
    for cell in row:
        cell.font = Font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=GREEN)
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def add_table(sheet, name: str, start_row: int, end_row: int, end_col: int) -> None:
    table = Table(displayName=name, ref=f"A{start_row}:{get_column_letter(end_col)}{end_row}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium4", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    sheet.add_table(table)


def build_workbook(audit: dict) -> Workbook:
    workbook = Workbook()
    readme = workbook.active
    readme.title = "Read me"
    readme.merge_cells("A1:H1")
    readme["A1"] = "CarbonSense · XGBoost 100-Scenario QA Workbook"
    style_title(readme["A1"])
    readme.row_dimensions[1].height = 28
    readme["A3"] = "Classification"
    readme["B3"] = "DETERMINISTIC SIMULATED QA DATA — not real people, not user records, not model-training data."
    readme["A3"].font = Font(bold=True, color=DARK)
    readme["B3"].font = Font(bold=True, color="9A6200")
    readme["B3"].fill = PatternFill("solid", fgColor=AMBER)
    readme.merge_cells("B3:H3")
    readme["A5"] = "Purpose"
    readme["B5"] = "Exercise the same frozen live XGBoost runtime with 100 bounded low-impact, typical, and high-impact input profiles."
    readme["A6"] = "Model runtime"
    readme["B6"] = "xgb-final-54f-v2 · 34 raw contract columns → 54 transformed features"
    readme["A7"] = "Validation"
    readme["B7"] = "Every result is finite, includes ranked live contributions, and reconciles grouped contributions to prediction within 0.2 kgCO₂e."
    readme["A9"] = "Workbook sheets"
    readme["B9"] = "Summary: QA range and profile bands. Scenarios: 100 complete simulated test inputs and outputs. Contributions: top three live drivers for each scenario."
    for cell in ("A5", "A6", "A7", "A9"):
        readme[cell].font = Font(bold=True, color=GREEN)
    for row in range(3, 10):
        readme[f"B{row}"].alignment = Alignment(wrap_text=True, vertical="top")
    readme.column_dimensions["A"].width = 20
    readme.column_dimensions["B"].width = 105
    for column in "CDEFGH":
        readme.column_dimensions[column].width = 12
    readme.sheet_view.showGridLines = False

    summary = workbook.create_sheet("Summary")
    summary.merge_cells("A1:F1")
    summary["A1"] = "Deterministic QA Summary"
    style_title(summary["A1"])
    summary.row_dimensions[1].height = 28
    summary.append([])
    summary.append(["Measure", "kgCO₂e / month"])
    style_header(summary[3])
    data = audit["summary"]
    summary.append(["Lowest deterministic test result", data["minimumKg"]])
    summary.append(["Highest deterministic test result", data["maximumKg"]])
    summary.append(["Matrix mean", data["meanKg"]])
    summary.append(["Matrix median", data["medianKg"]])
    summary.append([])
    summary.append(["Test band", "Scenario count", "Mean kgCO₂e", "Minimum kgCO₂e", "Maximum kgCO₂e"])
    style_header(summary[9])
    profile_labels = {"low_impact": "Low impact", "typical": "Typical", "high_impact": "High impact"}
    for profile, values in data["byProfile"].items():
        summary.append([profile_labels[profile], values["count"], values["meanKg"], values["minimumKg"], values["maximumKg"]])
    for row in range(4, 8):
        summary[f"B{row}"].number_format = "0.0"
    for row in range(10, 13):
        for column in "CDE":
            summary[f"{column}{row}"].number_format = "0.0"
    add_table(summary, "QASummaryMetrics", 3, 7, 2)
    add_table(summary, "QAProfileBands", 9, 12, 5)
    chart = BarChart()
    chart.title = "Mean model estimate by deterministic test band"
    chart.y_axis.title = "kgCO₂e / month"
    chart.x_axis.title = "Test band"
    chart.add_data(Reference(summary, min_col=3, min_row=9, max_row=12), titles_from_data=True)
    chart.set_categories(Reference(summary, min_col=1, min_row=10, max_row=12))
    chart.height = 7
    chart.width = 13
    summary.add_chart(chart, "G3")
    for column, width in {"A": 34, "B": 18, "C": 18, "D": 20, "E": 20}.items():
        summary.column_dimensions[column].width = width
    summary.sheet_view.showGridLines = False

    scenarios = workbook.create_sheet("Scenarios")
    headers = [
        "Scenario ID", "Test band", "Age", "Gender", "Body type", "Diet", "Shower frequency", "Heating source", "Energy efficiency", "Transport", "Vehicle type", "Vehicle distance (km/month)", "Air travel", "Electricity grid mix", "Grocery spend (model units)", "New clothes/month", "Waste bag size", "Waste bags/week", "TV / PC hours/day", "Internet hours/day", "Social activity", "Recycling", "Cooking appliances", "Prediction (kgCO₂e/month)", "Range low", "Range high", "Contribution reconciliation delta (kg)", "Top driver 1", "Top driver 2", "Top driver 3",
    ]
    scenarios.append(headers)
    style_header(scenarios[1])
    input_order = ["age", "sex", "body_type", "diet", "how_often_shower", "heating_energy_source", "energy_efficiency", "transport", "vehicle_type", "vehicle_monthly_distance_km", "frequency_of_traveling_by_air", "region", "monthly_grocery_bill", "how_many_new_clothes_monthly", "waste_bag_size", "waste_bag_weekly_count", "how_long_tv_pc_daily_hour", "how_long_internet_daily_hour", "social_activity", "recycling", "cooking_with"]
    for row in audit["scenarios"]:
        payload = row["input"]
        drivers = [f"{driver['label']} ({driver['direction']} {driver['shapValue']:+.1f})" for driver in row["topDrivers"]]
        values = [row["scenarioId"], profile_labels[row["profile"]]]
        for key in input_order:
            value = payload[key]
            values.append(", ".join(value) if isinstance(value, list) else value)
        values.extend([row["predictionKg"], row["uncertaintyRange"]["low"], row["uncertaintyRange"]["high"], row["reconciliationDelta"], *drivers])
        scenarios.append(values)
    add_table(scenarios, "QAScenarios", 1, 101, len(headers))
    for row in range(2, 102):
        for column in (24, 25, 26, 27):
            scenarios.cell(row, column).number_format = "0.0"
    scenarios.conditional_formatting.add("X2:X101", ColorScaleRule(start_type="min", start_color="E5F7EC", mid_type="percentile", mid_value=50, mid_color="FFF4D6", end_type="max", end_color="F7D8D2"))
    scenarios.freeze_panes = "A2"
    scenarios.auto_filter.ref = f"A1:{get_column_letter(len(headers))}101"
    widths = [15, 15, 8, 10, 15, 15, 18, 18, 18, 16, 14, 25, 18, 22, 27, 19, 17, 17, 19, 21, 16, 25, 28, 27, 14, 14, 30, 36, 36, 36]
    for index, width in enumerate(widths, start=1):
        scenarios.column_dimensions[get_column_letter(index)].width = width

    contributions = workbook.create_sheet("Top drivers")
    contributions.append(["Scenario ID", "Test band", "Rank", "Driver key", "Driver label", "Contribution (kgCO₂e)", "Direction"])
    style_header(contributions[1])
    for row in audit["scenarios"]:
        for rank, driver in enumerate(row["topDrivers"], start=1):
            contributions.append([row["scenarioId"], profile_labels[row["profile"]], rank, driver["feature"], driver["label"], driver["shapValue"], driver["direction"]])
    add_table(contributions, "QATopDrivers", 1, 301, 7)
    for row in range(2, 302):
        contributions[f"F{row}"].number_format = "+0.0;-0.0;0.0"
    contributions.conditional_formatting.add("F2:F301", ColorScaleRule(start_type="min", start_color="E5F7EC", mid_type="num", mid_value=0, mid_color="FFFFFF", end_type="max", end_color="F7D8D2"))
    contributions.freeze_panes = "A2"
    for column, width in {"A": 16, "B": 15, "C": 8, "D": 28, "E": 30, "F": 26, "G": 14}.items():
        contributions.column_dimensions[column].width = width

    for sheet in (summary, scenarios, contributions):
        sheet.sheet_view.showGridLines = False
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    return workbook


def main() -> None:
    if not AUDIT_PATH.exists():
        raise FileNotFoundError(f"Missing deterministic audit: {AUDIT_PATH}")
    audit = json.loads(AUDIT_PATH.read_text())
    workbook = build_workbook(audit)
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(DEFAULT_OUTPUT)
    print(json.dumps({"output": str(DEFAULT_OUTPUT), "scenarioCount": audit["scenarioCount"], "sheets": workbook.sheetnames}))


if __name__ == "__main__":
    main()
