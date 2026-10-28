"""
PDF report generation — builds a health summary PDF from a user's records,
profile, and computed insights. Uses reportlab (pure-Python, no system deps).
"""

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

_PRIMARY = colors.HexColor("#0ea5e9")
_DARK = colors.HexColor("#0f172a")
_MUTED = colors.HexColor("#64748b")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="LLTitle",
            fontSize=22,
            leading=26,
            textColor=_DARK,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="LLSub",
            fontSize=10,
            leading=13,
            textColor=_MUTED,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LLH2",
            fontSize=13,
            leading=16,
            textColor=_PRIMARY,
            spaceBefore=14,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(ParagraphStyle(name="LLBody", fontSize=10, leading=14, textColor=_DARK))
    return styles


def _kv_table(rows: list[tuple[str, str]]):
    data = [[k, v or "—"] for k, v in rows]
    t = Table(data, colWidths=[55 * mm, 110 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), _MUTED),
                ("TEXTCOLOR", (1, 0), (1, -1), _DARK),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ]
        )
    )
    return t


def build_health_report(
    *,
    user: dict,
    profile: dict | None,
    insights: dict,
    documents: list[dict],
) -> bytes:
    """Render a health summary PDF and return it as bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="LIFELINK Health Report",
    )
    s = _styles()
    story: list = []

    # Header
    story.append(Paragraph("LIFELINK Health Report", s["LLTitle"]))
    generated = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    story.append(Paragraph(f"Generated {generated}", s["LLSub"]))

    # Patient
    story.append(Paragraph("Patient Information", s["LLH2"]))
    p = profile or {}
    story.append(
        _kv_table(
            [
                ("Name", user.get("full_name", "")),
                ("Email", user.get("email", "")),
                ("Date of Birth", str(p.get("date_of_birth") or "")),
                ("Gender", p.get("gender") or ""),
                ("Blood Group", p.get("blood_group") or ""),
                ("Height / Weight", _ht_wt(p)),
                ("Allergies", _join(p.get("allergies"))),
                ("Chronic Conditions", _join(p.get("chronic_conditions"))),
                ("Emergency Contact", _emergency(p)),
            ]
        )
    )

    # Health summary
    story.append(Paragraph("Health Summary", s["LLH2"]))
    score = insights.get("health_score")
    score_txt = f"{score}/100" if score is not None else "Not enough data"
    story.append(
        _kv_table(
            [
                ("Health Score", score_txt),
                ("Total Documents", str(insights.get("total_documents", 0))),
                ("Processed Documents", str(insights.get("processed_documents", 0))),
            ]
        )
    )

    for label, key in [
        ("Conditions", "conditions"),
        ("Active Medications", "medications"),
        ("Abnormal Lab Values", "abnormal_labs"),
    ]:
        vals = insights.get(key) or []
        if vals:
            story.append(Spacer(1, 4))
            story.append(
                Paragraph(
                    f"<b>{label}:</b> " + ", ".join(str(v) for v in vals), s["LLBody"]
                )
            )

    for line in insights.get("insights") or []:
        story.append(Paragraph("• " + str(line), s["LLBody"]))

    # Records
    story.append(Paragraph("Medical Records", s["LLH2"]))
    if documents:
        header = ["Date", "Type", "Summary"]
        rows = [header]
        for d in documents:
            rows.append(
                [
                    str(d.get("document_date") or d.get("uploaded_at") or "")[:10],
                    str(d.get("doc_type") or ""),
                    str(d.get("summary_short") or "")[:70],
                ]
            )
        t = Table(rows, colWidths=[25 * mm, 35 * mm, 105 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f1f5f9")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(t)
    else:
        story.append(Paragraph("No medical records on file.", s["LLBody"]))

    # Disclaimer
    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            "<i>This report is auto-generated by LIFELINK from your uploaded records and is "
            "not a medical diagnosis. Always consult a qualified healthcare professional.</i>",
            s["LLSub"],
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf.read()


def _join(v) -> str:
    if not v:
        return ""
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v)
    return str(v)


def _ht_wt(p: dict) -> str:
    h, w = p.get("height_cm"), p.get("weight_kg")
    parts = []
    if h:
        parts.append(f"{h} cm")
    if w:
        parts.append(f"{w} kg")
    return " / ".join(parts)


def _emergency(p: dict) -> str:
    name, phone = p.get("emergency_contact_name"), p.get("emergency_contact_phone")
    if name and phone:
        return f"{name} ({phone})"
    return name or phone or ""
