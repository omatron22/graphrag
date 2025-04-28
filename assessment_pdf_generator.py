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
        Generate PDF with ReportLab with enhanced visualization and styling.

        Args:
            assessment_results: Assessment results
            charts: Chart configurations for visualization
            filepath: Path to save the PDF
    
        Returns:
            str: Path to the generated PDF
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib import colors
        from reportlab.graphics.shapes import Drawing, Rect
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.linecharts import LineChart
        from reportlab.graphics.charts.spider import SpiderChart
        from reportlab.lib.colors import PCMYKColor, Color

        # Define custom colors for a professional look
        corporate_blue = PCMYKColor(100, 60, 0, 50)  # Deep blue
        corporate_blue_light = PCMYKColor(100, 30, 0, 20)  # Lighter blue
        corporate_green = PCMYKColor(100, 0, 100, 30)  # Rich green
        corporate_green_light = PCMYKColor(50, 0, 80, 10)  # Light green
        corporate_red = PCMYKColor(0, 100, 100, 30)  # Rich red
        corporate_red_light = PCMYKColor(0, 60, 60, 10)  # Light red
        corporate_yellow = PCMYKColor(0, 30, 100, 10)  # Warm yellow
        corporate_gray = PCMYKColor(0, 0, 0, 50)  # Medium gray
        corporate_light_gray = PCMYKColor(0, 0, 0, 20)  # Light gray

        # Create PDF document with custom settings
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=letter,
            leftMargin=36, 
            rightMargin=36, 
            topMargin=36, 
            bottomMargin=36
        )
    
        # Enhanced styles
        styles = getSampleStyleSheet()
    
        # Add custom styles
        styles.add(ParagraphStyle(
            name='Cover_Title',
            parent=styles['Heading1'],
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=corporate_blue,
            spaceAfter=20
        ))
    
        styles.add(ParagraphStyle(
            name='Cover_Subtitle',
            parent=styles['Heading2'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=corporate_gray,
            spaceAfter=30
        ))
    
        styles.add(ParagraphStyle(
            name='Section_Title',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=corporate_blue,
            spaceAfter=12
        ))
    
        styles.add(ParagraphStyle(
            name='Subsection_Title',
            parent=styles['Heading2'],
            fontSize=16,
            leading=20,
            textColor=corporate_blue_light,
            spaceAfter=8
        ))
    
        styles.add(ParagraphStyle(
            name='Normal_Bold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold'
        ))
    
        styles.add(ParagraphStyle(
            name='Caption',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            textColor=corporate_gray
        ))
    
        styles.add(ParagraphStyle(
            name='Summary_Item',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            leftIndent=20,
            bulletIndent=12,
            spaceBefore=2,
            spaceAfter=5
        ))
    
        elements = []

        # Get entity name
        entity_name = assessment_results.get("entity", "Unknown Entity")
    
        # ADD COVER PAGE
        elements.append(Paragraph(f"Strategy Assessment Report", styles["Cover_Title"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"{entity_name}", styles["Cover_Subtitle"]))
        elements.append(Spacer(1, 30))
    
        # Add date and confidential marking
        timestamp = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Prepared: {timestamp}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("CONFIDENTIAL", styles["Normal_Bold"]))
        elements.append(Spacer(1, 36))
    
        # Add executive summary section to cover
        summary = assessment_results.get("summary", {})
        overall_score = summary.get("overall_score", 0.5)
        risk_level = summary.get("risk_level", "Medium")
    
        # Format score as percentage
        score_percent = f"{overall_score * 100:.1f}%"
    
        # Executive summary blurb
        summary_text = f"""This assessment report provides a comprehensive analysis of {entity_name}'s current strategic position, 
        with an overall performance score of {score_percent} and risk level assessed as {risk_level}. 
        The report outlines key findings across multiple business dimensions and provides tailored 
        strategic recommendations prioritized based on impact and urgency."""
    
        elements.append(Paragraph("Executive Overview", styles["Subsection_Title"]))
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 24))
    
        # Performance score bar - visual representation of score
        elements.append(Paragraph("Overall Performance", styles["Normal_Bold"]))
        elements.append(Spacer(1, 6))
    
        # Create custom score gauge
        def create_score_gauge(score, width=400, height=50):
            drawing = Drawing(width, height)
        
            # Background bar
            drawing.add(Rect(0, 15, width, 20, fillColor=corporate_light_gray, strokeColor=None))
        
            # Score bar
            score_width = min(width * score, width)
            if score >= 0.7:
                fill_color = corporate_green
            elif score >= 0.4:
                fill_color = corporate_yellow
            else:
                fill_color = corporate_red
            
            drawing.add(Rect(0, 15, score_width, 20, fillColor=fill_color, strokeColor=None))
        
            # Add labels
            drawing.add(Paragraph("0%", styles["Caption"]))
            drawing.add(Paragraph("100%", styles["Caption"]))
            drawing.add(Paragraph(f"{score*100:.1f}%", styles["Caption"]))
        
            return drawing
    
        elements.append(create_score_gauge(overall_score))
        elements.append(Spacer(1, 24))
    
        # Add key insights to cover
        key_insights = summary.get("key_insights", [])
        if key_insights:
            elements.append(Paragraph("Key Insights", styles["Subsection_Title"]))
            for insight in key_insights[:3]:  # Top 3 insights only on cover
                elements.append(Paragraph(f"• {insight}", styles["Normal"]))
    
        # Add page break after cover
        elements.append(PageBreak())
    
        # TABLE OF CONTENTS
        elements.append(Paragraph("Table of Contents", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        toc_data = [
            ["Section", "Page"],
            ["1. Current Situation Analysis", "3"],
            ["2. Risk Assessment", "5"],
            ["3. Strategic Recommendations", "7"],
            ["4. Implementation Roadmap", "10"],
            ["5. Performance Metrics", "12"],
            ["Appendix: Detailed Assessment Data", "14"]
        ]
    
        toc_table = Table(toc_data, colWidths=[350, 100])
        toc_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('LINEBELOW', (0, 0), (-1, 0), 1, corporate_blue),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, corporate_light_gray),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
    
        elements.append(toc_table)
        elements.append(Spacer(1, 24))
    
        # Add report introduction
        elements.append(Paragraph("About This Report", styles["Subsection_Title"]))
        elements.append(Paragraph(
            """This report provides a data-driven assessment of the current strategic position and recommendations 
            for future growth. The analysis is based on our knowledge graph technology that integrates data from 
            multiple sources to identify patterns, risks, and opportunities.""",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 12))
    
        elements.append(Paragraph("Methodology", styles["Normal_Bold"]))
        elements.append(Paragraph(
            """Our analysis framework evaluates 11 key business dimensions and identifies strategic 
            priorities based on your specified risk tolerance level. Each assessment area receives a 
            score from 0-100% and a risk classification.""",
            styles["Normal"]
        ))
    
        # Add page break before main content
        elements.append(PageBreak())
    
        # SECTION 1: CURRENT SITUATION ANALYSIS
        elements.append(Paragraph("SECTION 1: CURRENT SITUATION ANALYSIS", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        elements.append(Paragraph("Current Strategic Position", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        # Main summary information with enhanced styling
        summary_data = [
            ["Overall Performance Score", "Current Risk Level"],
            [score_percent, risk_level]
        ]
    
        summary_table = Table(summary_data, colWidths=[250, 250])
    
        # Determine colors based on scores
        performance_color = corporate_green_light if overall_score > 0.7 else corporate_yellow if overall_score > 0.4 else corporate_red_light
        risk_color = corporate_green_light if risk_level == "Low" else corporate_yellow if risk_level == "Medium" else corporate_red_light
    
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), corporate_blue_light),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), performance_color),
            ('BACKGROUND', (1, 1), (1, 1), risk_color),
            ('ALIGN', (0, 1), (1, 1), 'CENTER'),
            ('FONTNAME', (0, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (1, 1), 14),
            ('GRID', (0, 0), (1, 1), 1, corporate_blue)
        ]))
    
        elements.append(summary_table)
        elements.append(Spacer(1, 18))
    
        # Color legend with improved styling
        elements.append(Paragraph("Performance & Risk Level Legend:", styles["Normal_Bold"]))
        elements.append(Spacer(1, 6))
    
        legend_data = [
            ["", "Low Risk / Good", "Medium Risk / Average", "High Risk / Poor"],
            ["Color", "", "", ""]
        ]
    
        legend_table = Table(legend_data, colWidths=[80, 150, 150, 150])
        legend_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 1), (1, 1), corporate_green_light),
            ('BACKGROUND', (2, 1), (2, 1), corporate_yellow),
            ('BACKGROUND', (3, 1), (3, 1), corporate_red_light),
            ('GRID', (0, 0), (-1, -1), 1, corporate_gray),
        ]))
    
        elements.append(legend_table)
        elements.append(Spacer(1, 18))
    
        # Key insights section with better formatting
        elements.append(Paragraph("Key Insights from Current Analysis", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        insights = summary.get("key_insights", [])
        for insight in insights:
            elements.append(Paragraph(f"• {insight}", styles["Summary_Item"]))
    
        elements.append(Spacer(1, 18))
    
        # Performance Analysis Charts section
        elements.append(Paragraph("Performance Analysis Charts", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        # Add Risk Levels chart (improved pie chart)
        if "risk_levels" in charts:
            elements.append(Paragraph("Risk Level Distribution", styles["Normal_Bold"]))
            elements.append(Spacer(1, 6))
        
            pie_data = charts["risk_levels"]["data"]
        
            # Create enhanced pie chart
            drawing = Drawing(450, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 25
            pie.width = 150
            pie.height = 150
            pie.data = [item["value"] for item in pie_data]
            pie.labels = [item["label"] for item in pie_data]
            pie.slices.strokeWidth = 1
            pie.slices.strokeColor = colors.white
        
            # Custom colors based on risk levels
            risk_colors = {
                "High": corporate_red_light,
                "Medium": corporate_yellow,
                "Low": corporate_green_light
            }
        
            for i, label in enumerate(pie.labels):
                if label.split(':')[0] in risk_colors:
                    pie.slices[i].fillColor = risk_colors[label.split(':')[0]]
        
            # Add a legend
            from reportlab.graphics.charts.legends import Legend
            legend = Legend()
            legend.alignment = 'right'
            legend.x = 330
            legend.y = 85
            legend.columnMaximum = 8
            legend.colorNamePairs = [(risk_colors[label.split(':')[0]], label) for label in pie.labels if label.split(':')[0] in risk_colors]
        
            drawing.add(pie)
            drawing.add(legend)
            elements.append(drawing)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Figure 1: Distribution of risk levels across assessment areas", styles["Caption"]))
            elements.append(Spacer(1, 18))
    
        # Add Assessment Area Performance Scores (enhanced bar chart)
        if "group_scores" in charts:
            elements.append(Paragraph("Assessment Area Performance Scores", styles["Normal_Bold"]))
            elements.append(Spacer(1, 6))
        
            data = charts["group_scores"]["data"]
        
            # Create enhanced bar chart
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
        
            # Custom bar styles
            bc.bars[0].fillColor = corporate_blue_light
            bc.bars[0].strokeColor = corporate_blue
            bc.bars[0].strokeWidth = 1
        
            # Customize axis
            bc.categoryAxis.labels.boxAnchor = 'ne'
            bc.categoryAxis.labels.dx = 8
            bc.categoryAxis.labels.dy = -2
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.fontName = 'Helvetica'
            bc.categoryAxis.labels.fontSize = 8
            bc.valueAxis.labels.fontName = 'Helvetica'
            bc.valueAxis.labels.fontSize = 8
            bc.valueAxis.gridStrokeColor = corporate_light_gray
            bc.valueAxis.gridStrokeWidth = 0.5
        
            drawing.add(bc)
            elements.append(drawing)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Figure 2: Performance scores by assessment area (higher scores indicate better performance)", styles["Caption"]))
            elements.append(Spacer(1, 18))
        
        # Add page break before risk assessment
        elements.append(PageBreak())
    
        # SECTION 2: RISK ASSESSMENT
        elements.append(Paragraph("SECTION 2: RISK ASSESSMENT", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        elements.append(Paragraph("Risk Factors Overview", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        # Enhanced risk assessment breakdown
        risk_data = {}
        if isinstance(assessment_results, dict) and "groups" in assessment_results:
            risk_group = assessment_results["groups"].get("risk", {})
            if isinstance(risk_group, dict):
                risk_data = risk_group.get("findings", {})
    
        # Create a more detailed risk table with better styling
        if risk_data and isinstance(risk_data, list) and risk_data:
            # Create a table for detailed risk data
            risk_table_data = [["Risk Type", "Description", "Impact Area", "Level", "Status"]]
        
            for risk in risk_data:
                if isinstance(risk, dict):
                    risk_level = risk.get('level', 0)
                    if isinstance(risk_level, (int, float)):
                        risk_level_str = f"{int(float(risk_level) * 100)}%"
                    else:
                        risk_level_str = str(risk_level)
                
                    risk_table_data.append([
                        risk.get("risk_type", "Unknown").capitalize(),
                        risk.get("description", ""),
                        risk.get("impact_area", ""),
                        risk_level_str,
                        risk.get("mitigation_status", "")
                    ])
        
            # Create table with enhanced styling
            risk_table = Table(risk_table_data, colWidths=[80, 180, 100, 50, 100])
            risk_style = [
                ('BACKGROUND', (0, 0), (-1, 0), corporate_blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, corporate_light_gray),
                ('BOX', (0, 0), (-1, -1), 1, corporate_gray),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Center the Level column
                ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Center the Status column
            ]
        
            # Add color coding for risk levels
            for i in range(1, len(risk_table_data)):
                level_text = risk_table_data[i][3]
                try:
                    level_value = float(level_text.strip('%')) / 100
                    if level_value >= 0.7:
                        risk_style.append(('BACKGROUND', (3, i), (3, i), corporate_red_light))
                    elif level_value >= 0.4:
                        risk_style.append(('BACKGROUND', (3, i), (3, i), corporate_yellow))
                    else:
                        risk_style.append(('BACKGROUND', (3, i), (3, i), corporate_green_light))
                except ValueError:
                    # If we can't parse the value, use default colors
                    pass
                
                # Add color coding for status
                status = risk_table_data[i][4].lower()
                if "complete" in status or "done" in status:
                    risk_style.append(('BACKGROUND', (4, i), (4, i), corporate_green_light))
                elif "progress" in status or "active" in status or "ongoing" in status:
                    risk_style.append(('BACKGROUND', (4, i), (4, i), corporate_yellow))
                elif "not" in status or "early" in status or "pending" in status:
                    risk_style.append(('BACKGROUND', (4, i), (4, i), corporate_red_light))
        
            risk_table.setStyle(TableStyle(risk_style))
            elements.append(risk_table)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Table 1: Identified risk factors and current mitigation status", styles["Caption"]))
        else:
            elements.append(Paragraph("No detailed risk data available.", styles["Normal"]))
    
        elements.append(Spacer(1, 18))
    
        # Add Risk Impact Assessment Chart
        elements.append(Paragraph("Risk Impact Assessment", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        # Create a risk matrix (custom drawing)
        def create_risk_matrix(risks, width=500, height=300):
            drawing = Drawing(width, height)
        
            # Draw matrix grid
            rect = Rect(50, 50, 400, 200, fillColor=None, strokeColor=corporate_gray, strokeWidth=1)
            drawing.add(rect)
        
            # Add grid lines
            for i in range(1, 4):  # 3 vertical lines for probability
                drawing.add(Rect(50 + i * 100, 50, 0, 200, fillColor=None, strokeColor=corporate_gray, strokeWidth=0.5))
            
            for i in range(1, 3):  # 2 horizontal lines for impact
                drawing.add(Rect(50, 50 + i * 66.67, 400, 0, fillColor=None, strokeColor=corporate_gray, strokeWidth=0.5))
        
            # Add axis labels
            from reportlab.graphics.shapes import String
            drawing.add(String(250, 20, "Probability", fontName="Helvetica-Bold", fontSize=10, textAnchor="middle"))
            drawing.add(String(20, 150, "Impact", fontName="Helvetica-Bold", fontSize=10, textAnchor="middle", angle=90))
        
            # Add matrix labels
            drawing.add(String(100, 30, "Low", fontName="Helvetica", fontSize=8))
            drawing.add(String(200, 30, "Medium", fontName="Helvetica", fontSize=8))
            drawing.add(String(300, 30, "High", fontName="Helvetica", fontSize=8))
            drawing.add(String(400, 30, "Critical", fontName="Helvetica", fontSize=8))
        
            drawing.add(String(35, 80, "Low", fontName="Helvetica", fontSize=8))
            drawing.add(String(35, 150, "Medium", fontName="Helvetica", fontSize=8))
            drawing.add(String(35, 220, "High", fontName="Helvetica", fontSize=8))
        
            # Color zones
            # Green zone (low risk)
            drawing.add(Rect(50, 50, 100, 66.67, fillColor=corporate_green_light, strokeColor=None))
            # Yellow zones (medium risk)
            drawing.add(Rect(150, 50, 100, 66.67, fillColor=corporate_yellow, strokeColor=None))
            drawing.add(Rect(50, 116.67, 100, 66.67, fillColor=corporate_yellow, strokeColor=None))
            # Orange zones (high risk)
            drawing.add(Rect(250, 50, 100, 66.67, fillColor=PCMYKColor(0, 60, 80, 0), strokeColor=None))
            drawing.add(Rect(150, 116.67, 100, 66.67, fillColor=PCMYKColor(0, 60, 80, 0), strokeColor=None))
            drawing.add(Rect(50, 183.34, 100, 66.67, fillColor=PCMYKColor(0, 60, 80, 0), strokeColor=None))
            # Red zones (critical risk)
            drawing.add(Rect(350, 50, 100, 66.67, fillColor=corporate_red_light, strokeColor=None))
            drawing.add(Rect(250, 116.67, 100, 66.67, fillColor=corporate_red_light, strokeColor=None))
            drawing.add(Rect(150, 183.34, 100, 66.67, fillColor=corporate_red_light, strokeColor=None))
            drawing.add(Rect(50, 250, 400, 66.67, fillColor=corporate_red_light, strokeColor=None))
        
            # Place the risks on the matrix (would need actual risk data with probability and impact)
            # This is placeholder code - in real implementation, you'd place actual risk dots based on data
            if risks and isinstance(risks, list):
                for i, risk in enumerate(risks[:5]):  # Limit to 5 risks for clarity
                    # Determine position based on probability and impact
                    # For this example, we'll just place them in different cells
                    positions = [
                        (100, 80),   # Low prob, low impact
                        (200, 150),  # Medium prob, medium impact
                        (300, 220),  # High prob, high impact
                        (250, 180),  # Medium-high prob, high impact
                        (350, 120)   # High prob, medium impact
                    ]
                
                    if i < len(positions):
                        x, y = positions[i]
                        from reportlab.graphics.shapes import Circle
                        dot = Circle(x, y, 10, fillColor=colors.white, strokeColor=corporate_blue, strokeWidth=2)
                        drawing.add(dot)
                    
                        # Add risk number
                        text = String(x, y, str(i+1), fontName="Helvetica-Bold", fontSize=8, fillColor=corporate_blue, textAnchor="middle")
                        drawing.add(text)
        
            return drawing
    
        # Add risk matrix to PDF
        elements.append(create_risk_matrix(risk_data if isinstance(risk_data, list) else []))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Figure 3: Risk assessment matrix showing probability and impact of identified risks", styles["Caption"]))
        elements.append(Spacer(1, 24))
    
        # Add page break before strategic recommendations
        elements.append(PageBreak())
    
        # SECTION 3: STRATEGIC RECOMMENDATIONS
        elements.append(Paragraph("SECTION 3: STRATEGIC RECOMMENDATIONS", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        # Add strategy development approach
        user_inputs = assessment_results.get("user_inputs", {})
        risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
        priorities = user_inputs.get("priorities", [])
    
        elements.append(Paragraph("Strategy Development Approach", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        approach_text = f"""The following strategic recommendations have been tailored to {entity_name}'s current situation with 
        a <b>{risk_tolerance} risk tolerance</b> approach. """
    
        if priorities:
            approach_text += f"""Priority areas include: <b>{', '.join(priorities)}</b>."""
    
        elements.append(Paragraph(approach_text, styles["Normal"]))
        elements.append(Spacer(1, 6))
    
        # Risk tolerance explanation with better formatting
        tolerance_explanations = {
            "High": "Taking aggressive approaches that prioritize growth opportunities over safety.",
            "Medium": "Balancing risk mitigation with strategic growth initiatives.",
            "Low": "Prioritizing stability and risk mitigation over aggressive growth."
        }
    
        elements.append(Paragraph(f"<b>{risk_tolerance} risk tolerance</b> means: {tolerance_explanations.get(risk_tolerance, '')}", styles["Normal"]))
        elements.append(Spacer(1, 18))
    
        # Add recommendations with enhanced styling
        elements.append(Paragraph("Strategic Recommendations", styles["Subsection_Title"]))
        elements.append(Spacer(1, 12))
    
        recommendations = assessment_results.get("recommendations", [])
    
        for i, rec in enumerate(recommendations):
            # Create a custom styled recommendation box
            elements.append(Paragraph(f"{i+1}. {rec.get('title', 'Untitled Strategy')}", styles["Subsection_Title"]))
            elements.append(Spacer(1, 3))
        
            # Priority and timeline with colored indicators
            priority = rec.get('priority', 'medium').capitalize()
            timeline = rec.get('timeline', 'medium').capitalize()
        
            # Set priority color
            priority_color = corporate_red if priority == "High" else corporate_yellow if priority == "Medium" else corporate_green
            priority_text = f"Priority: <font color={priority_color}>{priority}</font> | Timeline: {timeline}"
        
            elements.append(Paragraph(priority_text, styles["Normal"]))
            elements.append(Spacer(1, 6))
        
            # Create a bordered box for the recommendation content
            rationale = rec.get('rationale', '')
            elements.append(Paragraph("<b>Rationale:</b>", styles["Normal_Bold"]))
            elements.append(Paragraph(rationale, styles["Normal"]))
            elements.append(Spacer(1, 6))
        
            # Add benefits section with visual improvements
            elements.append(Paragraph("<b>Expected Benefits:</b>", styles["Normal_Bold"]))
            benefits_list = rec.get('benefits', [])
            for benefit in benefits_list:
                elements.append(Paragraph(f"• {benefit}", styles["Summary_Item"]))
            elements.append(Spacer(1, 6))
        
            # Add implementation steps with numbered format
            elements.append(Paragraph("<b>Implementation Steps:</b>", styles["Normal_Bold"]))
            steps = rec.get('implementation_steps', [])
            for idx, step in enumerate(steps):
                elements.append(Paragraph(f"{idx+1}. {step}", styles["Summary_Item"]))
            elements.append(Spacer(1, 6))
        
            # Add KPIs with bullet points
            elements.append(Paragraph("<b>Success Metrics (KPIs):</b>", styles["Normal_Bold"]))
            kpis = rec.get('kpis', [])
            for kpi in kpis:
                elements.append(Paragraph(f"• {kpi}", styles["Summary_Item"]))
        
            # Add visual separator between recommendations
            elements.append(Spacer(1, 6))
            from reportlab.platypus import HRFlowable
            elements.append(HRFlowable(width="100%", thickness=1, color=corporate_light_gray, 
                                    spaceBefore=10, spaceAfter=10))
    
        # Add strategy priority distribution chart if available
        if "strategy_priorities" in charts:
            elements.append(Paragraph("Strategy Priority Distribution", styles["Normal_Bold"]))
            elements.append(Spacer(1, 6))
        
            # Create a simple horizontal bar chart for priority distribution
            priority_data = charts.get("strategy_priorities", {}).get("data", [])
        
            if priority_data:
                drawing = Drawing(400, 150)
            
                # Create simple bars for priority distribution
                bar_height = 20
                bar_spacing = 30
                max_value = max([item.get("value", 0) for item in priority_data])
                bar_width_factor = 300 / max(1, max_value)  # Max width of 300
            
                for i, item in enumerate(priority_data):
                    label = item.get("label", "")
                    value = item.get("value", 0)
                
                    # Choose color based on priority
                    if "High" in label:
                        color = corporate_red_light
                    elif "Medium" in label:
                        color = corporate_yellow
                    else:
                        color = corporate_green_light
                
                    # Draw the bar
                    bar_width = value * bar_width_factor
                    y_pos = 120 - (i * bar_spacing)
                    drawing.add(Rect(50, y_pos, bar_width, bar_height, fillColor=color, strokeColor=None))
                
                    # Add label and value
                    from reportlab.graphics.shapes import String
                    drawing.add(String(45, y_pos + bar_height/2, label, fontName="Helvetica", 
                                    fontSize=8, textAnchor="end"))
                    drawing.add(String(55 + bar_width, y_pos + bar_height/2, str(value), 
                                    fontName="Helvetica", fontSize=8))
            
                elements.append(drawing)
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Figure 4: Distribution of strategy recommendations by priority level", 
                                        styles["Caption"]))
    
        elements.append(Spacer(1, 18))
    
        # Add page break before implementation timeline
        elements.append(PageBreak())
    
        # SECTION 4: IMPLEMENTATION ROADMAP
        elements.append(Paragraph("SECTION 4: IMPLEMENTATION ROADMAP", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        elements.append(Paragraph("Strategic Implementation Timeline", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        elements.append(Paragraph(
            """The following timeline illustrates the recommended sequence and duration for 
            implementing the strategic recommendations. High priority items should be
            initiated first, with consideration for dependencies between related initiatives.""",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 12))
    
        # Create implementation roadmap (gantt chart style)
        # If we have implementation timeline data, use it
        if "implementation_timeline" in charts:
            timeline_data = charts.get("implementation_timeline", {}).get("data", [])
        
            if timeline_data:
                # Create simplified Gantt chart
                drawing = Drawing(500, 250)
            
                # Draw timeline axis
                axis_y = 50
                axis_length = 400
                from reportlab.graphics.shapes import Line
                drawing.add(Line(50, axis_y, 50 + axis_length, axis_y, 
                            strokeColor=corporate_gray, strokeWidth=1))
            
                # Draw time markers
                months = ['Month 1', 'Month 3', 'Month 6', 'Month 9', 'Month 12', 'Month 18']
                marker_positions = [0, 0.17, 0.33, 0.5, 0.67, 1.0]  # Relative positions
            
                for i, (month, pos) in enumerate(zip(months, marker_positions)):
                    x = 50 + (axis_length * pos)
                    drawing.add(Line(x, axis_y, x, axis_y - 5, strokeColor=corporate_gray))
                    drawing.add(String(x, axis_y - 15, month, fontSize=7, textAnchor="middle"))
            
                # Draw the timeline bars for each recommendation
                row_height = 25
                timeline_items = []
            
                # Sort recommendations for the timeline (keep high priority on top)
                if recommendations:
                    priority_order = {"high": 0, "medium": 1, "low": 2}
                    sorted_recs = sorted(recommendations, 
                                    key=lambda r: priority_order.get(r.get("priority", "medium").lower(), 1))
                
                    for i, rec in enumerate(sorted_recs[:5]):  # Show top 5 recommendations
                        title = rec.get("title", f"Strategy {i+1}")
                        priority = rec.get("priority", "medium").lower()
                        timeline = rec.get("timeline", "medium").lower()
                    
                        # Determine bar length based on timeline
                        if timeline == "short":
                            duration = 0.25  # 3 months
                        elif timeline == "medium":
                            duration = 0.5   # 6 months
                        else:
                            duration = 0.75  # 9 months
                    
                        # Determine bar position (stagger start dates slightly)
                        start_pos = 0.05 + (i * 0.05)  # Stagger starts slightly
                    
                        # Choose color based on priority
                        if priority == "high":
                            color = corporate_red_light
                        elif priority == "medium":
                            color = corporate_yellow
                        else:
                            color = corporate_green_light
                    
                        # Calculate bar coordinates
                        y = 80 + (i * row_height)
                        x1 = 50 + (start_pos * axis_length)
                        x2 = x1 + (duration * axis_length)
                    
                        # Draw the timeline bar
                        drawing.add(Rect(x1, y, x2-x1, row_height-10, 
                                    fillColor=color, strokeColor=corporate_gray))
                    
                        # Add label
                        short_title = title[:25] + "..." if len(title) > 25 else title
                        drawing.add(String(45, y + (row_height-10)/2, short_title, 
                                        fontSize=8, textAnchor="end"))
                    
                        # Add to the list
                        timeline_items.append({
                            "title": title,
                            "y": y,
                            "start": x1,
                            "end": x2,
                            "color": color
                        })
            
                elements.append(drawing)
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Figure 5: Implementation timeline for strategic recommendations", 
                                        styles["Caption"]))
        else:
            # Create a placeholder timeline using recommendations data
            if recommendations:
                # Create simplified Gantt chart
                drawing = Drawing(500, 250)
            
                # Draw timeline axis
                axis_y = 50
                axis_length = 400
                from reportlab.graphics.shapes import Line
                drawing.add(Line(50, axis_y, 50 + axis_length, axis_y, 
                            strokeColor=corporate_gray, strokeWidth=1))
            
                # Draw time markers
                months = ['Month 1', 'Month 3', 'Month 6', 'Month 9', 'Month 12', 'Month 18']
                marker_positions = [0, 0.17, 0.33, 0.5, 0.67, 1.0]  # Relative positions
            
                for i, (month, pos) in enumerate(zip(months, marker_positions)):
                    x = 50 + (axis_length * pos)
                    drawing.add(Line(x, axis_y, x, axis_y - 5, strokeColor=corporate_gray))
                    drawing.add(String(x, axis_y - 15, month, fontSize=7, textAnchor="middle"))
            
                # Draw the timeline bars for each recommendation
                row_height = 25
            
                # Sort recommendations (high priority on top)
                priority_order = {"high": 0, "medium": 1, "low": 2}
                sorted_recs = sorted(recommendations, 
                                key=lambda r: priority_order.get(r.get("priority", "medium").lower(), 1))
            
                for i, rec in enumerate(sorted_recs[:5]):  # Show top 5 recommendations
                    title = rec.get("title", f"Strategy {i+1}")
                    priority = rec.get("priority", "medium").lower()
                    timeline = rec.get("timeline", "medium").lower()
                
                    # Determine bar length based on timeline
                    if timeline == "short":
                        duration = 0.25  # 3 months
                    elif timeline == "medium":
                        duration = 0.5   # 6 months
                    else:
                        duration = 0.75  # 9 months
                
                    # Determine bar position (stagger start dates slightly)
                    start_pos = 0.05 + (i * 0.05)  # Stagger starts slightly
                
                    # Choose color based on priority
                    if priority == "high":
                        color = corporate_red_light
                    elif priority == "medium":
                        color = corporate_yellow
                    else:
                        color = corporate_green_light
                
                    # Calculate bar coordinates
                    y = 80 + (i * row_height)
                    x1 = 50 + (start_pos * axis_length)
                    x2 = x1 + (duration * axis_length)
                
                    # Draw the timeline bar
                    drawing.add(Rect(x1, y, x2-x1, row_height-10, 
                                fillColor=color, strokeColor=corporate_gray))
                
                    # Add label
                    short_title = title[:25] + "..." if len(title) > 25 else title
                    drawing.add(String(45, y + (row_height-10)/2, short_title, 
                                    fontSize=8, textAnchor="end"))
            
                elements.append(drawing)
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Figure 5: Implementation timeline for strategic recommendations", 
                                        styles["Caption"]))
    
        elements.append(Spacer(1, 18))
    
        # Add implementation considerations
        elements.append(Paragraph("Implementation Considerations", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        considerations_text = f"""
        Successful execution of these strategies will require coordinated effort across multiple business functions.
        Key considerations include:
        """
        elements.append(Paragraph(considerations_text, styles["Normal"]))
        elements.append(Spacer(1, 6))
    
        considerations = [
            "Resources and budget allocation should align with strategic priorities",
            "Regular progress monitoring against defined KPIs is essential",
            "Cross-functional teams should be established for each major initiative",
            "Change management processes should be implemented to address organizational impact",
            "Leadership alignment and consistent communication are critical success factors"
        ]
    
        for consideration in considerations:
            elements.append(Paragraph(f"• {consideration}", styles["Summary_Item"]))
    
        # Add page break before performance metrics
        elements.append(PageBreak())
    
        # SECTION 5: PERFORMANCE METRICS
        elements.append(Paragraph("SECTION 5: PERFORMANCE METRICS", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        elements.append(Paragraph("Key Performance Indicators", styles["Subsection_Title"]))
        elements.append(Spacer(1, 6))
    
        elements.append(Paragraph(
            """The following metrics should be tracked to measure the success of the strategic initiatives.
            Each metric is aligned with specific strategic objectives and should be monitored at the 
            recommended frequency.""",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 12))
    
        # Create KPI dashboard
        # Collect KPIs from all recommendations
        all_kpis = []
        for rec in recommendations:
            for kpi in rec.get('kpis', []):
                # Add KPI with its associated strategy
                all_kpis.append({
                    "metric": kpi,
                    "strategy": rec.get('title', ''),
                    "priority": rec.get('priority', 'medium')
                })
    
        # Group similar KPIs
        kpi_groups = {
            "Financial": [],
            "Market": [],
            "Operational": [],
            "Customer": []
        }
    
        # Categorize KPIs (simple keyword matching)
        for kpi in all_kpis:
            metric = kpi["metric"].lower()
            if any(word in metric for word in ["revenue", "profit", "cost", "margin", "roi", "financial"]):
                kpi_groups["Financial"].append(kpi)
            elif any(word in metric for word in ["market", "share", "competitor", "industry"]):
                kpi_groups["Market"].append(kpi)
            elif any(word in metric for word in ["process", "efficiency", "productivity", "time"]):
                kpi_groups["Operational"].append(kpi)
            elif any(word in metric for word in ["customer", "satisfaction", "nps", "retention"]):
                kpi_groups["Customer"].append(kpi)
            else:
                # Default to operational if no clear category
                kpi_groups["Operational"].append(kpi)
    
        # Create a KPI table for each category
        for category, kpis in kpi_groups.items():
            if kpis:
                elements.append(Paragraph(f"{category} Metrics", styles["Normal_Bold"]))
                elements.append(Spacer(1, 6))
            
                kpi_table_data = [["Metric", "Associated Strategy", "Priority", "Frequency"]]
            
                for kpi in kpis:
                    # Assign a reasonable monitoring frequency based on priority
                    if kpi["priority"].lower() == "high":
                        frequency = "Weekly"
                    elif kpi["priority"].lower() == "medium":
                        frequency = "Monthly"
                    else:
                        frequency = "Quarterly"
                
                    kpi_table_data.append([
                        kpi["metric"], 
                        kpi["strategy"][:30] + "..." if len(kpi["strategy"]) > 30 else kpi["strategy"],
                        kpi["priority"].capitalize(),
                        frequency
                    ])
            
                kpi_table = Table(kpi_table_data, colWidths=[180, 180, 70, 80])
                kpi_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), corporate_blue_light),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, corporate_light_gray),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                    ('ALIGN', (3, 0), (3, -1), 'CENTER')
                ]
            
                # Color code priority column
                for i in range(1, len(kpi_table_data)):
                    priority = kpi_table_data[i][2].lower()
                    if priority == "high":
                        kpi_style.append(('BACKGROUND', (2, i), (2, i), corporate_red_light))
                    elif priority == "medium":
                        kpi_style.append(('BACKGROUND', (2, i), (2, i), corporate_yellow))
                    else:
                        kpi_style.append(('BACKGROUND', (2, i), (2, i), corporate_green_light))
            
                kpi_table.setStyle(TableStyle(kpi_style))
                elements.append(kpi_table)
                elements.append(Spacer(1, 12))
    
        # If there are financial metrics, add a performance projection chart
        if "Financial" in kpi_groups and kpi_groups["Financial"]:
            elements.append(Paragraph("Performance Projections", styles["Subsection_Title"]))
            elements.append(Spacer(1, 6))
        
            # Create a simple line chart showing projected performance improvements
            drawing = Drawing(500, 200)
        
            # Create line chart
            chart = LineChart()
            chart.x = 50
            chart.y = 50
            chart.width = 400
            chart.height = 125
        
            # Chart data - projected improvement over time
            # This is placeholder data - in a real implementation, would use actual projections
            chart.data = [
                [1.0, 1.05, 1.12, 1.18, 1.25, 1.32],  # Revenue index
                [1.0, 1.02, 1.06, 1.12, 1.15, 1.20],  # Profit index
                [1.0, 1.03, 1.08, 1.15, 1.20, 1.28]   # Market share index
            ]
        
            # X axis - quarters
            chart.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4', 'Q1', 'Q2']
            chart.categoryAxis.labels.fontSize = 8
            chart.categoryAxis.labels.boxAnchor = 'n'
        
            # Y axis
            chart.valueAxis.valueMin = 0.9
            chart.valueAxis.valueMax = 1.4
            chart.valueAxis.valueStep = 0.1
            chart.valueAxis.labels.fontSize = 8
            chart.valueAxis.gridStrokeColor = corporate_light_gray
            chart.valueAxis.gridStrokeWidth = 0.5
        
            # Line styles
            chart.lines[0].strokeColor = corporate_blue
            chart.lines[0].strokeWidth = 2
            chart.lines[0].symbol = makeMarker('FilledCircle')
            chart.lines[0].symbol.size = 5
        
            chart.lines[1].strokeColor = corporate_green
            chart.lines[1].strokeWidth = 2
            chart.lines[1].symbol = makeMarker('FilledDiamond')
            chart.lines[1].symbol.size = 5
        
            chart.lines[2].strokeColor = corporate_red
            chart.lines[2].strokeWidth = 2
            chart.lines[2].symbol = makeMarker('FilledSquare')
            chart.lines[2].symbol.size = 5
        
            # Add legend
            legend = Legend()
            legend.alignment = 'right'
            legend.fontName = 'Helvetica'
            legend.fontSize = 8
            legend.x = 470
            legend.y = 130
            legend.colorNamePairs = [
                (corporate_blue, 'Revenue'), 
                (corporate_green, 'Profit'),
                (corporate_red, 'Market Share')
            ]   
        
            drawing.add(chart)
            drawing.add(legend)
            elements.append(drawing)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Figure 6: Projected performance improvements (indexed to Q1 baseline)", 
                                    styles["Caption"]))
    
        elements.append(Spacer(1, 24))
    
        # Add page break before appendix
        elements.append(PageBreak())
    
        # APPENDIX: DETAILED ASSESSMENT DATA
        elements.append(Paragraph("APPENDIX: DETAILED ASSESSMENT DATA", styles["Section_Title"]))
        elements.append(Spacer(1, 12))
    
        # Add details for each assessment group
        for group_id, group_data in assessment_results.get("groups", {}).items():
            # Skip empty groups
            if not group_data:
                continue
            
            # Group header
            elements.append(Paragraph(group_data.get("name", group_id.capitalize()), styles["Subsection_Title"]))
            elements.append(Spacer(1, 3))
        
            # Group description
            if "description" in group_data:
                elements.append(Paragraph(group_data["description"], styles["Normal"]))
                elements.append(Spacer(1, 6))
        
            # Group score and risk level with improved formatting
            score = group_data.get("score", 0.5)
            risk_level = group_data.get("risk_level", "Medium")
            score_percent = f"{score * 100:.1f}%"
        
            # Create score gauge for this group
            drawing = Drawing(200, 40)
        
            # Background bar
            drawing.add(Rect(0, 15, 150, 15, fillColor=corporate_light_gray, strokeColor=None))
        
            # Score bar
            score_width = min(150 * score, 150)
            if score >= 0.7:
                fill_color = corporate_green
            elif score >= 0.4:
                fill_color = corporate_yellow
            else:
                fill_color = corporate_red
            
            drawing.add(Rect(0, 15, score_width, 15, fillColor=fill_color, strokeColor=None))
        
            # Add labels
            from reportlab.graphics.shapes import String
            drawing.add(String(75, 5, f"{score*100:.1f}%", fontName="Helvetica-Bold", 
                            fontSize=8, textAnchor="middle"))
        
            elements.append(Paragraph(f"Score: {score_percent} | Risk Level: {risk_level}", styles["Normal_Bold"]))
            elements.append(drawing)
            elements.append(Spacer(1, 12))
        
            # Key findings
            findings = group_data.get("findings", [])
            if findings:
                elements.append(Paragraph("Key Findings:", styles["Normal_Bold"]))
            
                if isinstance(findings, dict):
                    # Handle dictionary-type findings
                    for finding_type, finding_value in findings.items():
                        if finding_type != "reasoning":
                            elements.append(Paragraph(f"• {finding_type.capitalize()}: {finding_value}", 
                                                styles["Summary_Item"]))
                elif isinstance(findings, list):
                    # Handle list-type findings
                    for finding in findings:
                        if isinstance(finding, dict):
                            # Handle dictionary-type finding
                            finding_type = finding.get("type", "other").capitalize()
                            description = finding.get("description", "")
                            elements.append(Paragraph(f"• {finding_type}: {description}", 
                                                styles["Summary_Item"]))
                        elif isinstance(finding, str):
                            # Handle string-type finding
                            elements.append(Paragraph(f"• {finding}", 
                                                styles["Summary_Item"]))
            
                elements.append(Spacer(1, 6))
        
            # Add metrics if available
            metrics = group_data.get("metrics", {})
            if metrics:
                elements.append(Paragraph("Metrics:", styles["Normal_Bold"]))
            
                # Create metrics table
                metrics_data = [["Metric", "Value", "Trend"]]
                for metric_name, metric_data in metrics.items():
                    if isinstance(metric_data, dict):
                        value = metric_data.get("value", "N/A")
                        unit = metric_data.get("unit", "")
                        if unit:
                            value = f"{value} {unit}"
                    
                        trend = metric_data.get("trend", "stable")
                        metrics_data.append([metric_name, value, trend])
            
                # Create and style the table
                metrics_table = Table(metrics_data, colWidths=[200, 150, 150])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (2, 0), corporate_blue_light),
                    ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
                    ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (2, 0), 8),
                    ('GRID', (0, 0), (2, len(metrics_data)-1), 0.5, corporate_light_gray),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER')
                ]))
            
                # Color code trends
                for i in range(1, len(metrics_data)):
                    trend = metrics_data[i][2].lower()
                    if "increase" in trend or "improving" in trend or "growth" in trend:
                        metrics_table.setStyle(TableStyle([
                            ('TEXTCOLOR', (2, i), (2, i), corporate_green)
                        ]))
                    elif "decrease" in trend or "declining" in trend:
                        metrics_table.setStyle(TableStyle([
                            ('TEXTCOLOR', (2, i), (2, i), corporate_red)
                        ]))
            
                elements.append(metrics_table)
                elements.append(Spacer(1, 12))
        
            # Add space between groups
            elements.append(Spacer(1, 24))
        
            # Add a horizontal line between assessment areas
            elements.append(HRFlowable(width="100%", thickness=1, color=corporate_light_gray, 
                                    spaceBefore=0, spaceAfter=12))
    
        # Build PDF
        from reportlab.graphics.shapes import makeMarker
        from reportlab.graphics.charts.legends import Legend
    
        doc.build(elements)
        logger.info(f"Generated enhanced assessment PDF: {filepath}")
    
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