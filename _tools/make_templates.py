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
        ws[f"G{r}"] = f'=IF(OR(NOT(ISNUMBER(A{r})),E{r}=""),"",A{r}+IF(E{r}="C",7,2))'
        ws[f"A{r}"].number_format = "yyyy-mm-dd"
        ws[f"G{r}"].number_format = "yyyy-mm-dd"
        ws[f"F{r}"].alignment = Alignment(wrap_text=True, vertical="top")
        for col in "ABCDEFGH":
            ws[f"{col}{r}"].border = Border(bottom=thin)
    # no example row: it would be counted on the Weekly count tab
    stop = dict(allow_blank=True, showErrorMessage=True, errorTitle="Pick from the list", error="Choose one of the values in the dropdown.")
    dv_sec = DataValidation(type="list", formula1='"' + ",".join(SECTIONS) + '"', **stop)
    dv_why = DataValidation(type="list", formula1='"C,M,T"', **stop)
    dv_fix = DataValidation(type="list", formula1='"No,Yes"', **stop)
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


# ---------- more templates ----------
from openpyxl.chart import LineChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation as _DV


def _head(ws, row, labels, fill=TEAL):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=t)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(wrap_text=True, vertical="center")


def final_grade():
    wb = Workbook()
    ws = wb.active
    ws.title = "Final grade"
    ws["A1"] = "What do I need on my final?"
    ws["A1"].font = Font(bold=True, size=15, color=INK)
    ws["A2"] = "Fill in the yellow cells. Leave a score blank if it is not graded yet. Check your syllabus for drops, scaling or rounding."
    ws["A2"].font = Font(color="5B6B7F", size=10)
    _head(ws, 4, ["Category", "Weight (% of course)", "Your score (%)"])
    cats = [("Homework", 0.20, 0.88), ("Quizzes", 0.15, 0.81), ("Midterm", 0.25, 0.76), ("Project", 0.10, None), ("", None, None), ("", None, None)]
    yellow = PatternFill("solid", fgColor="FFF6D6")
    for i, (n, w, sc) in enumerate(cats, 5):
        ws[f"A{i}"] = n or None
        ws[f"B{i}"] = w
        ws[f"C{i}"] = sc
        for col in "ABC":
            ws[f"{col}{i}"].fill = yellow
        ws[f"B{i}"].number_format = "0%"
        ws[f"C{i}"].number_format = "0.0%"
    ws["A12"] = "Weight of the final exam"
    ws["B12"] = 0.30
    ws["A13"] = "Grade you want overall"
    ws["B13"] = 0.85
    for r in (12, 13):
        ws[f"B{r}"].fill = yellow
        ws[f"B{r}"].number_format = "0%"
    ws["A15"] = "Your grade before the final"
    ws["B15"] = '=IFERROR(SUMPRODUCT(B5:B10,C5:C10)/SUMIF(C5:C10,"<>",B5:B10),"")'
    ws["B15"].number_format = "0.0%"
    ws["A16"] = "Score needed on the final"
    ws["B16"] = '=IF(OR(NOT(ISNUMBER(B15)),NOT(ISNUMBER(B12)),NOT(ISNUMBER(B13)),B12<=0),"",MAX(0,(B13-B15*(1-B12))/B12))'  # never a negative score
    ws["B16"].number_format = "0.0%"
    ws["A17"] = "What that means"
    ws["B17"] = '=IF(B16="","Fill in the cells above",IF(B16>1,"Out of reach unless there is extra credit: try a lower target",IF(B16<=0,"You already have it: any score keeps this grade","Aim for "&TEXT(B16,"0.0%")&" or more")))'
    for r in (15, 16):
        ws[f"A{r}"].font = Font(bold=True)
        ws[f"B{r}"].font = Font(bold=True, size=12, color=TEAL)
    ws["A17"].font = Font(bold=True)
    ws["A19"] = "Formula: needed = (target - current x (1 - weight of final)) / weight of final. FocusFlow Lab, free for personal use. thefocusflowlab.com/tools/final-grade-calculator/"
    ws["A19"].font = Font(color="5B6B7F", size=9)
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 56
    ws.column_dimensions["C"].width = 18
    wb.save(OUT / "final-grade-template.xlsx")


