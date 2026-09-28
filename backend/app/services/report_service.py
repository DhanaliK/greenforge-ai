"""
Report generation service for GreenForge AI.
Produces JSON reports and PDF exports.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def generate_pdf_report(report_data: Dict, report_id: int) -> Optional[str]:
    """Generate a PDF report using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        pdf_path = str(REPORTS_DIR / f"greenforge_report_{report_id}.pdf")

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()
        story = []

        # Custom styles
        title_style = ParagraphStyle(
            'GreenTitle',
            parent=styles['Title'],
            fontSize=22,
            textColor=colors.HexColor('#166534'),
            spaceAfter=6,
        )
        h1_style = ParagraphStyle(
            'GreenH1',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#15803d'),
            spaceAfter=4,
            spaceBefore=12,
        )
        h2_style = ParagraphStyle(
            'GreenH2',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#166534'),
            spaceAfter=3,
        )
        normal_style = styles['Normal']
        small_style = ParagraphStyle(
            'Small',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
        )

        # Header
        story.append(Paragraph("🌿 GreenForge AI", title_style))
        story.append(Paragraph("Sustainability Analysis Report", styles['Heading2']))
        story.append(Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            small_style
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#86efac')))
        story.append(Spacer(1, 0.3*cm))

        # Executive Summary
        story.append(Paragraph("Executive Summary", h1_style))
        summary = report_data.get("executive_summary", "No summary available.")
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 0.3*cm))

        # GreenForge Score
        score = report_data.get("greenforge_score", {})
        if score:
            story.append(Paragraph("GreenForge Score", h1_style))
            score_data = [
                ["Dimension", "Score"],
                ["Overall Score", f"{score.get('total', 0):.1f} / 100"],
                ["Algorithmic Efficiency", f"{score.get('algorithmic_efficiency', 0):.1f}"],
                ["Runtime Efficiency", f"{score.get('runtime_efficiency', 0):.1f}"],
                ["Memory Efficiency", f"{score.get('memory_efficiency', 0):.1f}"],
                ["I/O Efficiency", f"{score.get('io_efficiency', 0):.1f}"],
                ["ML Efficiency", f"{score.get('ml_efficiency', 0):.1f}"],
                ["Optimization Potential", f"{score.get('optimization_potential', 0):.1f}"],
            ]
            t = Table(score_data, colWidths=[10*cm, 5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0fdf4'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbf7d0')),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3*cm))

        # Code Findings
        code_findings = report_data.get("code_findings", {})
        findings_list = code_findings.get("findings", [])
        if findings_list:
            story.append(Paragraph("Code Analysis Findings", h1_style))
            severity_summary = code_findings.get("by_severity", {})
            summary_text = (
                f"Total: {code_findings.get('total', 0)} issues detected — "
                f"Critical: {severity_summary.get('Critical', 0)}, "
                f"High: {severity_summary.get('High', 0)}, "
                f"Medium: {severity_summary.get('Medium', 0)}, "
                f"Low: {severity_summary.get('Low', 0)}"
            )
            story.append(Paragraph(summary_text, normal_style))
            story.append(Spacer(1, 0.2*cm))

            for finding in findings_list[:10]:  # Limit to 10 in PDF
                sev = finding.get("severity", "Low")
                sev_colors = {
                    "Critical": "#dc2626", "High": "#ea580c",
                    "Medium": "#ca8a04", "Low": "#2563eb", "Informational": "#6b7280"
                }
                color = sev_colors.get(sev, "#6b7280")
                sev_style = ParagraphStyle(
                    f'Sev_{sev}',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor(color),
                    fontName='Helvetica-Bold',
                )
                story.append(Paragraph(f"[{sev}] {finding.get('title', '')}", sev_style))
                story.append(Paragraph(finding.get('explanation', ''), normal_style))
                story.append(Paragraph(
                    f"Recommendation: {finding.get('recommendation', '')}",
                    small_style
                ))
                story.append(Spacer(1, 0.15*cm))

        # Benchmark Results
        benchmark = report_data.get("benchmark", {})
        before = benchmark.get("before", {})
        after = benchmark.get("after", {})
        if before.get("mean_runtime"):
            story.append(Paragraph("Benchmark Results", h1_style))
            bench_data = [
                ["Metric", "Before Optimization", "After Optimization"],
                ["Mean Runtime (s)",
                 f"{before.get('mean_runtime', 0):.4f}",
                 f"{after.get('mean_runtime', 0):.4f}" if after.get("mean_runtime") else "—"],
                ["Peak Memory (MB)",
                 f"{before.get('peak_memory_mb', 0):.1f}",
                 f"{after.get('peak_memory_mb', 0):.1f}" if after.get("peak_memory_mb") else "—"],
            ]
            comp = benchmark.get("comparison", {})
            if comp.get("runtime_reduction_pct") is not None:
                bench_data.append([
                    "Runtime Improvement",
                    "—",
                    f"{comp['runtime_reduction_pct']:.1f}%"
                ])
            t = Table(bench_data, colWidths=[6*cm, 5*cm, 5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#eff6ff'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3*cm))

        # Sustainability
        sus = report_data.get("sustainability", {})
        if sus.get("estimated_energy_wh") is not None:
            story.append(Paragraph("Sustainability Estimates", h1_style))
            story.append(Paragraph(
                f"Estimated Energy: {sus['estimated_energy_wh']:.8f} Wh (modeled)",
                normal_style
            ))
            story.append(Paragraph(
                f"Estimated Carbon: {sus.get('estimated_carbon_gco2e', 0):.8f} gCO2e (modeled)",
                normal_style
            ))
            story.append(Paragraph(sus.get("methodology_note", ""), small_style))
            story.append(Spacer(1, 0.3*cm))

        # Responsible AI Note
        story.append(Paragraph("Responsible AI Statement", h1_style))
        story.append(Paragraph(
            report_data.get("responsible_ai_note", ""),
            small_style
        ))
        story.append(Spacer(1, 0.2*cm))

        # SDG Alignment
        sdg = report_data.get("sdg_alignment", {})
        if sdg:
            story.append(Paragraph("SDG Alignment", h1_style))
            story.append(Paragraph(f"Primary: {sdg.get('primary', '')}", normal_style))
            for s in sdg.get("secondary", []):
                story.append(Paragraph(f"Secondary: {s}", normal_style))

        # Footer
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#86efac')))
        story.append(Paragraph(
            "Generated by GreenForge AI — Agentic AI for Sustainable Software &amp; Machine Learning",
            small_style
        ))

        doc.build(story)
        return pdf_path

    except ImportError as e:
        logger.warning(f"ReportLab not available: {e}")
        return None
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return None
