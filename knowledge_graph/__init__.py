"""
Knowledge graph module for the business consulting system.
Handles graph construction, querying, and relationship extraction.
"""

from knowledge_graph.neo4j_manager import Neo4jManager
from knowledge_graph.triplet_extractor import TripletExtractor
from knowledge_graph.graph_query import GraphQueryManager