def score_log():
    wb = Workbook()
    ws = wb.active
    ws.title = "Practice scores"
    _head(ws, 1, ["Date", "Source", "Topic or section", "Right", "Total", "% right", "Target %", "At target?"])
    for col, w in zip("ABCDEFGH", [13, 22, 26, 9, 9, 10, 10, 12]):
        ws.column_dimensions[col].width = w
    from datetime import date
    rows = 200
    for r in range(2, rows + 2):
        ws[f"F{r}"] = f'=IF(OR(NOT(ISNUMBER(D{r})),NOT(ISNUMBER(E{r})),E{r}<=0),"",IF(D{r}>E{r},"Right > total?",D{r}/E{r}))'
        ws[f"H{r}"] = f'=IF(OR(NOT(ISNUMBER(F{r})),G{r}=""),"",IF(F{r}>=G{r},"Yes","Not yet"))'
        ws[f"G{r}"] = 0.75
        ws[f"F{r}"].number_format = "0%"
        ws[f"G{r}"].number_format = "0%"
        ws[f"A{r}"].number_format = "yyyy-mm-dd"
    # no example rows: they would feed Overall and the chart
    ws.freeze_panes = "A2"
    ws["J1"], ws["K1"] = "Overall", '=IFERROR(SUMPRODUCT(ISNUMBER(D2:D201)*ISNUMBER(E2:E201)*(E2:E201>0)*(D2:D201<=E2:E201),D2:D201)/SUMPRODUCT(ISNUMBER(D2:D201)*ISNUMBER(E2:E201)*(E2:E201>0)*(D2:D201<=E2:E201),E2:E201),"")'
    ws["K1"].number_format = "0%"
    ws["J1"].font = Font(bold=True)
    ws["K1"].font = Font(bold=True, color=TEAL, size=12)
    ch = LineChart()
    ch.title = "% right over time"
    ch.height, ch.width = 7.5, 16
    ch.add_data(Reference(ws, min_col=6, min_row=1, max_row=40), titles_from_data=True)
    ch.y_axis.number_format = "0%"
    ch.y_axis.scaling.min, ch.y_axis.scaling.max = 0, 1
    ws.add_chart(ch, "J3")
    ws["J20"] = "FocusFlow Lab, free for personal use. thefocusflowlab.com/tools/practice-score-tracker/"
    ws["J20"].font = Font(color="5B6B7F", size=9)
    wb.save(OUT / "practice-score-log.xlsx")


def study_schedule():
    wb = Workbook()
    ws = wb.active
    ws.title = "Week"
    sj = wb.create_sheet("Subjects")
    sj["A1"] = "Your subjects (edit this list)"
    sj["A1"].font = Font(bold=True, color=INK)
    for i, n in enumerate(["Biology", "Chemistry", "Maths", "Reading", "Review", "Break"], 2):
        sj[f"A{i}"] = n
    sj.column_dimensions["A"].width = 26
    sj["C1"], sj["D1"] = "Subject", "Hours this week"
    sj["C1"].font = sj["D1"].font = Font(bold=True, color=INK)
    for i in range(2, 12):
        sj[f"C{i}"] = f'=IF(A{i}="","",A{i})'
        sj[f"D{i}"] = f"=IF(A{i}=\"\",\"\",COUNTIF(Week!B3:H19,A{i}))"
    sj.column_dimensions["C"].width = 22
    sj.column_dimensions["D"].width = 16
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ws["A1"] = "Weekly study schedule: pick a subject for each hour"
    ws["A1"].font = Font(bold=True, size=14, color=INK)
    _head(ws, 2, ["Hour"] + days)
    for i, h in enumerate(range(6, 23), 3):
        ws[f"A{i}"] = f"{h}:00"
        ws[f"A{i}"].font = Font(bold=True, color="5B6B7F")
    dv = _DV(type="list", formula1="=Subjects!$A$2:$A$11", allow_blank=True, showErrorMessage=True, errorStyle="warning", errorTitle="Not on your subject list", error="Add it on the Subjects tab first, or keep it anyway.")
    ws.add_data_validation(dv)
    dv.add("B3:H19")
    thin = Side(style="thin", color="B9C8CD")
    for r in range(3, 20):
        for col in "BCDEFGH":
            ws[f"{col}{r}"].border = Border(bottom=thin, right=thin)
    ws.column_dimensions["A"].width = 8
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 14
    ws["A21"] = "Hours per subject are counted on the Subjects tab. Plan breaks as carefully as study. Leave about one block free for catch-up. FocusFlow Lab, free for personal use."
    ws["A21"].font = Font(color="5B6B7F", size=9)
    ws.freeze_panes = "B3"
    wb.save(OUT / "study-schedule-template.xlsx")


final_grade()
score_log()
study_schedule()
print("wrote", sorted(p.name for p in OUT.iterdir()))
