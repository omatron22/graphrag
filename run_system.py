#!/usr/bin/env python3
"""
Knowledge Graph-Based Business Consulting System Runner

This script provides a command-line interface to run the knowledge graph-based 
business consulting system. It allows users to analyze companies with different
risk profiles and generate strategic recommendations.
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from orchestrator import Orchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_system")

def print_banner():
    """Print the system banner"""
    print("\n" + "="*80)
    print(" Knowledge Graph-Based Business Consulting System ".center(80, "="))
    print("="*80 + "\n")
    print(" A complete offline business risk analysis system using knowledge graphs.")
    print(" Processes documents, extracts insights, and generates recommendations.")
    print("\n" + "="*80 + "\n")

def list_entities(orchestrator):
    """List top entities in the knowledge graph"""
    try:
        query = """
        MATCH (e:Entity)
        RETURN e.name AS name, COUNT { (e)--() } AS connections
        ORDER BY connections DESC
        LIMIT 20
        """
        
        entities = orchestrator.neo4j_manager.execute_query(query)
        return entities
    except Exception as e:
        logger.error(f"Error listing entities: {e}")
        return []

def analyze_entity(orchestrator, entity_name, user_inputs=None):
    """Analyze an entity and display results"""
    print(f"\nAnalyzing entity: {entity_name}")
    
    # Display user inputs if provided
    if user_inputs:
        print(f"Risk Tolerance: {user_inputs.get('risk_tolerance', 'Medium')}")
        if user_inputs.get('priorities'):
            print(f"Priorities: {', '.join(user_inputs.get('priorities', []))}")
        if user_inputs.get('constraints'):
            print(f"Constraints: {', '.join(user_inputs.get('constraints', []))}")
    
    print("This may take a few minutes. Please wait...\n")
    
    start_time = time.time()
    
    # Use run_strategy_assessment if user_inputs are provided, otherwise use generate_analysis_report
    if user_inputs:
        result = orchestrator.run_strategy_assessment(entity_name, user_inputs)
        report = result.get("assessment_results", {})
    else:
        report = orchestrator.generate_analysis_report(entity_name)
    
    end_time = time.time()
    
    print(f"\nEntity analysis completed in {end_time - start_time:.2f} seconds.")
    
    if "error" not in report:
        print("Status: ✅ Complete")
        
        # Print risk summary
        risks = report.get("risks", {}).get("categories", {})
        if risks:
            print("\nRisk Assessment:")
            for risk_type, level in risks.items():
                if risk_type != "reasoning":
                    print(f"  - {risk_type.capitalize()}: {level}")
        
        # Print top strategies
        if user_inputs:
            strategies = report.get("recommendations", [])
        else:
            strategies = report.get("strategies", [])
            
        if isinstance(strategies, list) and strategies:
            print("\nTop Strategies:")
            for i, strategy in enumerate(strategies[:min(3, len(strategies))]):
                print(f"  {i+1}. {strategy.get('title')} (Priority: {strategy.get('priority', 'medium')})")
        else:
            print("\nNo strategies available or invalid format.")
        
        # Print report paths
        if "report_path" in report:
            print(f"\nFull JSON report saved to: {report.get('report_path')}")
        
        # Show PDF path information
        pdf_path = report.get("pdf_path")
        if not pdf_path and isinstance(result, dict):
            pdf_path = result.get("pdf_path")
            
        if pdf_path:
            print(f"\nDetailed PDF report saved to: {pdf_path}")
        
        return report
    else:
        print("Status: ❌ Failed")
        print(f"Error: {report.get('error')}")
        return report

def simplified_interactive_mode():
    """Run a simplified interactive mode focused on strategy assessment"""
    print_banner()
    
    print("Initializing system components...")
    orchestrator = Orchestrator()
    
    try:
        while True:
            # Show available entities
            entities = list_entities(orchestrator)
            
            if not entities:
                print("\nNo entities found in knowledge graph.")
                print("Please run the system with --list-entities to check available entities.")
                break
            
            print("\nAvailable Companies:")
            print(f"{'#':<3} {'Company Name':<40} {'Connections':<10}")
            print("-"*60)
            
            for i, entity in enumerate(entities):
                print(f"{i+1:<3} {entity.get('name', 'Unknown'):<40} {entity.get('connections', 0):<10}")
            
            print("\n0. Exit")
            
            # Select entity
            entity_choice = input("\nSelect company to analyze (enter number or 0 to exit): ").strip()
            
            if entity_choice == "0":
                break
                
            try:
                entity_idx = int(entity_choice) - 1
                if 0 <= entity_idx < len(entities):
                    entity_name = entities[entity_idx].get("name")
                else:
                    print("Invalid selection. Please try again.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            
            # Risk tolerance selection
            print("\nSelect risk tolerance level:")
            print("1. Low - Conservative approach")
            print("2. Medium - Balanced approach")
            print("3. High - Aggressive approach")

            risk_choice = input("Enter choice (1-3, default 2): ").strip() or "2"
            risk_mapping = {"1": "Low", "2": "Medium", "3": "High"}
            risk_tolerance = risk_mapping.get(risk_choice, "Medium")

            # Get priorities
            print("\nEnter business priorities (comma-separated, e.g., market,finance,operations):")
            priorities_input = input("> ").strip()
            priorities = [p.strip() for p in priorities_input.split(",")] if priorities_input else []

            # Get constraints
            print("\nEnter business constraints (comma-separated, e.g., budget,timeline,resources):")
            constraints_input = input("> ").strip()
            constraints = [c.strip() for c in constraints_input.split(",")] if constraints_input else []

            # Create user inputs
            user_inputs = {
                "risk_tolerance": risk_tolerance,
                "priorities": priorities,
                "constraints": constraints
            }

            # Run analysis
            analyze_entity(orchestrator, entity_name, user_inputs)
            
            # Ask if user wants to continue
            print("\n")
            choice = input("Press Enter to continue or 'q' to quit: ").strip().lower()
            if choice == 'q':
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up and exiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        print("Cleaning up resources...")
        orchestrator.cleanup()
        print("System shutdown complete.")

def main():
    """Main entry point for the system"""
    parser = argparse.ArgumentParser(description="Knowledge Graph Business Consulting System Runner")
    parser.add_argument("--analyze", "-a", help="Analyze an entity", default=None)
    parser.add_argument("--risk-tolerance", "-r", choices=["low", "medium", "high"], 
                      help="Risk tolerance (low, medium, high)", default="medium")
    parser.add_argument("--priorities", "-p", help="Comma-separated list of priorities (e.g., market,finance)", default="")
    parser.add_argument("--constraints", "-c", help="Comma-separated list of constraints", default="")
    parser.add_argument("--list-entities", "-e", action="store_true", help="List top entities in knowledge graph")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in simplified interactive mode")
    parser.add_argument("--process-doc", help="Process a document file (advanced)", default=None)
    parser.add_argument("--visualize", "-v", help="Visualize an entity network (advanced)", default=None)
    parser.add_argument("--depth", "-d", type=int, help="Network depth for visualization", default=2)
    
    args = parser.parse_args()
    
    # If no arguments provided, default to interactive mode
    if len(sys.argv) == 1:
        args.interactive = True
    
    if args.interactive:
        simplified_interactive_mode()
        return 0
    
    # Non-interactive mode
    print_banner()
    
    orchestrator = Orchestrator()
    
    try:
        if args.list_entities:
            entities = list_entities(orchestrator)
            
            if entities:
                print("\nAvailable companies in knowledge graph:")
                print(f"{'#':<3} {'Company Name':<40} {'Connections':<10}")
                print("-"*60)
                
                for i, entity in enumerate(entities):
                    print(f"{i+1:<3} {entity.get('name', 'Unknown'):<40} {entity.get('connections', 0):<10}")
            else:
                print("\nNo companies found in knowledge graph.")
        
        if args.analyze:
            entity_name = args.analyze
            
            # Parse user inputs if provided
            priorities = [p.strip() for p in args.priorities.split(",")] if args.priorities else []
            constraints = [c.strip() for c in args.constraints.split(",")] if args.constraints else []
            
            user_inputs = {
                "risk_tolerance": args.risk_tolerance.capitalize(),
                "priorities": priorities,
                "constraints": constraints
            }
            
            # Only pass user_inputs if any non-default values were provided
            if args.risk_tolerance != "medium" or priorities or constraints:
                analyze_entity(orchestrator, entity_name, user_inputs)
            else:
                analyze_entity(orchestrator, entity_name)
        
        # Advanced options (kept for backward compatibility)
        if args.process_doc:
            file_path = args.process_doc
            if os.path.isfile(file_path):
                print(f"\nProcessing document: {file_path}")
                result = orchestrator.process_document(file_path)
                if result.get("status") == "complete":
                    print("Document processing completed successfully.")
            else:
                print(f"Error: File not found: {file_path}")
        
        if args.visualize:
            entity_name = args.visualize
            depth = args.depth
            print(f"\nVisualizing entity network: {entity_name}")
            viz = orchestrator.visualize_entity_network(entity_name, depth)
            if "error" not in viz:
                print(f"Visualization saved to: {viz.get('visualization_path')}")
        
        orchestrator.cleanup()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up and exiting...")
        orchestrator.cleanup()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        orchestrator.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())