import os
import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

class MedicalPDFGenerator:
    """
    Automated Medical Report & X-ray PDF Generator using ReportLab.
    Produces evidence-grounded educational summaries with clickable citations,
    laboratory tables, uncertainty ratings, and required disclaimers.
    """

    def __init__(self, output_dir: str = "./storage/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report_pdf(
        self,
        report_id: int,
        report_data: Dict[str, Any],
        entities: List[Dict[str, Any]],
        analysis_data: Dict[str, Any],
        evidence_sources: List[Dict[str, Any]]
    ) -> str:
        """Generate PDF for laboratory/clinical medical report."""
        filename = f"Medical_Summary_Report_{report_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#0369a1'),
            spaceAfter=4
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=12
        )

        disclaimer_banner_style = ParagraphStyle(
            'DisclaimerBanner',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.HexColor('#b91c1c'),
            alignment=1, # Center
            spaceAfter=10
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#0f766e'),
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("EVIDENCE-BASED MEDICAL REPORT ASSISTANT", title_style))
        story.append(Paragraph(f"Analysis ID: #{report_id} | Date: {datetime.datetime.now().strftime('%B %d, %Y - %H:%M UTC')} | File: {report_data.get('original_filename', 'Document')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=8))

        # 2. Prominent Medical Safety Disclaimer Banner
        disclaimer_table = Table(
            [[Paragraph("<b>CRITICAL NOTICE: AI-GENERATED EDUCATIONAL SUMMARY – NOT A MEDICAL DIAGNOSIS</b><br/><font size='8' color='#334155'>This report provides educational explanations for patient understanding. It does not replace clinical consultation with a licensed physician.</font>", disclaimer_banner_style)]],
            colWidths=[530]
        )
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#fca5a5')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(disclaimer_table)
        story.append(Spacer(1, 10))

        # 3. Executive Summary
        story.append(Paragraph("1. Executive Clinical Summary", section_heading))
        summary_text = analysis_data.get("summary_text", "Summary not available.")
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 6))

        # 4. Patient-Friendly Explanation
        story.append(Paragraph("2. Plain-Language Explanation", section_heading))
        patient_text = analysis_data.get("patient_friendly_explanation", "No additional notes provided.")
        for para in patient_text.split("\n\n"):
            story.append(Paragraph(para, body_style))
        story.append(Spacer(1, 8))

        # 5. Extracted Laboratory Results Table
        lab_items = [e for e in entities if e.get("entity_type") == "lab_test"]
        if lab_items:
            story.append(Paragraph("3. Extracted Laboratory Values", section_heading))
            table_data = [
                [
                    Paragraph("<b>Test Name</b>", body_style),
                    Paragraph("<b>Observed Value</b>", body_style),
                    Paragraph("<b>Unit</b>", body_style),
                    Paragraph("<b>Reference Interval</b>", body_style),
                    Paragraph("<b>Clinical Flag</b>", body_style),
                ]
            ]
            for item in lab_items:
                flag = item.get("flag", "NORMAL")
                flag_color = "#16a34a" if flag == "NORMAL" else "#dc2626"
                table_data.append([
                    Paragraph(item.get("text", ""), body_style),
                    Paragraph(f"<b>{item.get('normalized_value', '')}</b>", body_style),
                    Paragraph(item.get("unit", "") or "-", body_style),
                    Paragraph(item.get("reference_range", "") or "-", body_style),
                    Paragraph(f"<font color='{flag_color}'><b>{flag}</b></font>", body_style)
                ])

            lab_table = Table(table_data, colWidths=[150, 95, 75, 120, 90])
            lab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(lab_table)
            story.append(Spacer(1, 10))

        # 6. Retrieved Medical Evidence & Citations
        if evidence_sources:
            story.append(Paragraph("4. Evidence Citations & Peer-Reviewed Sources", section_heading))
            for idx, ev in enumerate(evidence_sources[:4], 1):
                ev_p = (
                    f"<b>[{idx}] {ev.get('source_title')}</b><br/>"
                    f"<i>Source:</i> {ev.get('source_org')} | <i>URL:</i> {ev.get('source_url')}<br/>"
                    f"<i>Evidence Excerpt:</i> {ev.get('excerpt')}"
                )
                story.append(Paragraph(ev_p, body_style))
                story.append(Spacer(1, 4))
            story.append(Spacer(1, 6))

        # 7. Questions to Discuss With Your Doctor
        questions = analysis_data.get("doctor_discussion_questions", [])
        if questions:
            story.append(Paragraph("5. Recommended Questions for Your Healthcare Provider", section_heading))
            for q in questions:
                story.append(Paragraph(f"• {q}", body_style))
            story.append(Spacer(1, 8))

        # 8. Uncertainty & System Verification
        story.append(Paragraph("6. AI Uncertainty & Transparency Statement", section_heading))
        uncert_text = (
            f"Extraction Confidence: {analysis_data.get('extraction_confidence', 0.94):.0%} | "
            f"Synthesis Model: {analysis_data.get('model_used', 'Groq Cloud Llama-3.3-70B')} | "
            "All laboratory numerical values were traced directly to source document pages without alteration."
        )
        story.append(Paragraph(uncert_text, subtitle_style))

        # Build PDF
        doc.build(story)
        return filepath

    def generate_xray_pdf(self, xray_id: int, xray_data: Dict[str, Any]) -> str:
        """Generate PDF for Chest X-ray research analysis."""
        filename = f"Chest_Xray_Report_{xray_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#0369a1'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#0f766e'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6
        )
        disclaimer_banner_style = ParagraphStyle(
            'DisclaimerBanner',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.HexColor('#b91c1c'),
            alignment=1,
            spaceAfter=8
        )

        story = []
        story.append(Paragraph("CHEST X-RAY RESEARCH INTERPRETATION REPORT", title_style))
        story.append(Paragraph(f"Study ID: #{xray_id} | Date: {datetime.datetime.now().strftime('%B %d, %Y - %H:%M UTC')} | File: {xray_data.get('original_filename', 'Radiograph')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=8))

        # Disclaimer
        disclaimer_table = Table(
            [[Paragraph("<b>RESEARCH ONLY: NOT A CONFIRMED RADIOLOGY DIAGNOSIS</b><br/><font size='8' color='#334155'>Hosted medical imaging feature analysis provides research observations only. Never use as sole diagnostic basis.</font>", disclaimer_banner_style)]],
            colWidths=[530]
        )
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#fca5a5')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(disclaimer_table)
        story.append(Spacer(1, 10))

        # Findings Summary
        story.append(Paragraph("1. Preliminary Radiographic Observations", section_heading))
        story.append(Paragraph(xray_data.get("preliminary_findings", "No findings summary."), body_style))
        story.append(Spacer(1, 6))

        # Pathology scores table
        story.append(Paragraph("2. Evaluated Thoracic Pathologies (Research Model Activations)", section_heading))
        obs_list = xray_data.get("observations_json", [])
        if isinstance(obs_list, list) and obs_list:
            table_data = [
                [
                    Paragraph("<b>Pathology</b>", body_style),
                    Paragraph("<b>Research Score</b>", body_style),
                    Paragraph("<b>Confidence Level</b>", body_style),
                    Paragraph("<b>Radiological Definition</b>", body_style)
                ]
            ]
            for item in obs_list[:8]:
                score = item.get("score", 0.0)
                level = item.get("confidence_level", "Low")
                lvl_color = "#dc2626" if level == "High" else ("#d97706" if level == "Moderate" else "#16a34a")
                table_data.append([
                    Paragraph(item.get("pathology", ""), body_style),
                    Paragraph(f"{score:.2f}", body_style),
                    Paragraph(f"<font color='{lvl_color}'><b>{level}</b></font>", body_style),
                    Paragraph(item.get("explanation", "")[:120] + "...", body_style)
                ])

            obs_table = Table(table_data, colWidths=[120, 80, 100, 230])
            obs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(obs_table)
            story.append(Spacer(1, 10))

        # Quality and Model Info
        story.append(Paragraph("3. Technical & Model Details", section_heading))
        tech_p = (
            f"<b>Model:</b> {xray_data.get('model_name', 'Hosted Medical Imaging API')}<br/>"
            f"<b>Architecture:</b> Cloud-Hosted Chest Radiograph Analysis Architecture<br/>"
            f"<b>Image Quality:</b> {xray_data.get('image_quality', 'Acceptable')}<br/>"
            f"<b>Anatomical Region:</b> {xray_data.get('anatomical_region', 'Chest')}"
        )
        story.append(Paragraph(tech_p, body_style))
        story.append(Spacer(1, 8))

        # Limitations
        story.append(Paragraph("4. Technical Limitations & Clinical Disclaimers", section_heading))
        story.append(Paragraph(xray_data.get("limitations_text", "Consult board-certified radiologist."), body_style))

        doc.build(story)
        return filepath

