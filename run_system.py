#!/usr/bin/env python3
"""
Knowledge Graph-Based Business Consulting System Runner

This script provides a command-line interface to run the knowledge graph-based 
business consulting system. It allows users to process documents, analyze entities,
and visualize networks.
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

def list_documents():
    """List available documents in the upload directory"""
    upload_dir = os.path.join("data", "uploads")
    
    if not os.path.exists(upload_dir):
        print("Upload directory not found. Creating it now...")
        os.makedirs(upload_dir, exist_ok=True)
        return []
    
    documents = []
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(filename)[1].lower()[1:]
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")
            documents.append((filename, file_ext, size, modified))
    
    return documents

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

def process_document(orchestrator, file_path):
    """Process a document and display results"""
    print(f"\nProcessing document: {file_path}")
    print("This may take a few minutes. Please wait...\n")
    
    start_time = time.time()
    result = orchestrator.process_document(file_path)
    end_time = time.time()
    
    print(f"\nDocument processing completed in {end_time - start_time:.2f} seconds.")
    
    if result.get("status") == "complete":
        print("Status: ✅ Complete")
        
        if result.get("primary_entities"):
            print("\nPrimary entities found:")
            for entity in result.get("primary_entities"):
                print(f"  - {entity}")
        else:
            print("\nNo primary entities found in the document.")
        
        return result
    elif result.get("status") == "partial":
        print("Status: ⚠️ Partial completion")
        print(f"Error: {result.get('analysis_error', 'Unknown error')}")
        return result
    else:
        print("Status: ❌ Failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return result

def analyze_entity(orchestrator, entity_name):
    """Analyze an entity and display results"""
    print(f"\nAnalyzing entity: {entity_name}")
    print("This may take a few minutes. Please wait...\n")
    
    start_time = time.time()
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
        
        # Add this line to show PDF path information
        if "pdf_path" in report:
            print(f"\nDetailed PDF report saved to: {report.get('pdf_path')}")
        
        return report
    else:
        print("Status: ❌ Failed")
        print(f"Error: {report.get('error')}")
        return report

def visualize_entity(orchestrator, entity_name, depth=2):
    """Visualize an entity network and display results"""
    print(f"\nGenerating visualization for entity: {entity_name} (depth: {depth})")
    print("This may take a few minutes for complex networks. Please wait...\n")
    
    start_time = time.time()
    viz = orchestrator.visualize_entity_network(entity_name, depth)
    end_time = time.time()
    
    print(f"\nVisualization completed in {end_time - start_time:.2f} seconds.")
    
    if "error" not in viz:
        print("Status: ✅ Complete")
        print(f"Network contains {len(viz.get('nodes', []))} nodes and {len(viz.get('links', []))} relationships")
        
        if "visualization_path" in viz:
            print(f"\nVisualization data saved to: {viz.get('visualization_path')}")
            print("You can use this JSON file with visualization tools like D3.js or Gephi")
        
        return viz
    else:
        print("Status: ❌ Failed")
        print(f"Error: {viz.get('error')}")
        return viz

def interactive_mode():
    """Run the system in interactive mode"""
    print_banner()
    
    print("Initializing system components...")
    orchestrator = Orchestrator()
    
    try:
        while True:
            print("\n" + "="*50)
            print("Main Menu".center(50))
            print("="*50)
            print("1. Process a document")
            print("2. List available documents")
            print("3. List top entities in knowledge graph")
            print("4. Analyze an entity")
            print("5. Visualize entity network")
            print("6. Run strategy assessment")
            print("7. Exit system")
            print("-"*50)
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                # Process a document
                documents = list_documents()
                
                if not documents:
                    print("\nNo documents found in uploads directory.")
                    print("Please add documents to 'data/uploads/' directory first.")
                    continue
                
                print("\nAvailable documents:")
                for i, (name, ext, size, modified) in enumerate(documents):
                    print(f"{i+1}. {name} ({ext.upper()}, {size/1024:.1f} KB, {modified})")
                
                doc_choice = input("\nEnter document number to process (or 'c' to cancel): ").strip()
                
                if doc_choice.lower() == 'c':
                    continue
                    
                try:
                    doc_idx = int(doc_choice) - 1
                    if 0 <= doc_idx < len(documents):
                        doc_name = documents[doc_idx][0]
                        doc_path = os.path.join("data", "uploads", doc_name)
                        process_document(orchestrator, doc_path)
                    else:
                        print("Invalid document number.")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == "2":
                # List documents
                documents = list_documents()
                
                if documents:
                    print("\nAvailable documents in uploads directory:")
                    print(f"{'#':<3} {'Filename':<40} {'Type':<8} {'Size':<10} {'Modified':<20}")
                    print("-"*80)
                    
                    for i, (name, ext, size, modified) in enumerate(documents):
                        print(f"{i+1:<3} {name:<40} {ext.upper():<8} {size/1024:.1f} KB {modified:<20}")
                else:
                    print("\nNo documents found in uploads directory.")
                    print("Please add documents to 'data/uploads/' directory.")
            
            elif choice == "3":
                # List entities
                entities = list_entities(orchestrator)
                
                if entities:
                    print("\nTop entities in knowledge graph:")
                    print(f"{'#':<3} {'Entity Name':<40} {'Connections':<10}")
                    print("-"*60)
                    
                    for i, entity in enumerate(entities):
                        print(f"{i+1:<3} {entity.get('name', 'Unknown'):<40} {entity.get('connections', 0):<10}")
                else:
                    print("\nNo entities found in knowledge graph.")
                    print("Process some documents first to populate the graph.")
            
            elif choice == "4":
                # Analyze entity
                entity_name = input("\nEnter entity name to analyze: ").strip()
                
                if entity_name:
                    analyze_entity(orchestrator, entity_name)
                else:
                    print("Please enter a valid entity name.")
            
            elif choice == "5":
                # Visualize entity network
                entity_name = input("\nEnter entity name to visualize: ").strip()
                
                if not entity_name:
                    print("Please enter a valid entity name.")
                    continue
                
                depth_input = input("Enter network depth (1-3, default is 2): ").strip()
                
                try:
                    depth = int(depth_input) if depth_input else 2
                    # Limit depth to avoid performance issues
                    depth = min(max(depth, 1), 3)
                except ValueError:
                    depth = 2
                    print("Using default depth: 2")
                
                visualize_entity(orchestrator, entity_name, depth)
            
            elif choice == "6":
                # Run strategy assessment
                print("\nStrategy Assessment")
    
                # Step 1: Select entity
                entities = list_entities(orchestrator)
    
                if not entities:
                    print("\nNo entities found in knowledge graph.")
                    print("Process some documents first to populate the graph.")
                    continue
    
                print("\nSelect an entity to assess:")
                for i, entity in enumerate(entities):
                    print(f"{i+1}. {entity.get('name', 'Unknown')}")
    
                entity_choice = input("\nEnter entity number, or 'c' to cancel: ").strip()
    
                if entity_choice.lower() == 'c':
                    continue
        
                try:
                    entity_idx = int(entity_choice) - 1
                    if 0 <= entity_idx < len(entities):
                        entity_name = entities[entity_idx].get("name")
                    else:
                        print("Invalid selection.")
                        continue
                except ValueError:
                    print("Please enter a valid number.")
                    continue
    
                # Step 2: Get user inputs
                print("\nSelect risk tolerance level:")
                print("1. Low - Conservative approach")
                print("2. Medium - Balanced approach")
                print("3. High - Aggressive approach")
    
                risk_choice = input("Enter choice (1-3, default 2): ").strip() or "2"
                risk_mapping = {"1": "Low", "2": "Medium", "3": "High"}
                risk_tolerance = risk_mapping.get(risk_choice, "Medium")
    
                print("\nEnter priorities (comma-separated, e.g., market,finance):")
                priorities_input = input("> ").strip()
                priorities = [p.strip() for p in priorities_input.split(",")] if priorities_input else []
    
                print("\nEnter constraints (comma-separated):")
                constraints_input = input("> ").strip()
                constraints = [c.strip() for c in constraints_input.split(",")] if constraints_input else []
    
                # Step 3: Run assessment
                user_inputs = {
                    "risk_tolerance": risk_tolerance,
                    "priorities": priorities,
                    "constraints": constraints
                }
    
                print(f"\nRunning strategy assessment for {entity_name}...")
                print("This may take a few minutes. Please wait...\n")
    
                result = orchestrator.run_strategy_assessment(entity_name, user_inputs)
    
                # Display results summary
                assessment_results = result.get("assessment_results", {})
    
                print("\nAssessment complete!")
                print(f"Entity: {entity_name}")
    
                # Show summary
                summary = assessment_results.get("summary", {})
                score = summary.get("overall_score", 0.5)
                risk_level = summary.get("risk_level", "Medium")
    
                print(f"Overall Score: {score*100:.1f}%")
                print(f"Risk Level: {risk_level}")
    
                # Show top recommendations
                print("\nTop Recommendations:")
                recommendations = assessment_results.get("recommendations", [])
                for i, rec in enumerate(recommendations[:3]):
                    print(f"{i+1}. {rec.get('title')} ({rec.get('priority', 'medium').capitalize()})")
    
                # Show PDF path
                pdf_path = result.get("pdf_path")
                if pdf_path:
                    print(f"\nReport saved to: {pdf_path}")
        
            elif choice == "7":
                # Exit
                print("\nCleaning up and exiting...")
                orchestrator.cleanup()
                print("System shutdown complete. Goodbye!")
                break
            
            else:
                print("\nInvalid choice. Please enter a number between 1 and 6.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up and exiting...")
        orchestrator.cleanup()
        print("System shutdown complete.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        print("Cleaning up and exiting...")
        orchestrator.cleanup()
        print("System shutdown complete.")

def main():
    """Main entry point for the system"""
    parser = argparse.ArgumentParser(description="Knowledge Graph Business Consulting System Runner")
    parser.add_argument("--process", "-p", help="Process a document file", default=None)
    parser.add_argument("--analyze", "-a", help="Analyze an entity", default=None)
    parser.add_argument("--visualize", "-v", help="Visualize an entity network", default=None)
    parser.add_argument("--depth", "-d", type=int, help="Network depth for visualization", default=2)
    parser.add_argument("--list-docs", "-l", action="store_true", help="List available documents")
    parser.add_argument("--list-entities", "-e", action="store_true", help="List top entities in knowledge graph")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # If no arguments provided, default to interactive mode
    if len(sys.argv) == 1:
        args.interactive = True
    
    if args.interactive:
        interactive_mode()
        return 0
    
    # Non-interactive mode
    print_banner()
    
    orchestrator = Orchestrator()
    
    try:
        if args.list_docs:
            documents = list_documents()
            
            if documents:
                print("\nAvailable documents in uploads directory:")
                print(f"{'#':<3} {'Filename':<40} {'Type':<8} {'Size':<10} {'Modified':<20}")
                print("-"*80)
                
                for i, (name, ext, size, modified) in enumerate(documents):
                    print(f"{i+1:<3} {name:<40} {ext.upper():<8} {size/1024:.1f} KB {modified:<20}")
            else:
                print("\nNo documents found in uploads directory.")
                print("Please add documents to 'data/uploads/' directory.")
        
        if args.list_entities:
            entities = list_entities(orchestrator)
            
            if entities:
                print("\nTop entities in knowledge graph:")
                print(f"{'#':<3} {'Entity Name':<40} {'Connections':<10}")
                print("-"*60)
                
                for i, entity in enumerate(entities):
                    print(f"{i+1:<3} {entity.get('name', 'Unknown'):<40} {entity.get('connections', 0):<10}")
            else:
                print("\nNo entities found in knowledge graph.")
                print("Process some documents first to populate the graph.")
        
        if args.process:
            file_path = args.process
            if os.path.isfile(file_path):
                process_document(orchestrator, file_path)
            else:
                print(f"Error: File not found: {file_path}")
        
        if args.analyze:
            entity_name = args.analyze
            analyze_entity(orchestrator, entity_name)
        
        if args.visualize:
            entity_name = args.visualize
            depth = args.depth
            visualize_entity(orchestrator, entity_name, depth)
        
        orchestrator.cleanup()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up and exiting...")
        orchestrator.cleanup()
        print("System shutdown complete.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        print("Cleaning up and exiting...")
        orchestrator.cleanup()
        print("System shutdown complete.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())