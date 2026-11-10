"""Build the downloadable spreadsheet templates used by the guides (assets/templates/).
Run: python _tools/make_templates.py   (needs openpyxl)"""
import csv, pathlib
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates"
OUT.mkdir(parents=True, exist_ok=True)

TEAL = "2A9D8F"
INK = "14213D"
HEAD = ["Date", "Source", "Section", "Topic", "Why (C, M or T)", "Next time I will", "Retest on", "Fixed?"]
EXAMPLE = ["", "Practice exam", "Bio/Biochem", "Enzyme inhibition graph", "M", "Say what each axis shows before I read the answers", None, "No"]
SECTIONS = ["Chem/Phys", "CARS", "Bio/Biochem", "Psych/Soc"]


def mcat_error_log():
    wb = Workbook()
    ws = wb.active
    ws.title = "Error log"
    ws.append(HEAD)
    widths = [13, 18, 14, 30, 15, 52, 13, 10]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = w
    thin = Side(style="thin", color="B9C8CD")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=TEAL)
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    rows = 300
    for r in range(2, rows + 2):
        ws[f"G{r}"] = f'=IF(OR(A{r}="",E{r}=""),"",A{r}+IF(E{r}="C",7,2))'
        ws[f"A{r}"].number_format = "yyyy-mm-dd"
        ws[f"G{r}"].number_format = "yyyy-mm-dd"
        ws[f"F{r}"].alignment = Alignment(wrap_text=True, vertical="top")
        for col in "ABCDEFGH":
            ws[f"{col}{r}"].border = Border(bottom=thin)
    # example row (row 2)
    for col, v in zip("ABCDEFH", [None, EXAMPLE[1], EXAMPLE[2], EXAMPLE[3], EXAMPLE[4], EXAMPLE[5], EXAMPLE[7]]):
        if v is not None:
            ws[f"{col}2"] = v
    from datetime import date
    ws["A2"] = date.today()
    ws["A2"].number_format = "yyyy-mm-dd"
    for col in "ABCDEFGH":
        ws[f"{col}2"].font = Font(italic=True, color="5B6B7F")
    dv_sec = DataValidation(type="list", formula1='"' + ",".join(SECTIONS) + '"', allow_blank=True)
    dv_why = DataValidation(type="list", formula1='"C,M,T"', allow_blank=True)
    dv_fix = DataValidation(type="list", formula1='"No,Yes"', allow_blank=True)
    for dv, rng in ((dv_sec, f"C2:C{rows + 1}"), (dv_why, f"E2:E{rows + 1}"), (dv_fix, f"H2:H{rows + 1}")):
        ws.add_data_validation(dv)
        dv.add(rng)
    ws.freeze_panes = "A2"

    s = wb.create_sheet("Weekly count")
    s["A1"] = "Count the letters once a week"
    s["A1"].font = Font(bold=True, size=14, color=INK)
    s["A3"], s["B3"], s["C3"] = "Reason", "Misses", "What it usually means"
    for c in s[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=TEAL)
    meaning = {"C": "Content gap: go back to the source and relearn it", "M": "Misread: slow down on the question and the passage",
               "T": "Timing: practise timed blocks and decide when to skip"}
    for i, k in enumerate("CMT", 4):
        s[f"A{i}"] = k
        s[f"B{i}"] = f"=COUNTIF('Error log'!E2:E{rows + 1},A{i})"
        s[f"C{i}"] = meaning[k]
    s["A8"], s["B8"] = "Section", "Misses"
    for c in s[8]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=TEAL)
    for i, sec in enumerate(SECTIONS, 9):
        s[f"A{i}"] = sec
        s[f"B{i}"] = f"=COUNTIF('Error log'!C2:C{rows + 1},A{i})"
    s["A14"] = "Not yet fixed"
    s["B14"] = f"=COUNTIFS('Error log'!H2:H{rows + 1},\"No\",'Error log'!E2:E{rows + 1},\"<>\")"
    s["A16"] = "FocusFlow Lab, free for personal use. Guide: thefocusflowlab.com/guides/mcat-error-log-template/"
    s["A16"].font = Font(color="5B6B7F", size=9)
    s.column_dimensions["A"].width = 18
    s.column_dimensions["B"].width = 10
    s.column_dimensions["C"].width = 58
    wb.save(OUT / "mcat-error-log-template.xlsx")

    with open(OUT / "mcat-error-log-template.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(HEAD[:6])
        w.writerow(["Example", "Practice exam", "Bio/Biochem", "Enzyme inhibition graph", "M", "Say what each axis shows before I read the answers"])
        for _ in range(20):
            w.writerow([""] * 6)


mcat_error_log()
print("wrote", sorted(p.name for p in OUT.iterdir()))
