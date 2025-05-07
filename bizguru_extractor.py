"""
Enhanced BizGuru report extractor with more robust section detection and fallback methods.
"""

import os
import re
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BizGuruExtractor:
    """
    Specialized extractor for BizGuru reports with enhanced robustness.
    """
    
    def __init__(self):
        """Initialize the enhanced BizGuru extractor"""
        # Expanded section headers based on blueprint.md
        self.group_structure = {
            "vision": ["Vision", "Vision Statement", "Vision Statement Output"],
            "market_assessment": ["Market Assessment", "Market Segment", "Market Segment Selection", "Market Analysis"],
            "strategic_assessment": ["Strategic Assessment", "Strategy Framework", "Strategic Position"],
            "risk_assessment": ["Risk Assessment", "Risk Factors", "Risk Analysis"],
            "competitive_assessment": ["Competitive Assessment", "Competition", "Competitor Analysis"],
            "portfolio_assessment": ["Portfolio Assessment", "Product Portfolio", "Service Portfolio"],
            "strengths_assessment": ["Strengths Assessment", "Strengths", "SWOT Strengths"],
            "weaknesses_assessment": ["Weaknesses Assessment", "Weaknesses", "SWOT Weaknesses"],
            "opportunities_assessment": ["Opportunities Assessment", "Opportunities", "SWOT Opportunities"],
            "threats_assessment": ["Threats Assessment", "Threats", "SWOT Threats"],
            "revenue_growth": ["Revenue Growth", "Finance Dashboard", "Financial Growth"],
            "operating_income": ["Operating Income", "Income", "Profit"],
            "cash_flow": ["Cash Flow", "Cashflow", "Cash Management"],
            "gross_margin": ["Gross Margin", "Margin", "Profitability"],
            "finance_metrics": ["Finance Metrics", "Financial Metrics", "Finance KPIs"],
            "time_to_hire": ["Time to Hire", "Hiring Time", "Recruitment Time"],
            "employee_turnover": ["Employee Turnover", "Staff Turnover", "Attrition"],
            "employee_engagement": ["Employee Engagement", "Staff Engagement", "Workforce Engagement"],
            "diversity": ["Diversity", "Inclusion", "Workforce Diversity"],
            "hr_metrics": ["HR Metrics", "Human Resources Metrics", "Personnel Metrics"],
            "inventory_turnover": ["Inventory Turnover", "Stock Turnover", "Inventory Management"],
            "on_time_delivery": ["On Time Delivery", "Delivery Performance", "Shipping Performance"],
            "first_pass_yield": ["First Pass Yield", "Quality Rate", "Production Quality"],
            "total_cycle_time": ["Total Cycle Time", "Process Time", "Throughput Time"],
            "operations_metrics": ["Operations Metrics", "Operational KPIs", "Process Metrics"],
            "annual_recurring_revenue": ["Annual Recurring Revenue", "ARR", "Recurring Revenue"],
            "customer_acquisition_cost": ["Customer Acquisition Cost", "CAC", "Acquisition Cost"],
            "design_win": ["Design Win", "Product Design", "Design Success"],
            "sales_opportunities": ["Sales Opportunities", "Sales Pipeline", "Sales Funnel"],
            "sales_marketing_metrics": ["Sales & Marketing Metrics", "Sales KPIs", "Marketing KPIs"]
        }
        
        logger.info("BizGuru Extractor initialized")
    
    def extract_from_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured data from a BizGuru PDF report with improved robustness.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            dict: Extracted data structured according to the 30 groups
        """
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
        
        logger.info(f"Extracting data from BizGuru report: {pdf_path}")
        
        # Extract entity name from filename or content
        entity_name = self._extract_entity_name(pdf_path)
        
        # Initialize result structure
        result = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "groups": {}
        }
        
        # Add default assessment data structure with empty values
        for group_id in self.group_structure:
            result["groups"][group_id] = {
                "name": group_id.replace("_", " ").title(),
                "findings": [],
                "score": 0.5,  # Default middle score
                "risk_level": "Medium"  # Default risk level
            }
        
        # Open PDF document
        try:
            doc = fitz.open(pdf_path)
            
            # Get full text content first for fallback
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n"
            
            # Extract page titles and associate with groups
            page_groups = self._map_pages_to_groups(doc)
            
            # Process each group with improved robustness
            for group_id, section_headers in self.group_structure.items():
                # Try to extract using section headers
                group_data = self._extract_group_data(doc, group_id, section_headers, page_groups)
                
                # If not found, try to extract based on keywords
                if not group_data or len(group_data.keys()) <= 2:  # Only has name and findings
                    group_data = self._extract_by_keywords(full_text, group_id)
                
                # Add whatever we found to results
                if group_data:
                    result["groups"][group_id].update(group_data)
            
            # Try to extract numerical scores from tables
            self._extract_scores_from_tables(doc, result["groups"])
            
            # Calculate risk levels based on scores
            self._calculate_risk_levels(result["groups"])
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Error extracting data from PDF: {e}")
            
            # Still return basic structure with entity name even if errors occur
            return result
        
        return result
    
    def _extract_entity_name(self, pdf_path: str) -> str:
        """
        Extract entity name from the PDF filename or content with improved reliability.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Entity name
        """
        # Get filename without extension
        filename = os.path.basename(pdf_path)
        base_name = os.path.splitext(filename)[0]
        
        # Use filename directly if it's simple
        if base_name.lower() in ["strong", "weak", "newco", "oldco"]:
            return base_name
        
        # Try to extract from the first page
        try:
            doc = fitz.open(pdf_path)
            first_page_text = doc[0].get_text()
            doc.close()
            
            # Look for common patterns in BizGuru reports
            name_patterns = [
                r"Report for: (.*?)\n",
                r"Company: (.*?)\n",
                r"^(.*?) Business Analysis",
                r"Strategic Assessment for (.*?)\n",
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, first_page_text)
                if match:
                    return match.group(1).strip()
        except:
            pass
        
        # Fallback to filename
        return base_name
    
    def _map_pages_to_groups(self, doc: fitz.Document) -> Dict[int, str]:
        """
        Create a mapping of page numbers to likely group IDs based on page content.
        
        Args:
            doc: The PDF document
            
        Returns:
            dict: Mapping of page numbers to group IDs
        """
        page_groups = {}
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Look for headers or titles on the page
            for group_id, headers in self.group_structure.items():
                for header in headers:
                    if header in text:
                        page_groups[page_num] = group_id
                        break
                
                if page_num in page_groups:
                    break
            
            # If no direct header found, look for keywords
            if page_num not in page_groups:
                page_groups[page_num] = self._identify_group_by_keywords(text)
        
        return page_groups
    
    def _identify_group_by_keywords(self, text: str) -> str:
        """
        Identify the most likely group based on keywords in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            str: Most likely group ID or "unknown"
        """
        # Define keywords for each group
        keywords = {
            "vision": ["vision", "mission", "future", "goal", "aspiration"],
            "market_assessment": ["market", "segment", "customer", "industry", "sector"],
            "strategic_assessment": ["strategy", "strategic", "position", "competitive position"],
            "risk_assessment": ["risk", "threat", "vulnerability", "mitigation", "exposure"],
            "competitive_assessment": ["competitor", "competition", "rivalry", "market share"],
            "portfolio_assessment": ["portfolio", "product", "service", "offering"],
            "strengths_assessment": ["strength", "advantage", "capability", "asset"],
            "weaknesses_assessment": ["weakness", "disadvantage", "limitation", "gap"],
            "opportunities_assessment": ["opportunity", "potential", "prospect", "growth"],
            "threats_assessment": ["threat", "challenge", "obstacle", "barrier"],
            "revenue_growth": ["revenue", "growth", "sales", "turnover", "income"],
            "operating_income": ["operating", "income", "profit", "margin", "earnings"],
            "cash_flow": ["cash", "flow", "liquidity", "funds", "treasury"],
            "gross_margin": ["gross", "margin", "profitability", "markup"],
            "finance_metrics": ["finance", "financial", "metric", "ratio", "kpi"],
            "time_to_hire": ["time", "hire", "recruitment", "talent", "acquisition"],
            "employee_turnover": ["turnover", "retention", "attrition", "churn"],
            "employee_engagement": ["engagement", "satisfaction", "morale", "motivation"],
            "diversity": ["diversity", "inclusion", "equality", "representation"],
            "hr_metrics": ["hr", "human resources", "personnel", "workforce"],
            "inventory_turnover": ["inventory", "stock", "supplies", "goods"],
            "on_time_delivery": ["delivery", "shipment", "punctuality", "timeliness"],
            "first_pass_yield": ["yield", "quality", "defect", "pass rate"],
            "total_cycle_time": ["cycle", "time", "throughput", "process time"],
            "operations_metrics": ["operations", "operational", "process", "efficiency"],
            "annual_recurring_revenue": ["recurring", "arr", "subscription", "retention"],
            "customer_acquisition_cost": ["acquisition", "cac", "customer cost", "acquisition"],
            "design_win": ["design", "win", "product design", "engineering"],
            "sales_opportunities": ["sales", "opportunities", "pipeline", "leads"],
            "sales_marketing_metrics": ["marketing", "promotion", "advertising", "branding"]
        }
        
        # Count keyword occurrences
        keyword_counts = {group_id: 0 for group_id in keywords}
        
        text_lower = text.lower()
        for group_id, group_keywords in keywords.items():
            for keyword in group_keywords:
                keyword_counts[group_id] += text_lower.count(keyword)
        
        # Find the group with the most keyword matches
        if all(count == 0 for count in keyword_counts.values()):
            return "unknown"
        
        return max(keyword_counts.items(), key=lambda x: x[1])[0]
    
    def _extract_group_data(self, doc: fitz.Document, group_id: str, section_headers: List[str], 
                          page_groups: Dict[int, str]) -> Dict[str, Any]:
        """
        Extract data for a specific group with improved robustness.
        
        Args:
            doc: The PDF document
            group_id: ID of the group to extract
            section_headers: Possible section headers for this group
            page_groups: Mapping of page numbers to group IDs
            
        Returns:
            dict: Extracted group data or empty dict if not found
        """
        # Find pages that likely contain this group
        group_pages = [page_num for page_num, page_group in page_groups.items() 
                     if page_group == group_id]
        
        # If no dedicated pages found, look for sections in the document
        if not group_pages:
            return self._extract_by_sections(doc, group_id, section_headers)
        
        # Extract text from all relevant pages
        group_text = ""
        for page_num in group_pages:
            page = doc[page_num]
            group_text += page.get_text() + "\n"
        
        # Look for metrics and key data
        group_data = self._process_text_for_metrics(group_text, group_id)
        
        # Add raw text if we found something
        if group_data:
            group_data["raw_text"] = group_text
            
            # Extract any numerical values as potential scores
            scores = self._extract_numerical_values(group_text)
            if scores:
                # Use the average of found numerical values as a score
                avg_score = sum(scores) / len(scores)
                # Normalize to 0-1 range if needed
                if avg_score > 1:
                    normalized_score = min(1.0, avg_score / 100)
                else:
                    normalized_score = min(1.0, avg_score)
                
                group_data["score"] = normalized_score
        
        return group_data
    
    def _extract_by_sections(self, doc: fitz.Document, group_id: str, section_headers: List[str]) -> Dict[str, Any]:
        """
        Extract data by looking for section headers in the document.
        
        Args:
            doc: The PDF document
            group_id: ID of the group to extract
            section_headers: Possible section headers for this group
            
        Returns:
            dict: Extracted group data or empty dict if not found
        """
        # Search for section headers in the document
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            for header in section_headers:
                if header in text:
                    # Found a section header - extract text
                    section_text = self._extract_section_text(doc, page_num, header)
                    
                    if section_text:
                        # Process the section text
                        group_data = self._process_text_for_metrics(section_text, group_id)
                        group_data["raw_text"] = section_text
                        return group_data
        
        logger.warning(f"Group {group_id} not found in document")
        return {}
    
    def _extract_section_text(self, doc: fitz.Document, start_page: int, section_header: str) -> str:
        """
        Extract text for a section, from its header until the next section.
        
        Args:
            doc: The PDF document
            start_page: Page where the section starts
            section_header: Header text for the section
            
        Returns:
            str: Extracted section text
        """
        section_text = ""
        current_page = start_page
        in_section = False
        
        while current_page < len(doc):
            page = doc[current_page]
            text = page.get_text()
            
            if not in_section:
                # Find the section header on this page
                header_pos = text.find(section_header)
                if header_pos >= 0:
                    in_section = True
                    text = text[header_pos + len(section_header):]
            
            if in_section:
                # Check if another section starts
                for header in self._get_all_possible_headers():
                    if header != section_header and header in text:
                        # Found the next section
                        next_header_pos = text.find(header)
                        section_text += text[:next_header_pos].strip()
                        return section_text
                
                # No next section on this page, add all text
                section_text += text + "\n"
            
            current_page += 1
        
        return section_text.strip()
    
    def _get_all_possible_headers(self) -> List[str]:
        """Get a flat list of all possible section headers"""
        all_headers = []
        for headers in self.group_structure.values():
            all_headers.extend(headers)
        return all_headers
    
    def _extract_by_keywords(self, full_text: str, group_id: str) -> Dict[str, Any]:
        """
        Extract data based on keywords when section headers aren't found.
        
        Args:
            full_text: Full text of the document
            group_id: ID of the group to extract
            
        Returns:
            dict: Extracted group data
        """
        # Define keywords specific to this group
        keywords = {
            "vision": ["vision", "mission", "goal", "aspiration"],
            "market_assessment": ["market", "segment", "customer", "industry", "sector"],
            "strategic_assessment": ["strategy", "strategic", "position", "competitive position"],
            # Add keywords for all groups
        }
        
        # Get keywords for this group
        group_keywords = keywords.get(group_id, [])
        
        # Add group name components as keywords
        group_words = group_id.replace("_", " ").split()
        for word in group_words:
            if len(word) > 3 and word not in group_keywords:
                group_keywords.append(word)
        
        # Find paragraphs containing keywords
        paragraphs = full_text.split("\n\n")
        relevant_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            if any(keyword.lower() in paragraph_lower for keyword in group_keywords):
                relevant_paragraphs.append(paragraph)
        
        if not relevant_paragraphs:
            return {}
        
        # Combine relevant paragraphs
        relevant_text = "\n\n".join(relevant_paragraphs)
        
        # Process the text for metrics
        group_data = self._process_text_for_metrics(relevant_text, group_id)
        group_data["raw_text"] = relevant_text
        
        # Extract numerical values as potential scores
        scores = self._extract_numerical_values(relevant_text)
        if scores:
            # Use the average of found numerical values as a score
            avg_score = sum(scores) / len(scores)
            # Normalize to 0-1 range if needed
            if avg_score > 1:
                normalized_score = min(1.0, avg_score / 100)
            else:
                normalized_score = min(1.0, avg_score)
            
            group_data["score"] = normalized_score
        
        return group_data
    
    def _extract_numerical_values(self, text: str) -> List[float]:
        """
        Extract potential numerical values (scores, percentages) from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            list: Extracted numerical values
        """
        # Look for percentages
        percentage_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(percentage_pattern, text)
        
        # Look for scores out of 10
        score_pattern = r'(\d+(?:\.\d+)?)\s*/\s*10'
        scores_out_of_10 = re.findall(score_pattern, text)
        
        # Look for decimal values between 0 and 1
        decimal_pattern = r'(?<!\d)0\.\d+'
        decimals = re.findall(decimal_pattern, text)
        
        # Convert to float values
        values = []
        
        for p in percentages:
            try:
                values.append(float(p) / 100)  # Convert to 0-1 scale
            except ValueError:
                pass
        
        for s in scores_out_of_10:
            try:
                values.append(float(s) / 10)  # Convert to 0-1 scale
            except ValueError:
                pass
        
        for d in decimals:
            try:
                values.append(float(d))  # Already in 0-1 scale
            except ValueError:
                pass
        
        return values
    
    def _process_text_for_metrics(self, text: str, group_id: str) -> Dict[str, Any]:
        """
        Process text to extract key metrics and findings.
        
        Args:
            text: Text to process
            group_id: ID of the group
            
        Returns:
            dict: Extracted metrics and findings
        """
        # Default data structure
        group_data = {
            "name": group_id.replace("_", " ").title(),
            "findings": []
        }
        
        # Extract key metrics based on group type
        if group_id == "vision":
            # Extract vision statement
            vision_match = re.search(r"vision\s*(?:statement)?:?\s*(.*?)(?:\n|$)", text, re.IGNORECASE)
            if vision_match:
                group_data["vision_statement"] = vision_match.group(1).strip()
            
            # Extract vision scores
            score_pattern = r"(\w+)\s+score:?\s*([\d.]+)"
            scores = re.findall(score_pattern, text, re.IGNORECASE)
            for score_name, value in scores:
                try:
                    group_data[f"{score_name.lower()}_score"] = float(value)
                except:
                    pass
        
        elif group_id in ["market_assessment", "strategic_assessment"]:
            # Extract market segments
            segment_pattern = r"(?:segment|market):?\s*([\w\s]+)(?:\s*attractiveness:?\s*([\d.]+))?"
            segments = re.findall(segment_pattern, text, re.IGNORECASE)
            
            if segments:
                group_data["segments"] = []
                for segment_info in segments:
                    segment_name = segment_info[0].strip()
                    attractiveness = 0.5  # Default
                    
                    if len(segment_info) > 1 and segment_info[1]:
                        try:
                            attractiveness = float(segment_info[1])
                            # Normalize if needed
                            if attractiveness > 1:
                                attractiveness = attractiveness / 100
                        except:
                            pass
                            
                    group_data["segments"].append({
                        "name": segment_name,
                        "attractiveness": attractiveness
                    })
        
        elif group_id in ["risk_assessment", "threats_assessment"]:
            # Extract risk factors
            risk_pattern = r"(?:risk|threat):?\s*([\w\s]+)(?:\s*level:?\s*([\d.]+))?"
            risks = re.findall(risk_pattern, text, re.IGNORECASE)
            
            if risks:
                group_data["risks"] = []
                for risk_info in risks:
                    risk_name = risk_info[0].strip()
                    risk_level = 0.5  # Default
                    
                    if len(risk_info) > 1 and risk_info[1]:
                        try:
                            risk_level = float(risk_info[1])
                            # Normalize if needed
                            if risk_level > 1:
                                risk_level = risk_level / 100
                        except:
                            pass
                            
                    group_data["risks"].append({
                        "risk_type": risk_name,
                        "level": risk_level,
                        "description": risk_name
                    })
        
        # Extract any financial metrics (for financial groups)
        if any(term in group_id for term in ["revenue", "income", "cash", "margin", "finance"]):
            # Look for common financial metrics
            metric_pattern = r"(\d+(?:\.\d+)?(?:M|K|%)?)(?:\s+|\))(revenue|growth|margin|income|profit|cash flow)"
            metrics = re.findall(metric_pattern, text, re.IGNORECASE)
            
            if metrics:
                group_data["metrics"] = []
                for value, metric_name in metrics:
                    # Clean and normalize value
                    value_clean = value.strip()
                    value_numeric = self._parse_numeric_value(value_clean)
                    
                    group_data["metrics"].append({
                        "name": metric_name.strip(),
                        "value": value_numeric,
                        "raw_value": value_clean
                    })
        
        # Extract any findings, insights or conclusions
        finding_patterns = [
            r"(?:finding|insight|conclusion):?\s*(.*?)(?:\n|$)",
            r"(?:key|main)\s+(?:point|observation):?\s*(.*?)(?:\n|$)",
            r"(?:•|\*)\s*(.*?)(?:\n|$)"  # Bullet points
        ]
        
        for pattern in finding_patterns:
            findings = re.findall(pattern, text, re.IGNORECASE)
            for finding in findings:
                if isinstance(finding, str):
                    finding_text = finding.strip()
                elif isinstance(finding, tuple):
                    finding_text = finding[0].strip()
                else:
                    continue
                    
                if finding_text and len(finding_text) > 5:
                    # Avoid duplicates
                    if not any(f["description"] == finding_text for f in group_data["findings"]):
                        group_data["findings"].append({
                            "description": finding_text,
                            "type": "finding"
                        })
        
        return group_data
    
    def _parse_numeric_value(self, value_str: str) -> float:
        """
        Parse a numeric value from a string, handling K/M suffixes.
        
        Args:
            value_str: String containing a value
            
        Returns:
            float: Parsed numeric value
        """
        try:
            # Remove non-numeric chars except dots and K/M suffix
            clean_str = ''.join(c for c in value_str if c.isdigit() or c == '.' or c in 'KkMm%')
            
            # Handle suffixes
            multiplier = 1.0
            if clean_str.endswith('K') or clean_str.endswith('k'):
                multiplier = 1000.0
                clean_str = clean_str[:-1]
            elif clean_str.endswith('M') or clean_str.endswith('m'):
                multiplier = 1000000.0
                clean_str = clean_str[:-1]
            elif clean_str.endswith('%'):
                multiplier = 0.01  # Convert to decimal
                clean_str = clean_str[:-1]
                
            # Convert to float and apply multiplier
            return float(clean_str) * multiplier
        except ValueError:
            return 0.0
    
    def _extract_scores_from_tables(self, doc: fitz.Document, groups: Dict[str, Dict[str, Any]]) -> None:
        """
        Try to extract scores from tables in the document.
        
        Args:
            doc: The PDF document
            groups: Group data to update with scores
        """
        # Try to use PyMuPDF's table extraction (requires latest version)
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract tables
                tables = page.find_tables()
                if not tables:
                    continue
                
                for table in tables:
                    # Convert table to text
                    table_text = ""
                    table_dict = table.extract()
                    for row in table_dict['rows']:
                        table_text += ' '.join(str(cell) for cell in row) + "\n"
                    
                    # Look for group names and associated scores
                    for group_id, group_data in groups.items():
                        group_name = group_id.replace('_', ' ')
                        if group_name.lower() in table_text.lower():
                            # Look for scores in the same row
                            scores = self._extract_numerical_values(table_text)
                            if scores:
                                # Use the largest score (often the important one)
                                max_score = max(scores)
                                if max_score > 1:
                                    normalized_score = min(1.0, max_score / 100)
                                else:
                                    normalized_score = min(1.0, max_score)
                                
                                group_data["score"] = normalized_score
        except:
            # Table extraction might not work if using older PyMuPDF
            pass
    
    def _calculate_risk_levels(self, groups: Dict[str, Dict[str, Any]]) -> None:
        """
        Calculate risk levels based on scores.
        
        Args:
            groups: Group data to update with risk levels
        """
        for group_id, group_data in groups.items():
            score = group_data.get("score", 0.5)
            
            # Invert score for risk calculation (higher score = lower risk)
            # Score is 0-1, with 1 being the best performance
            if "risk" in group_id or "threat" in group_id:
                # For direct risk groups, higher score means higher risk
                risk_score = score
            else:
                # For other groups, higher score means lower risk
                risk_score = 1.0 - score
            
            # Determine risk level
            if risk_score < 0.3:
                group_data["risk_level"] = "Low"
            elif risk_score < 0.7:
                group_data["risk_level"] = "Medium"
            else:
                group_data["risk_level"] = "High"