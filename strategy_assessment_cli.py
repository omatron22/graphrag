# strategy_assessment_cli.py
"""
Command-line interface for the Strategy Assessment Framework.
Provides an interactive interface for running strategy assessments.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

from knowledge_graph.neo4j_manager import Neo4jManager
from analysis.risk_engine import RiskAnalyzer
from analysis.strategy_generator import StrategyGenerator
from strategy_assessment import StrategyAssessment
from assessment_pdf_generator import AssessmentPDFGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrategyAssessmentCLI:
    """
    Command-line interface for the Strategy Assessment Framework.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        # Initialize Neo4j connection
        self.neo4j_manager = Neo4jManager()
        self.neo4j_manager.connect()
        
        # Initialize components
        self.risk_analyzer = RiskAnalyzer(self.neo4j_manager)
        self.strategy_generator = StrategyGenerator(self.neo4j_manager, self.risk_analyzer)
        self.assessment_framework = StrategyAssessment(self.neo4j_manager, self.risk_analyzer, self.strategy_generator)
        self.pdf_generator = AssessmentPDFGenerator()
        
        logger.info("Strategy Assessment CLI initialized")
    
    def run_interactive(self):
        """Run the CLI in interactive mode."""
        print("\n" + "="*80)
        print(" Business Strategy Assessment Framework ".center(80, "="))
        print("="*80 + "\n")
        
        while True:
            print("\nMain Menu:")
            print("1. Run new strategy assessment")
            print("2. View existing assessments")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                self._run_new_assessment()
            elif choice == "2":
                self._view_existing_assessments()
            elif choice == "3":
                print("\nExiting the Strategy Assessment Framework. Goodbye!")
                self.neo4j_manager.close()
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 3.")
    
    def _run_new_assessment(self):
        """Run a new strategy assessment."""
        print("\n" + "-"*80)
        print(" New Strategy Assessment ".center(80, "-"))
        print("-"*80 + "\n")
        
        # Step 1: Select entity to assess
        entity = self._select_entity()
        if not entity:
            return
        
        # Step 2: Get user inputs
        user_inputs = self._collect_user_inputs()
        
        # Step 3: Run assessment
        print(f"\nRunning strategy assessment for {entity}...")
        print("This may take a few minutes. Please wait...\n")
        
        assessment_results = self.assessment_framework.assess(entity, user_inputs)
        
        # Step 4: Generate charts
        charts = self.assessment_framework.generate_charts(assessment_results)
        
        # Step 5: Generate PDF report
        print("\nGenerating assessment report...")
        pdf_path = self.pdf_generator.generate_assessment_pdf(assessment_results, charts)
        
        # Step 6: Show results summary
        self._display_results_summary(assessment_results)
        
        print(f"\nAssessment complete! Report saved to: {pdf_path}")
    
    def _select_entity(self) -> Optional[str]:
        """
        Select an entity to assess.
        
        Returns:
            str: Selected entity name, or None if cancelled
        """
        print("\nStep 1: Select Entity to Assess\n")
        
        # Query Neo4j for available entities
        entities = self._get_available_entities()
        
        if not entities:
            print("No entities found in the knowledge graph.")
            print("Please process some documents first to populate the graph.")
            return None
        
        # Display available entities
        print("Available entities:")
        for i, entity in enumerate(entities):
            print(f"{i+1}. {entity['name']} ({entity['connections']} connections)")
        
        print("\nEnter entity number, or 'c' to cancel, or 'n' to enter a new entity name:")
        choice = input("> ").strip()
        
        if choice.lower() == 'c':
            print("Assessment cancelled.")
            return None
        elif choice.lower() == 'n':
            # Enter new entity name
            new_entity = input("Enter new entity name: ").strip()
            if new_entity:
                return new_entity
            else:
                print("Invalid entity name.")
                return None
        else:
            # Select from list
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entities):
                    return entities[idx]["name"]
                else:
                    print("Invalid selection.")
                    return None
            except ValueError:
                print("Invalid input.")
                return None
    
    def _get_available_entities(self) -> List[Dict[str, Any]]:
        """
        Get available entities from Neo4j.
    
        Returns:
            list: Available entities with their connection counts
        """
        query = """
        MATCH (e:Entity)
        WITH e, size([(e)--() | 1]) AS connections
        WHERE connections > 0
        RETURN e.name AS name, connections
        ORDER BY connections DESC
        LIMIT 20
        """
    
        return self.neo4j_manager.execute_query(query)
    
    def _collect_user_inputs(self) -> Dict[str, Any]:
        """
        Collect user inputs for the assessment.
        
        Returns:
            dict: User inputs
        """
        print("\nStep 2: Provide Assessment Inputs\n")
        
        # Risk tolerance
        print("Select risk tolerance level:")
        print("1. Low - Conservative approach, prioritizing risk mitigation")
        print("2. Medium - Balanced approach")
        print("3. High - Aggressive approach, prioritizing growth opportunities")
        
        risk_choice = input("Enter choice (1-3, default 2): ").strip() or "2"
        risk_mapping = {"1": "Low", "2": "Medium", "3": "High"}
        risk_tolerance = risk_mapping.get(risk_choice, "Medium")
        
        # Priorities
        print("\nSelect priority areas (comma-separated numbers):")
        print("1. Vision - Clear and inspiring future focus")
        print("2. Market - Position in attractive market segments")
        print("3. Strategic - Overall strategic positioning")
        print("4. Risk - Risk management and mitigation")
        print("5. Competitive - Competitive advantages and positioning")
        print("6. Financial - Financial metrics and performance")
        print("7. Operational - Operational efficiency and excellence")
        
        priority_choice = input("Enter priorities (e.g., 1,3,5): ").strip()
        priority_mapping = {
            "1": "vision",
            "2": "market",
            "3": "strategic",
            "4": "risk",
            "5": "competitive",
            "6": "finance",
            "7": "operations"
        }
        
        priorities = []
        if priority_choice:
            for p in priority_choice.split(","):
                p = p.strip()
                if p in priority_mapping:
                    priorities.append(priority_mapping[p])
        
        # Constraints
        print("\nEnter constraints (one per line, blank line to finish):")
        print("Examples: Limited resources, Regulatory requirements, Time constraints")
        
        constraints = []
        while True:
            constraint = input("> ").strip()
            if not constraint:
                break
            constraints.append(constraint)
        
        # Combine inputs
        user_inputs = {
            "risk_tolerance": risk_tolerance,
            "priorities": priorities,
            "constraints": constraints
        }
        
        print("\nInputs collected:")
        print(f"Risk Tolerance: {risk_tolerance}")
        print(f"Priorities: {', '.join(priorities) if priorities else 'None specified'}")
        print(f"Constraints: {', '.join(constraints) if constraints else 'None specified'}")
        
        return user_inputs
    
    def _display_results_summary(self, assessment_results: Dict[str, Any]):
        """
        Display a summary of assessment results.
        
        Args:
            assessment_results: Assessment results
        """
        print("\n" + "-"*80)
        print(" Assessment Results Summary ".center(80, "-"))
        print("-"*80 + "\n")
        
        entity_name = assessment_results.get("entity", "Unknown Entity")
        print(f"Entity: {entity_name}")
        
        # Summary stats
        summary = assessment_results.get("summary", {})
        overall_score = summary.get("overall_score", 0.5)
        risk_level = summary.get("risk_level", "Medium")
        
        score_display = f"{overall_score * 100:.1f}%"
        print(f"Overall Score: {score_display}")
        print(f"Risk Level: {risk_level}")
        
        # Key insights
        print("\nKey Insights:")
        for insight in summary.get("key_insights", []):
            print(f"• {insight}")
        
        # Top recommendations
        print("\nTop Strategic Recommendations:")
        recommendations = assessment_results.get("recommendations", [])
        for i, rec in enumerate(recommendations[:3]):  # Top 3 recommendations
            title = rec.get("title", "")
            priority = rec.get("priority", "medium").capitalize()
            timeline = rec.get("timeline", "medium").capitalize()
            
            print(f"{i+1}. {title}")
            print(f"   Priority: {priority} | Timeline: {timeline}")
            if rec.get("rationale"):
                print(f"   Rationale: {rec.get('rationale')}")
        
        # Areas of concern
        concern_areas = summary.get("concern_areas", [])
        if concern_areas:
            print("\nAreas of Concern:")
            for area in concern_areas:
                area_name = assessment_results.get("groups", {}).get(area, {}).get("name", area.capitalize())
                print(f"• {area_name}")
    
    def _view_existing_assessments(self):
        """View existing assessment reports."""
        print("\n" + "-"*80)
        print(" Existing Assessment Reports ".center(80, "-"))
        print("-"*80 + "\n")
        
        # Check for assessment files
        assessment_dir = os.path.join("data", "knowledge_base", "assessments")
        if not os.path.exists(assessment_dir):
            print("No assessment reports found.")
            return
        
        # Get list of assessment files
        assessment_files = []
        for filename in os.listdir(assessment_dir):
            if filename.startswith("assessment_") and filename.endswith(".json"):
                file_path = os.path.join(assessment_dir, filename)
                file_time = os.path.getmtime(file_path)
                assessment_files.append((filename, file_path, file_time))
        
        if not assessment_files:
            print("No assessment reports found.")
            return
        
        # Sort by modification time (newest first)
        assessment_files.sort(key=lambda x: x[2], reverse=True)
        
        # Display files
        print("Available assessment reports:")
        for i, (filename, file_path, file_time) in enumerate(assessment_files):
            # Extract entity name from filename
            # Format: assessment_entity_timestamp.json
            parts = filename.split("_")
            if len(parts) >= 2:
                entity_name = parts[1]
            else:
                entity_name = "Unknown"
            
            # Format timestamp
            timestamp = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{i+1}. {entity_name} - {timestamp}")
        
        # Let user select a file to view
        print("\nEnter report number to view details, or 'c' to cancel:")
        choice = input("> ").strip()
        
        if choice.lower() == 'c':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(assessment_files):
                self._display_assessment_report(assessment_files[idx][1])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    
    
    def _determine_risk_level(self, score: float, risk_tolerance: str) -> str:
        """
        Determine risk level based on score and tolerance.
    
        Args:
            score: Group score between 0.0 and 1.0
            risk_tolerance: User's risk tolerance (Low, Medium, High)
        
        Returns:
            str: Risk level (Low, Medium, High)
        """
        # Adjust thresholds based on risk tolerance
        if risk_tolerance == "Low":
            # Conservative thresholds
            if score >= 0.7:
                return "Low"
            elif score >= 0.4:
                return "Medium"
            else:
                return "High"
        elif risk_tolerance == "High":
            # Aggressive thresholds
            if score >= 0.6:
                return "Low"
            elif score >= 0.3:
                return "Medium"
            else:
                return "High"
        else:
            # Medium tolerance (default)
            if score >= 0.65:
                return "Low"
            elif score >= 0.35:
                return "Medium"
            else:
                return "High"
        
    def _display_assessment_report(self, file_path: str):
        """
        Display an assessment report.
        
        Args:
            file_path: Path to the assessment report file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                assessment_results = json.load(f)
            
            self._display_results_summary(assessment_results)
            
            print("\nPress Enter to return to the main menu.")
            input()
            
        except Exception as e:
            logger.error(f"Error loading assessment report: {e}")
            print(f"Error loading assessment report: {e}")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Business Strategy Assessment Framework CLI")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--entity", "-e", help="Entity to assess")
    parser.add_argument("--risk", "-r", choices=["Low", "Medium", "High"], default="Medium", help="Risk tolerance")
    parser.add_argument("--priorities", "-p", help="Comma-separated priorities")
    parser.add_argument("--constraints", "-c", help="Comma-separated constraints")
    parser.add_argument("--output", "-o", help="Output directory for reports")
    
    args = parser.parse_args()
    
    # Create CLI
    cli = StrategyAssessmentCLI()
    
    # Run in appropriate mode
    if args.interactive or not args.entity:
        # Interactive mode
        try:
            cli.run_interactive()
        except KeyboardInterrupt:
            print("\n\nExiting the Strategy Assessment Framework. Goodbye!")
            cli.neo4j_manager.close()
    else:
        # Command-line mode
        entity = args.entity
        
        # Parse inputs
        user_inputs = {
            "risk_tolerance": args.risk,
            "priorities": args.priorities.split(",") if args.priorities else [],
            "constraints": args.constraints.split(",") if args.constraints else []
        }
        
        # Run assessment
        print(f"Running strategy assessment for {entity}...")
        assessment_results = cli.assessment_framework.assess(entity, user_inputs)
        
        # Generate charts
        charts = cli.assessment_framework.generate_charts(assessment_results)
        
        # Generate PDF report
        print("Generating assessment report...")
        pdf_path = cli.pdf_generator.generate_assessment_pdf(assessment_results, charts)
        
        # Show results summary
        cli._display_results_summary(assessment_results)
        
        print(f"\nAssessment complete! Report saved to: {pdf_path}")
        
        # Cleanup
        cli.neo4j_manager.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())