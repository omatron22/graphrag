# assessment_pdf_generator.py
"""
PDF Generator for Strategy Assessment outputs.
Creates structured PDF reports with assessment results and visualizations.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import time

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssessmentPDFGenerator:
    """
    Generates PDF reports for strategy assessment results.
    """
    
    def __init__(self, output_dir=None):
        """Initialize PDF generator."""
        # Set output directory
        self.output_dir = output_dir or os.path.join("data", "outputs", "pdfs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize PDF library
        self._init_pdf_library()
        
        logger.info("Assessment PDF Generator initialized")
    
    def _init_pdf_library(self):
        """Initialize PDF generation library."""
        # Try to import ReportLab
        try:
            # First check if we can import the base reportlab package
            try:
                import reportlab
                logger.info(f"Found reportlab version: {reportlab.__version__}")
                logger.info(f"Reportlab path: {reportlab.__file__}")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Error importing reportlab base package: {e}")
        
            # Now try importing specific reportlab modules
            try:
                from reportlab.lib.pagesizes import letter, A4
                logger.info("Successfully imported reportlab.lib.pagesizes")
            
                from reportlab.lib import colors
                logger.info("Successfully imported reportlab.lib.colors")
            
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                logger.info("Successfully imported reportlab.lib.styles")
            
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
                logger.info("Successfully imported reportlab.platypus")
            
                from reportlab.graphics.charts.piecharts import Pie
                logger.info("Successfully imported reportlab.graphics.charts.piecharts")
            
                from reportlab.graphics.charts.barcharts import VerticalBarChart
                logger.info("Successfully imported reportlab.graphics.charts.barcharts")
            
                from reportlab.graphics.charts.linecharts import HorizontalLineChart
                logger.info("Successfully imported reportlab.graphics.charts.linecharts")
            
                from reportlab.graphics.shapes import Drawing
                logger.info("Successfully imported reportlab.graphics.shapes")
            
                # Continue with initialization if all imports succeed
                self.pdf_lib = {
                    "pagesizes": {"letter": letter, "A4": A4},
                    "colors": colors,
                    "styles": getSampleStyleSheet(),
                    "SimpleDocTemplate": SimpleDocTemplate,
                    "Paragraph": Paragraph,
                    "Spacer": Spacer,
                    "Table": Table,
                    "TableStyle": TableStyle,
                    "Image": Image,
                    "charts": {
                        "Pie": Pie,
                        "VerticalBarChart": VerticalBarChart,
                        "HorizontalLineChart": HorizontalLineChart
                    },
                    "Drawing": Drawing
                }
            
                # Add custom styles
                self.pdf_lib["styles"].add(ParagraphStyle(
                    name='Heading1Center',
                    parent=self.pdf_lib["styles"]['Heading1'],
                    alignment=1  # Center alignment
                ))
            
                self.pdf_lib["styles"].add(ParagraphStyle(
                    name='Normal-Bold',
                    parent=self.pdf_lib["styles"]['Normal'],
                    fontName='Helvetica-Bold'
                ))
            
                # Log Python environment information
                import sys
                logger.info(f"Python executable: {sys.executable}")
                logger.info(f"Python version: {sys.version}")
            
                logger.info("ReportLab PDF library initialized")
                self.pdf_engine = "reportlab"
            
            except ImportError as e:
                logger.warning(f"Specific ReportLab module import error: {e}")
                self.pdf_engine = "fallback"
        
        except Exception as e:
            logger.warning(f"Unexpected error initializing ReportLab: {e}")
            self.pdf_engine = "fallback"
    
    def generate_assessment_pdf(self, assessment_results: Dict[str, Any], charts: Dict[str, Dict[str, Any]]) -> str:
        """
        Generate a PDF report for strategy assessment results.
        
        Args:
            assessment_results: Assessment results
            charts: Chart configurations for visualization
            
        Returns:
            str: Path to the generated PDF
        """
        entity_name = assessment_results.get("entity", "Unknown Entity")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategy_assessment_{entity_name.replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        if self.pdf_engine == "reportlab":
            return self._generate_with_reportlab(assessment_results, charts, filepath)
        else:
            return self._generate_with_fallback(assessment_results, charts, filepath)
    
    def _generate_with_reportlab(self, assessment_results: Dict[str, Any], charts: Dict[str, Dict[str, Any]], filepath: str) -> str:
        """
        Generate PDF with ReportLab.
    
        Args:
            assessment_results: Assessment results
            charts: Chart configurations for visualization
            filepath: Path to save the PDF
        
        Returns:
            str: Path to the generated PDF
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.linecharts import LineChart
        from reportlab.graphics.charts.spider import SpiderChart
    
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = self.pdf_lib["styles"]
        elements = []
    
        # Add title and cover page
        entity_name = assessment_results.get("entity", "Unknown Entity")
        title = f"Strategy Assessment Report: {entity_name}"
        elements.append(Paragraph(title, styles["Heading1Center"]))
        elements.append(Spacer(1, 24))
    
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
        elements.append(Spacer(1, 36))
    
        # Add explanation of the report structure
        elements.append(Paragraph("About This Report", styles["Heading3"]))
        elements.append(Paragraph(
            "This report is divided into two main sections:", 
            styles["Normal"]
        ))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "1. <b>Current Situation Analysis</b>: An assessment of the company's current state, risks, and opportunities.", 
            styles["Normal"]
        ))
        elements.append(Paragraph(
            "2. <b>Strategic Recommendations</b>: Tailored strategies based on the analysis and your specified risk tolerance.", 
            styles["Normal"]
        ))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            "All scores range from 0% to 100%, where higher scores indicate better performance. Risk levels (Low/Medium/High) indicate areas of concern.",
            styles["Normal"]
        ))
    
        elements.append(PageBreak())
    
        # SECTION 1: CURRENT SITUATION ANALYSIS
        elements.append(Paragraph("SECTION 1: CURRENT SITUATION ANALYSIS", styles["Heading1"]))
        elements.append(Spacer(1, 12))
    
        # Add executive summary
        elements.append(Paragraph("Executive Summary", styles["Heading2"]))
        elements.append(Spacer(1, 6))
    
        summary = assessment_results.get("summary", {})
        overall_score = summary.get("overall_score", 0.5)
        risk_level = summary.get("risk_level", "Medium")
    
        # Format score as percentage
        score_percent = f"{overall_score * 100:.1f}%"
    
        # Add current state explanation
        elements.append(Paragraph(
            f"Based on our analysis, {entity_name} currently has an overall performance score of {score_percent} with " +
            f"an overall risk level assessed as {risk_level}. The score represents the company's current health " +
            f"across all measured business dimensions, where higher percentages indicate better performance.",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 12))
    
        # Add summary table with better explanation
        summary_data = [
            ["Overall Performance Score", "Current Risk Level"],
            [score_percent, risk_level]
        ]
    
        summary_table = Table(summary_data, colWidths=[250, 250])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), 
            colors.lightgreen if overall_score > 0.7 else 
            colors.lightyellow if overall_score > 0.4 else colors.lightcoral),
            ('BACKGROUND', (1, 1), (1, 1), 
            colors.lightgreen if risk_level == "Low" else 
            colors.lightyellow if risk_level == "Medium" else colors.lightcoral),
            ('ALIGN', (0, 1), (1, 1), 'CENTER'),
            ('FONTNAME', (0, 1), (1, 1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, 1), 1, colors.black)
        ]))
    
        elements.append(summary_table)
        elements.append(Spacer(1, 12))
    
        # Add color legend
        elements.append(Paragraph("Score & Risk Level Color Legend:", styles["Normal-Bold"]))
        elements.append(Spacer(1, 6))
    
        legend_data = [
            ["", "Low Risk/Good Performance", "Medium Risk/Average Performance", "High Risk/Poor Performance"],
            ["Color", "", "", ""]
        ]
    
        legend_table = Table(legend_data, colWidths=[80, 150, 150, 150])
        legend_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 1), (1, 1), colors.lightgreen),
            ('BACKGROUND', (2, 1), (2, 1), colors.lightyellow),
            ('BACKGROUND', (3, 1), (3, 1), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
    
        elements.append(legend_table)
        elements.append(Spacer(1, 18))
    
        # Add key insights
        elements.append(Paragraph("Key Insights from Current Analysis", styles["Heading3"]))
        elements.append(Spacer(1, 6))
    
        insights = summary.get("key_insights", [])
        for insight in insights:
            elements.append(Paragraph(f"• {insight}", styles["Normal"]))
            elements.append(Spacer(1, 3))
    
        elements.append(Spacer(1, 18))
    
        # Add risk breakdown section
        elements.append(Paragraph("Risk Assessment Breakdown", styles["Heading3"]))
        elements.append(Spacer(1, 6))

        # Extract risk data
        risk_data = {}
        if isinstance(assessment_results, dict) and "groups" in assessment_results:
            risk_group = assessment_results["groups"].get("risk", {})
            if isinstance(risk_group, dict):
                risk_data = risk_group.get("findings", {})

        if risk_data and (isinstance(risk_data, dict) or (isinstance(risk_data, list) and risk_data)):
            # Check if it's a list of detailed risk entries or just key-value pairs
            if isinstance(risk_data, list):
                # Detailed risk data in list format
                risk_table_data = [["Risk Type", "Description", "Impact Area", "Level", "Probability", "Status"]]
        
                for risk in risk_data:
                    if isinstance(risk, dict):
                        risk_level = risk.get('level', 0)
                        if isinstance(risk_level, (int, float)):
                            risk_level_str = f"{float(risk_level) * 100:.0f}%"
                        else:
                            risk_level_str = str(risk_level)
                
                        risk_table_data.append([
                            risk.get("risk_type", "Unknown").capitalize(),
                            risk.get("description", ""),
                            risk.get("impact_area", ""),
                            risk_level_str,
                            risk.get("probability", ""),
                            risk.get("mitigation_status", "")
                        ])
            else:
                # Simple risk categories in dict format
                risk_table_data = [["Risk Category", "Current Risk Level"]]
        
                for risk_type, level in risk_data.items():
                    if risk_type != "reasoning":
                        risk_table_data.append([risk_type.capitalize(), level])
    
            # Calculate appropriate column widths
            if len(risk_table_data[0]) == 2:  # Simple format
                colWidths = [250, 250]
            else:  # Detailed format
                colWidths = None  # Auto-size columns
    
            risk_table = Table(risk_table_data, colWidths=colWidths)
            risk_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, len(risk_table_data)-1), 1, colors.black)
            ]

            # Add color coding for risk levels if using the simple format
            if len(risk_table_data[0]) == 2:  # Simple format with just category and level
                for i in range(1, len(risk_table_data)):
                    level = risk_table_data[i][1]
                    if level == "Low":
                        risk_styles.append(('BACKGROUND', (1, i), (1, i), colors.lightgreen))
                    elif level == "Medium":
                        risk_styles.append(('BACKGROUND', (1, i), (1, i), colors.lightyellow))
                    elif level == "High":
                        risk_styles.append(('BACKGROUND', (1, i), (1, i), colors.lightcoral))

            risk_table.setStyle(TableStyle(risk_styles))
            elements.append(risk_table)
        else:
            elements.append(Paragraph("No detailed risk data available.", styles["Normal"]))
    
        elements.append(Spacer(1, 18))
    
        # Add visualization charts
        elements.append(Paragraph("Performance Analysis Charts", styles["Heading3"]))
        elements.append(Spacer(1, 6))
    
        # Add Risk Levels chart
        if "risk_levels" in charts:
            elements.append(Paragraph("Risk Levels by Assessment Area", styles["Normal-Bold"]))
            elements.append(Spacer(1, 6))
        
            # Create pie chart
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 125
            pie.height = 125
            pie.data = [item["value"] for item in charts["risk_levels"]["data"]]
            pie.labels = [item["label"] for item in charts["risk_levels"]["data"]]
            pie.slices.strokeWidth = 1
        
            # Set colors based on risk levels
            risk_colors = {
                "High": colors.lightcoral,
                "Medium": colors.lightyellow,
                "Low": colors.lightgreen
            }
        
            for i, label in enumerate(pie.labels):
                if label in risk_colors:
                    pie.slices[i].fillColor = risk_colors[label]
        
            drawing.add(pie)
            elements.append(drawing)
            elements.append(Spacer(1, 18))
    
        # Add Group Scores chart
        if "group_scores" in charts:
            elements.append(Paragraph("Assessment Area Performance Scores", styles["Normal-Bold"]))
            elements.append(Spacer(1, 6))
        
            # Create bar chart
            data = charts["group_scores"]["data"]
            drawing = Drawing(500, 250)
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 175
            bc.width = 400
            bc.data = [[item["value"] for item in data]]
            bc.categoryAxis.categoryNames = [item["label"] for item in data]
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = 1
            bc.valueAxis.valueStep = 0.2
            bc.bars[0].fillColor = colors.steelblue
        
            # Rotate labels for better fit
            bc.categoryAxis.labels.boxAnchor = 'ne'
            bc.categoryAxis.labels.dx = 8
            bc.categoryAxis.labels.dy = -2
            bc.categoryAxis.labels.angle = 30
        
            drawing.add(bc)
            elements.append(drawing)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Higher scores (closer to 1.0) indicate better performance in each area.", styles["Normal"]))
            elements.append(Spacer(1, 18))
    
        # Add financial impact chart if available
        if "financial_impact" in charts and isinstance(charts["financial_impact"], dict):
            elements.append(Paragraph("Financial Performance Metrics", styles["Normal-Bold"]))
        
            # Create financial chart based on available data
            # Implementation would depend on the specific data structure
            # This is just a placeholder
            elements.append(Paragraph("Financial metrics visualization would appear here.", styles["Normal"]))
            elements.append(Spacer(1, 18))
    
        # Add page break before recommendations
        elements.append(PageBreak())
    
        # SECTION 2: STRATEGIC RECOMMENDATIONS
        elements.append(Paragraph("SECTION 2: STRATEGIC RECOMMENDATIONS", styles["Heading1"]))
        elements.append(Spacer(1, 12))
    
        # Add explanation of recommendations
        user_inputs = assessment_results.get("user_inputs", {})
        risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
        priorities = user_inputs.get("priorities", [])
    
        elements.append(Paragraph("Strategy Development Approach", styles["Heading3"]))
        elements.append(Spacer(1, 6))
    
        elements.append(Paragraph(
            f"The following strategic recommendations have been tailored to {entity_name}'s current situation " +
            f"with a <b>{risk_tolerance} risk tolerance</b> approach. " +
            (f"Priority areas include: <b>{', '.join(priorities)}</b>." if priorities else ""),
            styles["Normal"]
        ))
        elements.append(Spacer(1, 6))
    
        elements.append(Paragraph(
            f"<b>{risk_tolerance} risk tolerance</b> means: " +
            ("Taking aggressive approaches that prioritize growth opportunities over safety." if risk_tolerance == "High" else
             "Balancing risk mitigation with growth opportunities." if risk_tolerance == "Medium" else
             "Prioritizing stability and risk mitigation over aggressive growth."),
            styles["Normal"]
        ))
        elements.append(Spacer(1, 18))
    
        # Add recommendations
        elements.append(Paragraph("Strategic Recommendations", styles["Heading2"]))
        elements.append(Spacer(1, 12))
    
        recommendations = assessment_results.get("recommendations", [])
        for i, rec in enumerate(recommendations):
            # Recommendation header
            elements.append(Paragraph(f"{i+1}. {rec.get('title')}", styles["Heading3"]))
            elements.append(Spacer(1, 3))
        
            # Priority and timeline
            priority = rec.get('priority', 'medium').capitalize()
            timeline = rec.get('timeline', 'medium').capitalize()
            priority_color = (colors.lightcoral if priority == "High" else 
                            colors.lightyellow if priority == "Medium" else colors.lightgreen)
        
            elements.append(Paragraph(
                f"Priority: <font color='{priority_color}'>{priority}</font> | Timeline: {timeline}", 
                styles["Normal"])
            )
            elements.append(Spacer(1, 6))
        
            # Rationale with better formatting
            elements.append(Paragraph("Rationale:", styles["Normal-Bold"]))
            elements.append(Paragraph(rec.get('rationale', ''), styles["Normal"]))
            elements.append(Spacer(1, 6))
        
            # Benefits
            elements.append(Paragraph("Expected Benefits:", styles["Normal-Bold"]))
            for benefit in rec.get('benefits', []):
                elements.append(Paragraph(f"• {benefit}", styles["Normal"]))
            elements.append(Spacer(1, 6))
        
            # Implementation steps
            elements.append(Paragraph("Implementation Steps:", styles["Normal-Bold"]))
            for step in rec.get('implementation_steps', []):
                elements.append(Paragraph(f"• {step}", styles["Normal"]))
            elements.append(Spacer(1, 6))
        
            # KPIs
            elements.append(Paragraph("Success Metrics (KPIs):", styles["Normal-Bold"]))
            for kpi in rec.get('kpis', []):
                elements.append(Paragraph(f"• {kpi}", styles["Normal"]))
        
            # Space between recommendations
            elements.append(Spacer(1, 24))
    
        # Add strategy priority chart if available
        if "strategy_priorities" in charts:
            elements.append(Paragraph("Strategy Priority Distribution", styles["Heading3"]))
            elements.append(Spacer(1, 6))
        
            # Create the strategy priority chart
            priority_data = charts["strategy_priorities"]["data"]
            drawing = Drawing(400, 200)
            bc = VerticalBarChart()
            bc.x = 100
            bc.y = 50
            bc.height = 125
            bc.width = 200
            bc.data = [[item["value"] for item in priority_data]]
            bc.categoryAxis.categoryNames = [item["label"] for item in priority_data]
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max([item["value"] for item in priority_data]) + 1
            bc.valueAxis.valueStep = 1
        
            # Color bars by priority
            colorMap = {
                'High Priority': colors.lightcoral,
                'Medium Priority': colors.lightyellow,
                'Low Priority': colors.lightgreen
            }
        
            for i, label in enumerate([item["label"] for item in priority_data]):
                if label in colorMap:
                    bc.bars[0][i].fillColor = colorMap[label]
        
            drawing.add(bc)
            elements.append(drawing)
            elements.append(Spacer(1, 18))
    
        # Add appendix with detailed assessments
        elements.append(PageBreak())
        elements.append(Paragraph("APPENDIX: DETAILED ASSESSMENT DATA", styles["Heading1"]))
        elements.append(Spacer(1, 12))
    
        # Add details for each assessment group
        for group_id, group_data in assessment_results.get("groups", {}).items():
            # Group header
            elements.append(Paragraph(group_data.get("name", group_id.capitalize()), styles["Heading3"]))
            elements.append(Spacer(1, 3))
        
            # Group description
            elements.append(Paragraph(group_data.get("description", ""), styles["Normal"]))
            elements.append(Spacer(1, 6))
        
            # Group score and risk level
            score = group_data.get("score", 0.5)
            risk_level = group_data.get("risk_level", "Medium")
            score_percent = f"{score * 100:.1f}%"
        
            score_table = Table([["Score", "Risk Level"], [score_percent, risk_level]], colWidths=[250, 250])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (0, 1), 
                colors.lightgreen if score > 0.7 else 
                colors.lightyellow if score > 0.4 else colors.lightcoral),
                ('BACKGROUND', (1, 1), (1, 1), 
                colors.lightgreen if risk_level == "Low" else 
                colors.lightyellow if risk_level == "Medium" else colors.lightcoral),
                ('ALIGN', (0, 1), (1, 1), 'CENTER'),
                ('FONTNAME', (0, 1), (1, 1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (1, 1), 1, colors.black)
            ]))
        
            elements.append(score_table)
            elements.append(Spacer(1, 12))
        
            # Key findings
            findings = group_data.get("findings", [])
            if findings:
                elements.append(Paragraph("Key Findings:", styles["Normal-Bold"]))
                for finding in findings:
                    if isinstance(finding, dict):
                        # Handle dictionary-type finding
                        finding_type = finding.get("type", "other").capitalize()
                        description = finding.get("description", "")
                        elements.append(Paragraph(f"• {finding_type}: {description}", styles["Normal"]))
                    elif isinstance(finding, str):
                        # Handle string-type finding
                        elements.append(Paragraph(f"• {finding}", styles["Normal"]))
                    else:
                        # Handle other types (unlikely, but for safety)
                        elements.append(Paragraph(f"• {str(finding)}", styles["Normal"]))
            
            # Add metrics if available
            metrics = group_data.get("metrics", {})
            if metrics:
                elements.append(Paragraph("Metrics:", styles["Normal-Bold"]))
            
                # Create metrics table
                metrics_data = [["Metric", "Value", "Trend"]]
                for metric_name, metric_data in metrics.items():
                    value = metric_data.get("value", "N/A")
                    unit = metric_data.get("unit", "")
                    if unit:
                        value = f"{value} {unit}"
                
                    trend = metric_data.get("trend", "stable")
                    metrics_data.append([metric_name, value, trend])
            
                # Create and style the table
                metrics_table = Table(metrics_data, colWidths=[200, 150, 150])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
                    ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (2, 0), 12),
                    ('GRID', (0, 0), (2, len(metrics_data)-1), 1, colors.black)
                ]))
            
                elements.append(metrics_table)
                elements.append(Spacer(1, 12))
        
            # Add space between groups
            elements.append(Spacer(1, 24))
    
        # Build PDF
        doc.build(elements)
        logger.info(f"Generated assessment PDF: {filepath}")
    
        return filepath
    
    def _generate_with_fallback(self, assessment_results: Dict[str, Any], charts: Dict[str, Dict[str, Any]], filepath: str) -> str:
        """
        Generate PDF with fallback method (JSON export).
        
        Args:
            assessment_results: Assessment results
            charts: Chart configurations for visualization
            filepath: Path to save the PDF
            
        Returns:
            str: Path to the generated PDF
        """
        # Since we can't generate a proper PDF, save assessment results as JSON
        json_path = filepath.replace(".pdf", ".json")
        
        # Combine assessment results and charts
        export_data = {
            "assessment_results": assessment_results,
            "charts": charts,
            "export_note": "PDF generation not available. Data exported as JSON instead."
        }
        
        # Save to file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.warning(f"PDF generation not available. Exported data as JSON: {json_path}")
        
        return json_path