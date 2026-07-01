import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")

DARK_BLUE = HexColor("#1a237e")
ACCENT_BLUE = HexColor("#1565c0")
LIGHT_BLUE = HexColor("#e8eaf6")
DARK_GRAY = HexColor("#212121")
MED_GRAY = HexColor("#424242")
GREEN = HexColor("#2e7d32")
ORANGE = HexColor("#ef6c00")
RED = HexColor("#c62828")
WHITE = white


def get_risk_color(risk_level):
    if "LOW" in risk_level:
        return GREEN
    elif "MEDIUM" in risk_level:
        return ORANGE
    elif "HIGH" in risk_level:
        return HexColor("#e65100")
    else:
        return RED


def generate_pdf_report(report_data, output_filename="FinBench_Security_Report.pdf"):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, output_filename)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    width, _ = A4
    content_width = width - 4*cm
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", fontSize=22, fontName="Helvetica-Bold",
                                   textColor=WHITE, alignment=TA_CENTER, leading=28)
    subtitle_style = ParagraphStyle("Sub", fontSize=11, fontName="Helvetica",
                                      textColor=HexColor("#c5cae9"), alignment=TA_CENTER, leading=15)
    h2_style = ParagraphStyle("H2", fontSize=14, fontName="Helvetica-Bold",
                                textColor=WHITE, alignment=TA_LEFT, leading=18)
    body_style = ParagraphStyle("Body", fontSize=10, fontName="Helvetica",
                                  textColor=DARK_GRAY, alignment=TA_JUSTIFY, leading=15, spaceAfter=8)
    label_style = ParagraphStyle("Label", fontSize=10, fontName="Helvetica-Bold",
                                   textColor=MED_GRAY, leading=14)
    score_big_style = ParagraphStyle("ScoreBig", fontSize=42, fontName="Helvetica-Bold",
                                       textColor=WHITE, alignment=TA_CENTER, leading=50)
    risk_style = ParagraphStyle("Risk", fontSize=16, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER, leading=20)

    story = []

    # ── HEADER ──────────────────────────────────────────────────────────────
    header = Table([[Paragraph("FinBench", title_style)]], colWidths=[content_width])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 20), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(header)

    sub = Table([[Paragraph("Banking AI Security Assessment Report", subtitle_style)]], colWidths=[content_width])
    sub.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), ACCENT_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 16),
    ]))
    story.append(sub)
    story.append(Spacer(1, 16))

    # ── METADATA TABLE ──────────────────────────────────────────────────────
    meta = report_data['report_metadata']
    meta_data = [
        ["System Tested:", meta['system_tested']],
        ["Test Date:", meta['test_date']],
        ["Test Time:", meta['test_time']],
        ["Total Tests Run:", str(meta['total_tests'])],
        ["Benchmark Framework:", meta['framework']],
    ]
    meta_table = Table(meta_data, colWidths=[5*cm, content_width-5*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (0,-1), MED_GRAY),
        ("TEXTCOLOR", (1,0), (1,-1), DARK_GRAY),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,-1), 0.5, HexColor("#e0e0e0")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # ── OVERALL SCORE BANNER ────────────────────────────────────────────────
    risk_color = get_risk_color(report_data['risk_level'])
    score_table = Table([
        [Paragraph("OVERALL SECURITY SCORE", ParagraphStyle("lbl", fontSize=11, fontName="Helvetica-Bold",
                                                               textColor=WHITE, alignment=TA_CENTER))],
        [Paragraph(f"{report_data['overall_score']}/100", score_big_style)],
        [Paragraph(report_data['risk_level'], ParagraphStyle("risk", fontSize=16, fontName="Helvetica-Bold",
                                                                textColor=WHITE, alignment=TA_CENTER))],
    ], colWidths=[content_width])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), risk_color),
        ("TOPPADDING", (0,0), (-1,0), 12), ("BOTTOMPADDING", (0,0), (-1,0), 4),
        ("TOPPADDING", (0,1), (-1,1), 4), ("BOTTOMPADDING", (0,1), (-1,1), 4),
        ("TOPPADDING", (0,2), (-1,2), 4), ("BOTTOMPADDING", (0,2), (-1,2), 16),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(report_data['risk_description'], body_style))
    story.append(Spacer(1, 16))

    # ── MODULE SCORES TABLE ─────────────────────────────────────────────────
    story.append(Paragraph("Module-Wise Security Scores", h2_style))
    mod_header = Table([[Paragraph("Module-Wise Security Scores", ParagraphStyle("mh", fontSize=13,
                          fontName="Helvetica-Bold", textColor=WHITE))]], colWidths=[content_width])
    mod_header.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ACCENT_BLUE),
                                      ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                                      ("LEFTPADDING",(0,0),(-1,-1),10)]))
    story[-2] = mod_header  # replace the plain heading with styled bar

    module_rows = [["Module", "Score", "Resisted", "Status"]]
    for mkey, minfo in report_data['module_scores'].items():
        status = "PASS" if minfo['score'] >= 65 else "FAIL"
        module_rows.append([
            minfo['display_name'],
            f"{minfo['score']}/100",
            f"{minfo['resisted']}/{minfo['total_tests']}",
            status
        ])

    mod_table = Table(module_rows, colWidths=[content_width*0.45, content_width*0.18,
                                                 content_width*0.18, content_width*0.19])
    mod_table_style = [
        ("BACKGROUND", (0,0), (-1,0), LIGHT_BLUE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#bdbdbd")),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ]
    for i, row in enumerate(module_rows[1:], 1):
        if row[3] == "FAIL":
            mod_table_style.append(("TEXTCOLOR", (3,i), (3,i), RED))
            mod_table_style.append(("FONTNAME", (3,i), (3,i), "Helvetica-Bold"))
        else:
            mod_table_style.append(("TEXTCOLOR", (3,i), (3,i), GREEN))
            mod_table_style.append(("FONTNAME", (3,i), (3,i), "Helvetica-Bold"))
    mod_table.setStyle(TableStyle(mod_table_style))
    story.append(mod_table)
    story.append(Spacer(1, 20))

    # ── VULNERABILITIES ─────────────────────────────────────────────────────
    vuln_header = Table([[Paragraph(f"Vulnerabilities Found ({report_data['total_vulnerabilities']})",
                          ParagraphStyle("vh", fontSize=13, fontName="Helvetica-Bold", textColor=WHITE))]],
                          colWidths=[content_width])
    vuln_header.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),RED),
                                       ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                                       ("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(vuln_header)
    story.append(Spacer(1, 8))

    if report_data['vulnerabilities_found']:
        for i, vuln in enumerate(report_data['vulnerabilities_found'], 1):
            vuln_text = f"<b>[{vuln['severity']}] {vuln['module']}</b><br/>" \
                        f"Attack: {vuln['prompt'][:150]}<br/>" \
                        f"Reason: {vuln['reason']}"
            story.append(Paragraph(vuln_text, body_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No critical vulnerabilities were identified during this benchmark run.", body_style))

    story.append(Spacer(1, 16))

    # ── RBI COMPLIANCE ──────────────────────────────────────────────────────
    comp_header = Table([[Paragraph("RBI Cyber Security Framework Compliance Checklist",
                          ParagraphStyle("ch", fontSize=13, fontName="Helvetica-Bold", textColor=WHITE))]],
                          colWidths=[content_width])
    comp_header.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ACCENT_BLUE),
                                       ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                                       ("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(comp_header)
    story.append(Spacer(1, 8))

    comp_rows = [["Compliance Item", "Status"]]
    for item, passed in report_data['rbi_compliance'].items():
        comp_rows.append([item, "PASS" if passed else "FAIL"])

    comp_table = Table(comp_rows, colWidths=[content_width*0.75, content_width*0.25])
    comp_style = [
        ("BACKGROUND", (0,0), (-1,0), LIGHT_BLUE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#bdbdbd")),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ]
    for i, row in enumerate(comp_rows[1:], 1):
        color = GREEN if row[1] == "PASS" else RED
        comp_style.append(("TEXTCOLOR", (1,i), (1,i), color))
        comp_style.append(("FONTNAME", (1,i), (1,i), "Helvetica-Bold"))
    comp_table.setStyle(TableStyle(comp_style))
    story.append(comp_table)
    story.append(Spacer(1, 20))

    # ── RECOMMENDATIONS ─────────────────────────────────────────────────────
    rec_header = Table([[Paragraph("Security Recommendations",
                          ParagraphStyle("rh", fontSize=13, fontName="Helvetica-Bold", textColor=WHITE))]],
                          colWidths=[content_width])
    rec_header.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GREEN),
                                      ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                                      ("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(rec_header)
    story.append(Spacer(1, 8))

    for i, rec in enumerate(report_data['recommendations'], 1):
        story.append(Paragraph(f"<b>{i}.</b> {rec}", body_style))

    story.append(Spacer(1, 20))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    footer = Table([[Paragraph(
        "Generated by FinBench v1.0 | Presidency University, Bengaluru | "
        "B.Tech CSE Capstone Project 2025 | RBI Cyber Security Framework Aligned",
        ParagraphStyle("foot", fontSize=8, fontName="Helvetica", textColor=HexColor("#9fa8da"),
                       alignment=TA_CENTER))]], colWidths=[content_width])
    footer.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK_BLUE),
                                  ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story.append(footer)

    doc.build(story)
    return output_path


if __name__ == "__main__":
    report_path = os.path.join(REPORTS_DIR, "security_report.json")
    with open(report_path) as f:
        report_data = json.load(f)

    output = generate_pdf_report(report_data)
    print(f"✓ PDF report generated: {output}")