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
    
    def generate_assessment_pdfs(self, assessment_results: Dict[str, Any], charts: Dict[str, Dict[str, Any]], risk_level: str) -> List[str]:
        """
        Generate all three PDF reports for strategy assessment results.
        
        Args:
            assessment_results: Assessment results
            charts: Chart configurations for visualization
            risk_level: Risk level (H/M/L) from user input
            
        Returns:
            list: Paths to the generated PDFs
        """
        entity_name = assessment_results.get("entity", "Unknown Entity")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        pdf_paths = []
        
        # 1. Strategy Summary Recommendation PDF
        summary_filepath = os.path.join(self.output_dir, f"strategy_summary_{entity_name.replace(' ', '_')}_{risk_level}_{timestamp}.pdf")
        summary_path = self._generate_strategy_summary_pdf(assessment_results, charts, risk_level, summary_filepath)
        pdf_paths.append(summary_path)
        
        # 2. Strategic Assessment Chart - Goals PDF
        assessment_filepath = os.path.join(self.output_dir, f"strategic_assessment_{entity_name.replace(' ', '_')}_{risk_level}_{timestamp}.pdf")
        assessment_path = self._generate_strategic_assessment_pdf(assessment_results, charts, risk_level, assessment_filepath)
        pdf_paths.append(assessment_path)
        
        # 3. Execution Chart - Goals PDF
        execution_filepath = os.path.join(self.output_dir, f"execution_chart_{entity_name.replace(' ', '_')}_{risk_level}_{timestamp}.pdf")
        execution_path = self._generate_execution_chart_pdf(assessment_results, charts, risk_level, execution_filepath)
        pdf_paths.append(execution_path)
        
        return pdf_paths
    
    def _generate_strategy_summary_pdf(self, assessment_results, charts, risk_level, filepath):
        """
        Generate Strategy Summary Recommendation PDF.
    
        Args:
            assessment_results: Assessment results data
            charts: Chart configurations
            risk_level: Risk level (H/M/L)
            filepath: Output file path
        
        Returns:
            str: Path to the generated PDF
        """
        if self.pdf_engine == "reportlab":
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.charts.barcharts import VerticalBarChart
            from reportlab.graphics.charts.piecharts import Pie
        
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = self.pdf_lib["styles"]
            elements = []
        
            # Add title and cover page
            entity_name = assessment_results.get("entity", "Unknown Entity")
            title = f"Strategy Summary Recommendation: {entity_name} (Risk: {risk_level})"
            elements.append(Paragraph(title, styles["Heading1Center"]))
            elements.append(Spacer(1, 24))
        
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
            elements.append(Spacer(1, 36))
        
            # Get user inputs
            user_inputs = assessment_results.get("user_inputs", {})
            risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
            priorities = user_inputs.get("priorities", [])
            constraints = user_inputs.get("constraints", [])
        
            # Add executive summary
            elements.append(Paragraph("Executive Summary", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            summary = assessment_results.get("summary", {})
            overall_score = summary.get("overall_score", 0.5)
            risk_level_full = summary.get("risk_level", "Medium")
        
            # Format score as percentage
            score_percent = f"{overall_score * 100:.1f}%"
        
            # Add current state explanation
            elements.append(Paragraph(
                f"This strategy summary provides recommendations for {entity_name} based on a comprehensive assessment " +
                f"of 30 business areas. The analysis indicates an overall performance score of {score_percent} with " +
                f"a risk level assessed as {risk_level_full}.",
                styles["Normal"]
            ))
            elements.append(Spacer(1, 12))
        
            # Add risk tolerance and priorities
            elements.append(Paragraph(
                f"Strategy recommendations are tailored to a <b>{risk_tolerance} risk tolerance</b> approach. " +
                (f"Priority areas include: <b>{', '.join(priorities)}</b>." if priorities else "") +
                (f" Key constraints considered: <b>{', '.join(constraints)}</b>." if constraints else ""),
                styles["Normal"]
            ))
            elements.append(Spacer(1, 18))
        
            # Top Recommendations
            elements.append(Paragraph("Top Strategic Recommendations", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            recommendations = assessment_results.get("recommendations", [])
            # Limit to top 3-5 recommendations
            top_recommendations = recommendations[:min(5, len(recommendations))]
        
            for i, rec in enumerate(top_recommendations):
                # Recommendation header
                elements.append(Paragraph(f"{i+1}. {rec.get('title')}", styles["Heading3"]))
                elements.append(Spacer(1, 3))
            
                # Priority and timeline
                priority = rec.get('priority', 'medium').capitalize()
                timeline = rec.get('timeline', 'medium').capitalize()
            
                elements.append(Paragraph(f"Priority: {priority} | Timeline: {timeline}", styles["Normal-Bold"]))
                elements.append(Spacer(1, 6))
            
                # Rationale
                elements.append(Paragraph(rec.get('rationale', ''), styles["Normal"]))
                elements.append(Spacer(1, 6))
            
                # Benefits
                if rec.get('benefits'):
                    elements.append(Paragraph("Key Benefits:", styles["Normal-Bold"]))
                    for benefit in rec.get('benefits', []):
                        elements.append(Paragraph(f"• {benefit}", styles["Normal"]))
                    elements.append(Spacer(1, 12))
        
            # Add key risk factors
            elements.append(PageBreak())
            elements.append(Paragraph("Key Risk Factors", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            # Extract risk assessment group
            risk_group = None
            for group_id, group_data in assessment_results.get("groups", {}).items():
                if "risk" in group_id.lower():
                    risk_group = group_data
                    break
        
            if risk_group and risk_group.get("findings"):
                # Show top risks
                risk_findings = risk_group.get("findings", [])
                if isinstance(risk_findings, list):
                    # Sort risks by level/importance if possible
                    if all(isinstance(r, dict) for r in risk_findings):
                        risk_findings.sort(key=lambda r: float(r.get("level", 0)) if isinstance(r.get("level"), (int, float, str)) else 0, reverse=True)
                
                    for i, risk in enumerate(risk_findings[:5]):  # Show top 5 risks
                        if isinstance(risk, dict):
                            risk_type = risk.get("risk_type", "Unknown").capitalize()
                            description = risk.get("description", "")
                            elements.append(Paragraph(f"{i+1}. {risk_type}: {description}", styles["Normal-Bold"]))
                        
                            # Add impact area and probability if available
                            impact = risk.get("impact_area", "")
                            probability = risk.get("probability", "")
                            if impact or probability:
                                elements.append(Paragraph(
                                    f"Impact Area: {impact} | Probability: {probability}", 
                                    styles["Normal"]
                                ))
                            elements.append(Spacer(1, 12))
                else:
                    # Handle dictionary format if that's what's provided
                    for risk_type, level in risk_findings.items():
                        if risk_type != "reasoning":
                            elements.append(Paragraph(
                                f"• {risk_type.capitalize()}: {level}",
                                styles["Normal-Bold"]
                            ))
                    elements.append(Spacer(1, 12))
            else:
                elements.append(Paragraph("No specific risk factors identified.", styles["Normal"]))
                elements.append(Spacer(1, 12))
        
            # Add priority distribution chart if available
            if "strategy_priorities" in charts:
                elements.append(Paragraph("Recommendation Priority Distribution", styles["Heading3"]))
                elements.append(Spacer(1, 6))
            
                # Create chart
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
                bc.bars[0].fillColor = colors.steelblue
            
                drawing.add(bc)
                elements.append(drawing)
                elements.append(Spacer(1, 24))
        
            # Build the PDF
            doc.build(elements)
            logger.info(f"Generated Strategy Summary PDF: {filepath}")
            return filepath
        else:
            # Fallback to JSON export
            return self._generate_with_fallback(assessment_results, charts, filepath)

    def _generate_strategic_assessment_pdf(self, assessment_results, charts, risk_level, filepath):
        """
        Generate Strategic Assessment Chart - Goals PDF.
    
        Args:
            assessment_results: Assessment results data
            charts: Chart configurations
            risk_level: Risk level (H/M/L)
            filepath: Output file path
        
        Returns:
            str: Path to the generated PDF
        """
        if self.pdf_engine == "reportlab":
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.charts.barcharts import VerticalBarChart
            from reportlab.graphics.charts.piecharts import Pie
            from reportlab.graphics.charts.spider import SpiderChart
        
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = self.pdf_lib["styles"]
            elements = []
        
            # Add title and cover page
            entity_name = assessment_results.get("entity", "Unknown Entity")
            title = f"Strategic Assessment Chart - Goals: {entity_name} (Risk: {risk_level})"
            elements.append(Paragraph(title, styles["Heading1Center"]))
            elements.append(Spacer(1, 24))
        
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
            elements.append(Spacer(1, 36))
        
            # Get key data
            user_inputs = assessment_results.get("user_inputs", {})
            risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
        
            # Introduction
            elements.append(Paragraph("Assessment Overview", styles["Heading2"]))
            elements.append(Paragraph(
                f"This strategic assessment chart provides a visual representation of current performance and strategic goals " +
                f"for {entity_name}, tailored to a {risk_tolerance} risk tolerance profile.",
                styles["Normal"]
            ))
            elements.append(Spacer(1, 18))
        
            # Performance Overview by Group
            elements.append(Paragraph("Performance by Assessment Area", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            # Create table for group scores
            group_data = [["Assessment Area", "Score", "Risk Level"]]
            # Sort groups by score for better visualization
            sorted_groups = sorted(
                assessment_results.get("groups", {}).items(),
                key=lambda x: x[1].get("score", 0.5),
                reverse=True
            )
        
            for group_id, group_info in sorted_groups:
                name = group_info.get("name", group_id.capitalize())
                score = group_info.get("score", 0.5)
                risk_level = group_info.get("risk_level", "Medium")
                score_percent = f"{score * 100:.1f}%"
            
                group_data.append([name, score_percent, risk_level])
        
            # Create and style the table
            group_table = Table(group_data, colWidths=[250, 100, 150])
            group_table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        
            # Add color coding for risk levels
            for i in range(1, len(group_data)):
                risk_level = group_data[i][2]
                if risk_level == "Low":
                    group_table_style.append(('BACKGROUND', (2, i), (2, i), colors.lightgreen))
                elif risk_level == "Medium":
                    group_table_style.append(('BACKGROUND', (2, i), (2, i), colors.lightyellow))
                elif risk_level == "High":
                    group_table_style.append(('BACKGROUND', (2, i), (2, i), colors.lightcoral))
        
            group_table.setStyle(TableStyle(group_table_style))
            elements.append(group_table)
            elements.append(Spacer(1, 18))
        
            # Add bar chart for scores if available
            if "group_scores" in charts:
                elements.append(Paragraph("Assessment Area Performance Scores", styles["Heading3"]))
                elements.append(Spacer(1, 6))
            
                # Create bar chart
                data = charts["group_scores"]["data"]
                drawing = Drawing(500, 300)
                bc = VerticalBarChart()
                bc.x = 50
                bc.y = 50
                bc.height = 200
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
                elements.append(Paragraph("Higher scores (closer to 1.0) indicate better performance in each area.", 
                                        styles["Normal"]))
                elements.append(Spacer(1, 18))
        
            # Strategic goals visualization
            elements.append(PageBreak())
            elements.append(Paragraph("Strategic Goals", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            # Add radar chart for strategic goals if available
            if "strategic_goals" in charts:
                elements.append(Paragraph("Strategic Goals Assessment", styles["Heading3"]))
            
                # Create radar/spider chart
                radar_data = charts["strategic_goals"]
                categories = radar_data.get("categories", [])
                datasets = radar_data.get("datasets", [])
            
                if categories and datasets:
                    # Calculate dimensions
                    width, height = 400, 400
                    drawing = Drawing(width, height)
                
                    # Create spider chart
                    spider = SpiderChart()
                    spider.x = width // 2
                    spider.y = height // 2
                    spider.width = 300
                    spider.height = 300
                
                    # Add data
                    spider.data = [d.get("data", []) for d in datasets]
                    spider.labels = categories
                
                    # Customize appearance
                    spider.strands[0].strokeColor = colors.steelblue
                    if len(spider.strands) > 1:
                        spider.strands[1].strokeColor = colors.red
                
                    spider.fillColor = colors.steelblue
                    spider.fillAlpha = 0.2
                
                    # Add to drawing
                    drawing.add(spider)
                    elements.append(drawing)
                
                    # Add legend
                    legend_data = [[d.get("label", f"Dataset {i+1}") for i, d in enumerate(datasets)]]
                    legend_table = Table(legend_data)
                    legend_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ]))
                    elements.append(legend_table)
                    elements.append(Spacer(1, 18))
            
            # Strategic Improvement Areas
            elements.append(Paragraph("Strategic Improvement Areas", styles["Heading3"]))
            elements.append(Spacer(1, 6))
        
            # Extract areas needing most improvement
            concern_areas = assessment_results.get("summary", {}).get("concern_areas", [])
        
            if concern_areas:
                elements.append(Paragraph("Areas requiring strategic attention:", styles["Normal-Bold"]))
                for area_id in concern_areas:
                    area_data = assessment_results.get("groups", {}).get(area_id, {})
                    area_name = area_data.get("name", area_id.capitalize())
                    area_score = area_data.get("score", 0)
                    area_score_pct = f"{area_score * 100:.1f}%"
                
                    elements.append(Paragraph(
                        f"• {area_name} (Current Score: {area_score_pct})",
                        styles["Normal"]
                    ))
                
                    # Add key findings for this area
                    findings = area_data.get("findings", [])
                    if findings and isinstance(findings, list):
                        for finding in findings[:2]:  # Show top 2 findings per area
                            if isinstance(finding, dict):
                                elements.append(Paragraph(f"  - {finding.get('description', '')}", styles["Normal"]))
            
                elements.append(Spacer(1, 18))
            else:
                elements.append(Paragraph("No significant areas of concern identified.", styles["Normal"]))
                elements.append(Spacer(1, 18))
        
            # Build the PDF
            doc.build(elements)
            logger.info(f"Generated Strategic Assessment Chart PDF: {filepath}")
            return filepath
        else:
            # Fallback to JSON export
            return self._generate_with_fallback(assessment_results, charts, filepath)

    def _generate_execution_chart_pdf(self, assessment_results, charts, risk_level, filepath):
        """
        Generate Execution Chart - Goals PDF.
    
        Args:
            assessment_results: Assessment results data
            charts: Chart configurations
            risk_level: Risk level (H/M/L)
            filepath: Output file path
        
        Returns:
            str: Path to the generated PDF
        """
        if self.pdf_engine == "reportlab":
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing, Rect, String
            from reportlab.graphics.charts.barcharts import VerticalBarChart
            from reportlab.graphics.charts.linecharts import HorizontalLineChart
        
            # Create PDF document (landscape for better timeline view)
            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            styles = self.pdf_lib["styles"]
            elements = []
        
            # Add title and cover page
            entity_name = assessment_results.get("entity", "Unknown Entity")
            title = f"Execution Chart - Goals: {entity_name} (Risk: {risk_level})"
            elements.append(Paragraph(title, styles["Heading1Center"]))
            elements.append(Spacer(1, 24))
        
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
            elements.append(Spacer(1, 36))
        
            # Introduction
            elements.append(Paragraph("Execution Overview", styles["Heading2"]))
            elements.append(Paragraph(
                f"This execution chart provides a timeline and implementation plan for recommended strategies. " +
                f"It shows dependencies, resource requirements, and expected outcomes aligned with strategic goals.",
                styles["Normal"]
            ))
            elements.append(Spacer(1, 18))
        
            # Implementation Timeline
            elements.append(Paragraph("Implementation Timeline", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            # Create a simplified Gantt chart showing strategy implementation timelines
            recommendations = assessment_results.get("recommendations", [])
        
            if recommendations:
                # Create timeline data
                timeline_data = [["Strategy", "Priority", "Timeline", "0-6 months", "6-18 months", "18+ months"]]
            
                for rec in recommendations:
                    title = rec.get("title", "Untitled Strategy")
                    priority = rec.get("priority", "medium").capitalize()
                    timeline = rec.get("timeline", "medium").lower()
                
                    # Create row with timing indicators
                    row = [title, priority, timeline.capitalize()]
                
                    # Add visual indicators for timing
                    if timeline == "short":
                        row.extend(["●", "", ""])
                    elif timeline == "medium":
                        row.extend(["●", "●", ""])
                    else:  # long
                        row.extend(["●", "●", "●"])
                
                    timeline_data.append(row)
            
                # Create and style the table
                timeline_table = Table(timeline_data, colWidths=[200, 70, 70, 80, 80, 80])
                timeline_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (5, -1), 'CENTER'),
                ]
            
                # Add priority-based color coding
                for i in range(1, len(timeline_data)):
                    priority = timeline_data[i][1]
                    if priority == "High":
                        timeline_style.append(('BACKGROUND', (1, i), (1, i), colors.lightcoral))
                    elif priority == "Medium":
                        timeline_style.append(('BACKGROUND', (1, i), (1, i), colors.lightyellow))
                    elif priority == "Low":
                        timeline_style.append(('BACKGROUND', (1, i), (1, i), colors.lightgreen))
            
                timeline_table.setStyle(TableStyle(timeline_style))
                elements.append(timeline_table)
                elements.append(Spacer(1, 24))
        
            # Key Implementation Steps
            elements.append(PageBreak())
            elements.append(Paragraph("Key Implementation Steps", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            # Create table with implementation steps for each strategy
            if recommendations:
                for i, rec in enumerate(recommendations):
                    # Strategy header
                    elements.append(Paragraph(f"{i+1}. {rec.get('title')}", styles["Heading3"]))
                    elements.append(Spacer(1, 6))
                
                    # Implementation steps
                    steps = rec.get("implementation_steps", [])
                    if steps:
                        steps_data = [["Step", "Description"]]
                        for j, step in enumerate(steps):
                            steps_data.append([f"Step {j+1}", step])
                    
                        step_table = Table(steps_data, colWidths=[60, 440])
                        step_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        elements.append(step_table)
                    else:
                        elements.append(Paragraph("No specific implementation steps defined.", styles["Normal"]))
                
                    # KPIs for measuring success
                    elements.append(Spacer(1, 6))
                    elements.append(Paragraph("Success Metrics (KPIs):", styles["Normal-Bold"]))
                    kpis = rec.get("kpis", [])
                    if kpis:
                        for kpi in kpis:
                            elements.append(Paragraph(f"• {kpi}", styles["Normal"]))
                    else:
                        elements.append(Paragraph("No specific KPIs defined.", styles["Normal"]))
                
                    elements.append(Spacer(1, 18))
        
            # Resource Requirements
            elements.append(PageBreak())
            elements.append(Paragraph("Resource Requirements & Dependencies", styles["Heading2"]))
            elements.append(Spacer(1, 12))
        
            # This would normally be populated with actual resource requirements
            # For now we'll use a placeholder table
            elements.append(Paragraph(
                "The following resources and dependencies have been identified as critical for successful implementation:",
                styles["Normal"]
            ))
            elements.append(Spacer(1, 12))
        
            resource_data = [
                ["Resource Type", "Priority", "Timeline Needed"],
                ["Executive Sponsorship", "High", "Full Duration"],
                ["Cross-functional Team", "High", "Full Duration"],
                ["Technical Resources", "Medium", "Early Implementation"],
                ["Budget Allocation", "High", "Milestone-based"],
                ["Marketing Support", "Medium", "Later Stages"],
                ["Analytics Capabilities", "Medium", "Full Duration"]
            ]
        
            resource_table = Table(resource_data, colWidths=[200, 100, 200])
            resource_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(resource_table)
            elements.append(Spacer(1, 24))
        
            # Build the PDF
            doc.build(elements)
            logger.info(f"Generated Execution Chart PDF: {filepath}")
            return filepath
        else:
            # Fallback to JSON export
            return self._generate_with_fallback(assessment_results, charts, filepath)