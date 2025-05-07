#!/usr/bin/env python3
"""
Knowledge Graph-Based Business Consulting System Runner with Qmirac Engine Guidelines
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
    print(" Qmirac Engine - Business Strategy Assessment ".center(80, "="))
    print("="*80 + "\n")
    print(" A complete business strategy assessment system using knowledge graphs.")
    print(" Processes 30 assessment areas and generates strategic recommendations.")
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

def run_qmirac_assessment(orchestrator, entity_name, user_inputs):
    """Run Qmirac assessment and display results"""
    print(f"\nRunning Qmirac assessment for: {entity_name}")
    
    # Display user inputs
    print(f"Risk Tolerance: {user_inputs.get('risk_tolerance', 'Medium')}")
    if user_inputs.get('priorities'):
        print(f"Priorities: {', '.join(user_inputs.get('priorities', []))}")
    if user_inputs.get('constraints'):
        print(f"Constraints: {', '.join(user_inputs.get('constraints', []))}")
    
    print("Processing 30 assessment areas. This may take a few minutes. Please wait...\n")
    
    start_time = time.time()
    
    # Run the Qmirac assessment
    result = orchestrator.run_qmirac_assessment(entity_name, user_inputs)
    
    end_time = time.time()
    
    print(f"\nQmirac assessment completed in {end_time - start_time:.2f} seconds.")
    
    if "assessment_results" in result:
        print("Status: ✅ Complete")
        
        # Print risk summary
        risk_level = user_inputs.get("risk_tolerance", "Medium")
        print(f"\nRisk Tolerance Level: {risk_level}")
        
        # Print risk assessment results if available
        if "risk_summary" in result["assessment_results"]:
            risk_summary = result["assessment_results"]["risk_summary"]
            print("\nRisk Assessment:")
            for risk_type, level in risk_summary.items():
                if risk_type != "reasoning":
                    print(f"  - {risk_type.capitalize()}: {level}")
        
        # Print top 3 recommendations if available
        if "recommendations" in result["assessment_results"]:
            recommendations = result["assessment_results"]["recommendations"]
            if recommendations:
                print("\nTop Recommendations:")
                for i, rec in enumerate(recommendations[:3]):
                    print(f"  {i+1}. {rec.get('title')} (Priority: {rec.get('priority', 'Medium')})")
        
        # Print generated PDF paths
        if "pdf_paths" in result:
            print("\nGenerated PDF Reports:")
            for path in result["pdf_paths"]:
                print(f"  - {path}")
        
        return result
    else:
        print("Status: ❌ Failed")
        print(f"Error: {result.get('error', 'Unknown error occurred')}")
        return result

def simplified_interactive_mode():
    """Run a simplified interactive mode focused on Qmirac assessment"""
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
            
            # User Input Chat 1: Risk Tolerance (H/M/L)
            print("\nUser Input Chat 1: Select risk tolerance level (H/M/L):")
            print("H - High risk tolerance (aggressive approach)")
            print("M - Medium risk tolerance (balanced approach)")
            print("L - Low risk tolerance (conservative approach)")

            risk_choice = input("Enter choice (H/M/L, default M): ").strip().upper() or "M"
            risk_tolerance = {"H": "High", "M": "Medium", "L": "Low"}.get(risk_choice, "Medium")

            # User Input Chat 2: Priorities
            print("\nUser Input Chat 2: Enter business priorities (comma-separated):")
            print("Example: market growth, revenue, customer acquisition")
            priorities_input = input("> ").strip()
            priorities = [p.strip() for p in priorities_input.split(",")] if priorities_input else []

            # User Input Chat 3: Constraints
            print("\nUser Input Chat 3: Enter business constraints (comma-separated):")
            print("Example: budget limitations, timeline restrictions, resource availability")
            constraints_input = input("> ").strip()
            constraints = [c.strip() for c in constraints_input.split(",")] if constraints_input else []

            # Create user inputs
            user_inputs = {
                "risk_tolerance": risk_tolerance,
                "priorities": priorities,
                "constraints": constraints
            }

            # Run Qmirac assessment
            run_qmirac_assessment(orchestrator, entity_name, user_inputs)
            
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
    parser = argparse.ArgumentParser(description="Qmirac Engine - Business Strategy Assessment")
    parser.add_argument("--analyze", "-a", help="Analyze an entity", default=None)
    parser.add_argument("--risk-tolerance", "-r", choices=["H", "M", "L", "high", "medium", "low"], 
                      help="Risk tolerance (H/M/L)", default="M")
    parser.add_argument("--priorities", "-p", help="Comma-separated list of priorities", default="")
    parser.add_argument("--constraints", "-c", help="Comma-separated list of constraints", default="")
    parser.add_argument("--list-entities", "-e", action="store_true", help="List top entities in knowledge graph")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in simplified interactive mode")
    parser.add_argument("--populate-test", action="store_true", help="Populate with Qmirac test data")
    parser.add_argument("--process-reports", action="store_true", 
                  help="Process BizGuru reports if available, otherwise use test data")
    
    args = parser.parse_args()
    
    # If no arguments provided, default to interactive mode
    if len(sys.argv) == 1:
        args.interactive = True
    
    # Handle populate test data option
    if args.populate_test:
        print("Populating system with Qmirac test data...")
        import populate_test_data
        success = populate_test_data.populate_test_data()
        if success:
            print("Test data populated successfully.")
        else:
            print("Error populating test data.")
        return 0
    
    # Normal system operation
    if args.interactive:
        simplified_interactive_mode()
        return 0
    
    if args.process_reports:
        import process_bizguru_reports
        result = process_bizguru_reports.main()
        return result

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
            
            # Process risk tolerance input (convert to full name if needed)
            risk_tolerance = args.risk_tolerance.upper()
            if risk_tolerance in ["H", "HIGH"]:
                risk_tolerance = "High"
            elif risk_tolerance in ["M", "MEDIUM"]:
                risk_tolerance = "Medium" 
            elif risk_tolerance in ["L", "LOW"]:
                risk_tolerance = "Low"
            
            # Parse priorities and constraints
            priorities = [p.strip() for p in args.priorities.split(",")] if args.priorities else []
            constraints = [c.strip() for c in args.constraints.split(",")] if args.constraints else []
            
            # Create user inputs
            user_inputs = {
                "risk_tolerance": risk_tolerance,
                "priorities": priorities,
                "constraints": constraints
            }
            
            # Run Qmirac assessment
            run_qmirac_assessment(orchestrator, entity_name, user_inputs)
        
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