"""
Generate 5 realistic sample medical report PDFs for testing LIFELINK's
upload → OCR → AI extraction → timeline → risk pipeline.

Run inside the backend container (reportlab is installed):
    python scripts/make_test_reports.py
Outputs to /app/scripts/test_reports/ (copy out with `docker cp`).
"""

import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUT = os.path.join(os.path.dirname(__file__), "test_reports")
os.makedirs(OUT, exist_ok=True)

styles = getSampleStyleSheet()
H = ParagraphStyle("H", parent=styles["Heading1"], fontSize=16, spaceAfter=4)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
BODY = styles["Normal"]
B = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, leading=15)


def _doc(fname):
    return SimpleDocTemplate(
        os.path.join(OUT, fname),
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )


def _lab_table(rows):
    data = [["Test", "Result", "Unit", "Reference", "Flag"]] + rows
    t = Table(data, colWidths=[55 * mm, 25 * mm, 22 * mm, 40 * mm, 20 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f4f7fb")],
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return t


# ─── 1. Blood Test Lab Report (diabetes + anemia signals) ───
def report_1():
    d = _doc("1_lab_report_cbc_diabetes.pdf")
    e = [
        Paragraph("Apollo Diagnostics", H),
        Paragraph("NABL Accredited Laboratory · Madurai, Tamil Nadu", SUB),
        Spacer(1, 10),
        Paragraph("<b>LABORATORY REPORT</b>", B),
        Paragraph(
            "Patient: Saransh Rajput &nbsp;&nbsp; Age/Sex: 28/M &nbsp;&nbsp; "
            "Date: 12 Oct 2026 &nbsp;&nbsp; Ref. Dr: Dr. R. Menon",
            B,
        ),
        Spacer(1, 8),
        Paragraph("<b>Complete Blood Count & Glucose Panel</b>", B),
        Spacer(1, 4),
        _lab_table(
            [
                ["Hemoglobin", "10.8", "g/dL", "13.0 - 17.0", "LOW"],
                ["Fasting Blood Sugar", "142", "mg/dL", "70 - 100", "HIGH"],
                ["HbA1c", "7.4", "%", "4.0 - 5.6", "HIGH"],
                ["Total WBC", "7200", "/cmm", "4000 - 11000", "NORMAL"],
                ["Platelet Count", "2.4", "lakh/cmm", "1.5 - 4.1", "NORMAL"],
                ["Serum Cholesterol", "228", "mg/dL", "< 200", "HIGH"],
            ]
        ),
        Spacer(1, 10),
        Paragraph(
            "<b>Impression:</b> Mild anemia with impaired glucose control "
            "(pre-diabetic / early diabetic range). Elevated cholesterol noted. "
            "Clinical correlation and dietary modification advised.",
            B,
        ),
        Spacer(1, 6),
        Paragraph("Verified by: Dr. R. Menon, MD (Pathology)", SUB),
    ]
    d.build(e)


# ─── 2. Prescription ───
def report_2():
    d = _doc("2_prescription.pdf")
    e = [
        Paragraph("Dr. Anita Sharma, MBBS, MD (Medicine)", H),
        Paragraph("City Care Clinic · Reg. No. TN/2011/4521", SUB),
        Spacer(1, 10),
        Paragraph(
            "Patient: Saransh Rajput &nbsp;&nbsp; Age: 28 &nbsp;&nbsp; "
            "Date: 15 Oct 2026",
            B,
        ),
        Spacer(1, 6),
        Paragraph(
            "<b>Diagnosis:</b> Type 2 Diabetes Mellitus, Iron-deficiency anemia", B
        ),
        Spacer(1, 8),
        Paragraph("<b>Rx</b>", B),
        _lab_table(
            [
                ["Metformin 500mg", "1-0-1", "tablet", "After meals x 30 days", ""],
                [
                    "Ferrous Sulfate 200mg",
                    "1-0-0",
                    "tablet",
                    "After breakfast x 30 days",
                    "",
                ],
                ["Atorvastatin 10mg", "0-0-1", "tablet", "At night x 30 days", ""],
                ["Vitamin B12", "1-0-0", "tablet", "Weekly x 8 weeks", ""],
            ]
        ),
        Spacer(1, 10),
        Paragraph(
            "<b>Advice:</b> Low-sugar diet, 30 min brisk walk daily, "
            "repeat HbA1c after 3 months. Follow up in 4 weeks.",
            B,
        ),
        Spacer(1, 6),
        Paragraph("Signature: Dr. Anita Sharma", SUB),
    ]
    d.build(e)


# ─── 3. Discharge Summary ───
def report_3():
    d = _doc("3_discharge_summary.pdf")
    e = [
        Paragraph("Fortis Hospital — Discharge Summary", H),
        Paragraph("Department of Cardiology", SUB),
        Spacer(1, 10),
        Paragraph(
            "Patient: Saransh Rajput &nbsp;&nbsp; Age/Sex: 28/M &nbsp;&nbsp; "
            "MRN: FH-220934",
            B,
        ),
        Paragraph("Admitted: 02 Sep 2026 &nbsp;&nbsp; Discharged: 05 Sep 2026", B),
        Spacer(1, 8),
        Paragraph(
            "<b>Admission Diagnosis:</b> Acute gastroenteritis with dehydration", B
        ),
        Paragraph(
            "<b>Procedures:</b> IV fluid resuscitation, electrolyte correction", B
        ),
        Spacer(1, 6),
        Paragraph(
            "<b>Hospital Course:</b> Patient presented with 2-day history of vomiting "
            "and loose stools. Managed with IV fluids, antiemetics, and probiotics. "
            "Vitals stabilised by day 2. Tolerated oral feeds by day 3.",
            B,
        ),
        Spacer(1, 6),
        Paragraph(
            "<b>Discharge Medications:</b> ORS sachets, Ondansetron 4mg SOS, "
            "Pantoprazole 40mg OD x 5 days.",
            B,
        ),
        Spacer(1, 6),
        Paragraph(
            "<b>Follow-up:</b> Review in OPD after 1 week if symptoms persist.", B
        ),
        Spacer(1, 6),
        Paragraph("Consultant: Dr. Vikram Rao, DM (Cardiology)", SUB),
    ]
    d.build(e)


# ─── 4. Kidney Function Test (CKD signals) ───
def report_4():
    d = _doc("4_kidney_function_test.pdf")
    e = [
        Paragraph("SRL Diagnostics", H),
        Paragraph("Renal Function Panel", SUB),
        Spacer(1, 10),
        Paragraph(
            "Patient: Saransh Rajput &nbsp;&nbsp; Age/Sex: 28/M &nbsp;&nbsp; "
            "Date: 20 Oct 2026",
            B,
        ),
        Spacer(1, 8),
        _lab_table(
            [
                ["Serum Creatinine", "2.1", "mg/dL", "0.7 - 1.3", "HIGH"],
                ["Blood Urea", "68", "mg/dL", "15 - 40", "HIGH"],
                ["eGFR", "41", "mL/min", "> 90", "LOW"],
                ["Serum Sodium", "138", "mEq/L", "135 - 145", "NORMAL"],
                ["Serum Potassium", "5.3", "mEq/L", "3.5 - 5.1", "HIGH"],
                ["Uric Acid", "7.8", "mg/dL", "3.5 - 7.2", "HIGH"],
            ]
        ),
        Spacer(1, 10),
        Paragraph(
            "<b>Impression:</b> Reduced eGFR with elevated creatinine and urea "
            "suggestive of Stage 3 Chronic Kidney Disease. Nephrology referral advised. "
            "Monitor potassium closely.",
            B,
        ),
        Spacer(1, 6),
        Paragraph("Verified by: Dr. S. Iyer, MD", SUB),
    ]
    d.build(e)


# ─── 5. Thyroid + Lipid Profile ───
def report_5():
    d = _doc("5_thyroid_lipid_profile.pdf")
    e = [
        Paragraph("Metropolis Healthcare", H),
        Paragraph("Thyroid & Lipid Profile", SUB),
        Spacer(1, 10),
        Paragraph(
            "Patient: Saransh Rajput &nbsp;&nbsp; Age/Sex: 28/M &nbsp;&nbsp; "
            "Date: 25 Oct 2026",
            B,
        ),
        Spacer(1, 8),
        Paragraph("<b>Thyroid Function</b>", B),
        _lab_table(
            [
                ["TSH", "6.8", "uIU/mL", "0.4 - 4.0", "HIGH"],
                ["Free T4", "0.9", "ng/dL", "0.8 - 1.8", "NORMAL"],
                ["Free T3", "2.6", "pg/mL", "2.3 - 4.2", "NORMAL"],
            ]
        ),
        Spacer(1, 8),
        Paragraph("<b>Lipid Profile</b>", B),
        _lab_table(
            [
                ["Total Cholesterol", "242", "mg/dL", "< 200", "HIGH"],
                ["LDL Cholesterol", "165", "mg/dL", "< 100", "HIGH"],
                ["HDL Cholesterol", "38", "mg/dL", "> 40", "LOW"],
                ["Triglycerides", "198", "mg/dL", "< 150", "HIGH"],
            ]
        ),
        Spacer(1, 10),
        Paragraph(
            "<b>Impression:</b> Subclinical hypothyroidism with dyslipidemia. "
            "Recommend thyroid medication review and statin therapy. "
            "Repeat TSH after 6 weeks.",
            B,
        ),
        Spacer(1, 6),
        Paragraph("Verified by: Dr. P. Nair, MD", SUB),
    ]
    d.build(e)


if __name__ == "__main__":
    report_1()
    report_2()
    report_3()
    report_4()
    report_5()
    print("Generated 5 reports in:", OUT)
    for f in sorted(os.listdir(OUT)):
        print("  -", f)
