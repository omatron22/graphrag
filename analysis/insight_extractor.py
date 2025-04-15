"""
Insight extractor for the knowledge graph-based business consulting system.
Identifies patterns, trends, correlations, and anomalies in the knowledge graph.
"""

import os
import logging
import json
from datetime import datetime
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
import networkx as nx
import config
from knowledge_graph.graph_query import GraphQueryManager

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InsightExtractor:
    """
    Extracts business insights from the knowledge graph by identifying
    patterns, trends, correlations, and anomalies.
    """
    
    def __init__(self, neo4j_manager):
        """
        Initialize the insight extractor.
        
        Args:
            neo4j_manager: Instance of Neo4jManager for graph access
        """
        self.neo4j_manager = neo4j_manager
        self.graph_query = GraphQueryManager(neo4j_manager)
        self.model_config = config.MODELS['reasoning']
        
        # Create output directory for insights
        self.output_dir = os.path.join("data", "knowledge_base", "insights")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("Insight Extractor initialized")
    
    def extract_insights(self, entity_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract comprehensive insights from the knowledge graph.
        
        Args:
            entity_name: Optional name of the entity to focus on
                         If None, analyzes the entire graph
            
        Returns:
            dict: Extracted insights with supporting data
        """
        logger.info(f"Extracting insights {'for ' + entity_name if entity_name else 'from entire graph'}")
        
        # Initialize results dictionary
        insights = {
            "timestamp": datetime.now().isoformat(),
            "focus_entity": entity_name,
            "key_findings": [],
            "patterns": [],
            "trends": [],
            "correlations": [],
            "anomalies": [],
            "networks": {},
            "metrics": {},
            "visualization_data": {}
        }
        
        # Apply different insight extraction methods
        try:
            # General graph analysis
            graph_metrics = self._analyze_graph_structure(entity_name)
            insights["metrics"] = graph_metrics
            
            # Pattern detection
            patterns = self._detect_patterns(entity_name)
            insights["patterns"] = patterns
            
            # Trend analysis
            trends = self._analyze_trends(entity_name)
            insights["trends"] = trends
            
            # Correlation analysis
            correlations = self._find_correlations(entity_name)
            insights["correlations"] = correlations
            
            # Anomaly detection
            anomalies = self._detect_anomalies(entity_name)
            insights["anomalies"] = anomalies
            
            # Network analysis
            network_insights = self._analyze_network(entity_name)
            insights["networks"] = network_insights
            
            # Generate key findings using LLM
            key_findings = self._generate_key_findings(
                entity_name, patterns, trends, correlations, anomalies, network_insights)
            insights["key_findings"] = key_findings
            
            # Prepare visualization data
            visualization_data = self._prepare_visualization_data(insights)
            insights["visualization_data"] = visualization_data
            
            # Save results to file
            self._save_insights(insights, entity_name)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return {"error": str(e)}
    
    def _analyze_graph_structure(self, entity_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the structure of the knowledge graph to extract metrics.
        
        Args:
            entity_name: Optional entity to focus on
            
        Returns:
            dict: Graph structure metrics
        """
        logger.info("Analyzing graph structure")
        
        # Query to get basic graph metrics
        graph_metric_query = """
        MATCH (n)
        RETURN 
            COUNT(n) as node_count, 
            size([p = ()-[]->() | p]) as relationship_count
        """
        
        # Query to get entity type distribution
        entity_type_query = """
        MATCH (n)
        WITH labels(n) as entity_labels
        UNWIND entity_labels as label
        RETURN label, COUNT(*) as count
        ORDER BY count DESC
        """
        
        # Query to get relationship type distribution
        relationship_type_query = """
        MATCH ()-[r]->()
        WITH type(r) as rel_type
        RETURN rel_type, COUNT(*) as count
        ORDER BY count DESC
        """
        
        # Execute queries
        graph_metrics = self.neo4j_manager.execute_query(graph_metric_query)
        entity_types = self.neo4j_manager.execute_query(entity_type_query)
        relationship_types = self.neo4j_manager.execute_query(relationship_type_query)
        
        # Calculate graph density if we have nodes and relationships
        density = 0
        if graph_metrics and len(graph_metrics) > 0:
            node_count = graph_metrics[0]['node_count']
            rel_count = graph_metrics[0]['relationship_count']
            if node_count > 1:
                density = rel_count / (node_count * (node_count - 1))
        
        # If entity_name is provided, get entity-specific metrics
        entity_specific = {}
        if entity_name:
            entity_query = f"""
            MATCH (e {{name: $entity_name}})-[r]-(connected)
            WITH e, connected, r, type(r) as rel_type
            RETURN 
                COUNT(DISTINCT connected) as connection_count,
                COUNT(r) as relationship_count,
                COLLECT(DISTINCT rel_type) as relationship_types,
                size([p = (e)-[*1..2]-(indirect) | p]) as extended_network_size
            """
            
            entity_metrics = self.neo4j_manager.execute_query(
                entity_query, {"entity_name": entity_name})
            
            if entity_metrics and len(entity_metrics) > 0:
                entity_specific = entity_metrics[0]
        
        # Compile results
        return {
            "overall": {
                "node_count": graph_metrics[0]['node_count'] if graph_metrics else 0,
                "relationship_count": graph_metrics[0]['relationship_count'] if graph_metrics else 0,
                "density": density,
            },
            "entity_distribution": entity_types,
            "relationship_distribution": relationship_types,
            "entity_specific": entity_specific
        }
    
    def _detect_patterns(self, entity_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect recurring patterns in the knowledge graph.
        
        Args:
            entity_name: Optional entity to focus on
            
        Returns:
            list: Detected patterns with supporting evidence
        """
        logger.info("Detecting patterns in knowledge graph")
        
        patterns = []
        
        # Pattern 1: Common entity relationships (frequent relationship paths)
        path_query = """
        MATCH path = (a)-[r1]->(b)-[r2]->(c)
        WHERE type(r1) <> type(r2)
        WITH type(r1) as type1, type(r2) as type2, COUNT(path) as frequency
        WHERE frequency > 2
        RETURN type1, type2, frequency
        ORDER BY frequency DESC
        LIMIT 5
        """
        
        # If entity name is provided, focus on that entity
        if entity_name:
            path_query = """
            MATCH path = (a {name: $entity_name})-[r1]->(b)-[r2]->(c)
            WITH type(r1) as type1, type(r2) as type2, COUNT(path) as frequency
            WHERE frequency > 1
            RETURN type1, type2, frequency
            ORDER BY frequency DESC
            LIMIT 5
            """
        
        relationship_patterns = self.neo4j_manager.execute_query(
            path_query, {"entity_name": entity_name} if entity_name else {})
        
        if relationship_patterns:
            pattern_description = "Common relationship chains"
            if entity_name:
                pattern_description = f"Common relationship chains from {entity_name}"
                
            patterns.append({
                "type": "relationship_chain",
                "description": pattern_description,
                "instances": relationship_patterns,
                "frequency": sum(item['frequency'] for item in relationship_patterns),
                "significance": "medium"  # Default significance
            })
        
        # Pattern 2: Common attribute combinations
        # (entities that frequently share the same set of attributes)
        attribute_query = """
        MATCH (e:Entity)
        WITH keys(e) as attributes, COUNT(*) as entity_count
        WHERE entity_count > 1 AND size(attributes) > 3
        RETURN attributes, entity_count
        ORDER BY entity_count DESC
        LIMIT 5
        """
        
        attribute_patterns = self.neo4j_manager.execute_query(attribute_query)
        
        if attribute_patterns:
            patterns.append({
                "type": "attribute_combination",
                "description": "Entities with similar attribute sets",
                "instances": attribute_patterns,
                "frequency": sum(item['entity_count'] for item in attribute_patterns),
                "significance": "medium"  # Default significance
            })
        
        # Pattern 3: Cyclical relationships (entities forming loops)
        cycle_query = """
        MATCH path = (a)-[r1]->(b)-[r2]->(c)-[r3]->(a)
        WHERE elementId(a) < elementId(b) AND elementId(b) < elementId(c) // Avoid duplicates
        WITH a.name as node1, b.name as node2, c.name as node3, 
             type(r1) as rel1, type(r2) as rel2, type(r3) as rel3,
             COUNT(path) as cycle_count
        RETURN node1, node2, node3, rel1, rel2, rel3, cycle_count
        ORDER BY cycle_count DESC
        LIMIT 5
        """
        
        cycle_patterns = self.neo4j_manager.execute_query(cycle_query)
        
        if cycle_patterns:
            patterns.append({
                "type": "relationship_cycle",
                "description": "Entities forming relationship cycles",
                "instances": cycle_patterns,
                "frequency": len(cycle_patterns),
                "significance": "high"  # Cycles are often significant
            })
        
        # Evaluate pattern significance based on frequency and coverage
        for pattern in patterns:
            if pattern["frequency"] > 10:
                pattern["significance"] = "high"
            elif pattern["frequency"] < 3:
                pattern["significance"] = "low"
        
        return patterns
    
    def _analyze_trends(self, entity_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze temporal trends in the knowledge graph.
        
        Args:
            entity_name: Optional entity to focus on
            
        Returns:
            list: Identified trends with supporting data
        """
        logger.info("Analyzing temporal trends")
        
        trends = []
        
        # Trend 1: Metric changes over time
        metric_trend_query = """
        MATCH (e:Entity)-[:HAS_METRIC]->(m:Metric)
        WHERE m.timestamp IS NOT NULL
        WITH e.name as entity, m.name as metric, m.value as value, m.timestamp as timestamp
        ORDER BY entity, metric, timestamp
        WITH entity, metric, COLLECT({value: value, timestamp: timestamp}) as values
        WHERE size(values) > 1
        RETURN entity, metric, values
        LIMIT 10
        """
        
        if entity_name:
            metric_trend_query = """
            MATCH (e:Entity {name: $entity_name})-[:HAS_METRIC]->(m:Metric)
            WHERE m.timestamp IS NOT NULL
            WITH e.name as entity, m.name as metric, m.value as value, m.timestamp as timestamp
            ORDER BY entity, metric, timestamp
            WITH entity, metric, COLLECT({value: value, timestamp: timestamp}) as values
            WHERE size(values) > 1
            RETURN entity, metric, values
            """
        
        metric_trends = self.neo4j_manager.execute_query(
            metric_trend_query, {"entity_name": entity_name} if entity_name else {})
        
        # Process metric trends to determine direction and significance
        for trend in metric_trends:
            values = trend["values"]
            if len(values) < 2:
                continue
                
            # Calculate trend direction and magnitude
            first_value = float(values[0]["value"]) if isinstance(values[0]["value"], (int, float, str)) else 0
            last_value = float(values[-1]["value"]) if isinstance(values[-1]["value"], (int, float, str)) else 0
            
            try:
                first_value = float(first_value)
                last_value = float(last_value)
                
                if first_value == 0:
                    percent_change = 100 if last_value > 0 else -100 if last_value < 0 else 0
                else:
                    percent_change = ((last_value - first_value) / abs(first_value)) * 100
                
                direction = "increasing" if percent_change > 0 else "decreasing" if percent_change < 0 else "stable"
                magnitude = "significant" if abs(percent_change) > 20 else "moderate" if abs(percent_change) > 5 else "minor"
                
                trends.append({
                    "type": "metric_trend",
                    "entity": trend["entity"],
                    "metric": trend["metric"],
                    "direction": direction,
                    "magnitude": magnitude,
                    "percent_change": round(percent_change, 2),
                    "values": values,
                    "significance": "high" if magnitude == "significant" else "medium" if magnitude == "moderate" else "low"
                })
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue
        
        # Trend 2: Relationship growth patterns
        relationship_trend_query = """
        MATCH (e1)-[r]->(e2)
        WHERE r.timestamp IS NOT NULL
        WITH type(r) as relationship_type, COUNT(r) as rel_count, 
             min(r.timestamp) as first_occurrence, max(r.timestamp) as last_occurrence
        RETURN relationship_type, rel_count, first_occurrence, last_occurrence
        ORDER BY rel_count DESC
        LIMIT 5
        """
        
        relationship_trends = self.neo4j_manager.execute_query(relationship_trend_query)
        
        for trend in relationship_trends:
            if "first_occurrence" not in trend or "last_occurrence" not in trend:
                continue
                
            # Convert to datetime if strings
            try:
                if isinstance(trend["first_occurrence"], str) and isinstance(trend["last_occurrence"], str):
                    first_date = datetime.fromisoformat(trend["first_occurrence"].replace('Z', '+00:00'))
                    last_date = datetime.fromisoformat(trend["last_occurrence"].replace('Z', '+00:00'))
                    
                    days_diff = (last_date - first_date).days
                    growth_rate = trend["rel_count"] / max(1, days_diff) * 30  # Monthly growth rate
                    
                    trends.append({
                        "type": "relationship_growth",
                        "relationship_type": trend["relationship_type"],
                        "total_count": trend["rel_count"],
                        "days_span": days_diff,
                        "growth_rate": round(growth_rate, 2),
                        "first_occurrence": trend["first_occurrence"],
                        "last_occurrence": trend["last_occurrence"],
                        "significance": "high" if growth_rate > 5 else "medium" if growth_rate > 1 else "low"
                    })
            except (ValueError, TypeError):
                # Skip invalid date formats
                continue
        
        # Trend 3: Entity importance evolution
        entity_evolution_query = """
        MATCH (e:Entity)
        WHERE e.created_at IS NOT NULL OR e.mentioned_dates IS NOT NULL
        WITH e, 
            CASE WHEN e.created_at IS NOT NULL THEN e.created_at ELSE null END as created_at,
            CASE WHEN e.mentioned_dates IS NOT NULL THEN e.mentioned_dates ELSE [] END as mentioned_dates,
            COUNT {(e)--()} as connection_count
        RETURN e.name as entity, created_at, mentioned_dates, connection_count
        ORDER BY connection_count DESC
        LIMIT 10
        """
        
        if entity_name:
            # For a specific entity, look at its connections over time instead
            entity_evolution_query = """
            MATCH (e:Entity {name: $entity_name})-[r]-(connected)
            WHERE r.timestamp IS NOT NULL
            WITH connected.name as connected_entity, r.timestamp as connection_time
            ORDER BY connection_time
            RETURN connected_entity, connection_time
            """
        
        entity_evolution = self.neo4j_manager.execute_query(
            entity_evolution_query, {"entity_name": entity_name} if entity_name else {})
        
        if entity_name and entity_evolution:
            # For specific entity, analyze connection growth pattern
            connection_points = [(item["connected_entity"], item["connection_time"]) for item in entity_evolution]
            
            if connection_points:
                trends.append({
                    "type": "entity_evolution",
                    "entity": entity_name,
                    "connection_growth": connection_points,
                    "connection_count": len(connection_points),
                    "significance": "medium"
                })
        
        return trends
    
    def _find_correlations(self, entity_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find correlations between different metrics and entities.
        
        Args:
            entity_name: Optional entity to focus on
            
        Returns:
            list: Detected correlations with supporting evidence
        """
        logger.info("Finding correlations in knowledge graph")
        
        correlations = []
        
        # Correlation 1: Entity metrics that move together
        metric_correlation_query = """
        MATCH (e1:Entity)-[:HAS_METRIC]->(m1:Metric)
        MATCH (e2:Entity)-[:HAS_METRIC]->(m2:Metric)
        WHERE e1 <> e2 AND m1.name = m2.name 
              AND m1.timestamp IS NOT NULL AND m2.timestamp IS NOT NULL
              AND abs(datetime(m1.timestamp) - datetime(m2.timestamp)) < duration('P7D')
        WITH e1.name as entity1, e2.name as entity2, m1.name as metric,
             m1.value as value1, m2.value as value2
        WHERE (value1 IS NOT NULL AND value2 IS NOT NULL) AND 
            ((value1 IS INTEGER AND value2 IS INTEGER) OR (value1 IS FLOAT AND value2 IS FLOAT))        WITH entity1, entity2, metric, COLLECT({v1: value1, v2: value2}) as value_pairs
        WHERE size(value_pairs) > 2
        RETURN entity1, entity2, metric, value_pairs
        LIMIT 5
        """
        
        if entity_name:
            metric_correlation_query = """
            MATCH (e1:Entity {name: $entity_name})-[:HAS_METRIC]->(m1:Metric)
            MATCH (e2:Entity)-[:HAS_METRIC]->(m2:Metric)
            WHERE e1 <> e2 AND m1.name = m2.name 
                  AND m1.timestamp IS NOT NULL AND m2.timestamp IS NOT NULL
                  AND abs(datetime(m1.timestamp) - datetime(m2.timestamp)) < duration('P7D')
            WITH e1.name as entity1, e2.name as entity2, m1.name as metric,
                 m1.value as value1, m2.value as value2
            WHERE (value1 IS NOT NULL AND value2 IS NOT NULL) AND 
                ((value1 IS INTEGER AND value2 IS INTEGER) OR (value1 IS FLOAT AND value2 IS FLOAT))            WITH entity1, entity2, metric, COLLECT({v1: value1, v2: value2}) as value_pairs
            WHERE size(value_pairs) > 2
            RETURN entity1, entity2, metric, value_pairs
            """
        
        metric_correlations = self.neo4j_manager.execute_query(
            metric_correlation_query, {"entity_name": entity_name} if entity_name else {})
        
        # Calculate correlation coefficient and significance
        for corr in metric_correlations:
            try:
                # Extract paired values
                value_pairs = corr["value_pairs"]
                x_values = [float(pair["v1"]) for pair in value_pairs]
                y_values = [float(pair["v2"]) for pair in value_pairs]
                
                # Calculate simple correlation coefficient
                # This is a simplified version - in production, use scipy or numpy
                n = len(x_values)
                if n < 3:
                    continue
                    
                sum_x = sum(x_values)
                sum_y = sum(y_values)
                sum_xy = sum(x*y for x, y in zip(x_values, y_values))
                sum_x2 = sum(x*x for x in x_values)
                sum_y2 = sum(y*y for y in y_values)
                
                # Calculate correlation coefficient
                numerator = n * sum_xy - sum_x * sum_y
                denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))**0.5
                
                if denominator == 0:
                    continue
                    
                correlation_coef = numerator / denominator
                
                # Determine direction and strength
                correlation_strength = abs(correlation_coef)
                correlation_direction = "positive" if correlation_coef > 0 else "negative"
                strength_label = "strong" if correlation_strength > 0.7 else "moderate" if correlation_strength > 0.3 else "weak"
                
                correlations.append({
                    "type": "metric_correlation",
                    "entity1": corr["entity1"],
                    "entity2": corr["entity2"],
                    "metric": corr["metric"],
                    "correlation_coefficient": round(correlation_coef, 2),
                    "direction": correlation_direction,
                    "strength": strength_label,
                    "data_points": len(value_pairs),
                    "significance": "high" if correlation_strength > 0.7 and len(value_pairs) > 5 else "medium" if correlation_strength > 0.5 else "low"
                })
            except (ValueError, TypeError, ZeroDivisionError):
                # Skip on calculation errors
                continue
        
        # Correlation 2: Entities that frequently appear together
        cooccurrence_query = """
        MATCH (a)-[:MENTIONED_WITH|APPEARS_WITH|RELATED_TO]->(b)
        WITH a, b, COUNT(*) as frequency
        WHERE frequency > 2 AND elementId(a) < elementId(b) // Avoid duplicates
        RETURN a.name as entity1, b.name as entity2, frequency
        ORDER BY frequency DESC
        LIMIT 10
        """
        
        if entity_name:
            cooccurrence_query = """
            MATCH (a {name: $entity_name})-[:MENTIONED_WITH|APPEARS_WITH|RELATED_TO]->(b)
            WITH a, b, COUNT(*) as frequency
            WHERE frequency > 1
            RETURN a.name as entity1, b.name as entity2, frequency
            ORDER BY frequency DESC
            LIMIT 10
            """
        
        cooccurrence_correlations = self.neo4j_manager.execute_query(
            cooccurrence_query, {"entity_name": entity_name} if entity_name else {})
        
        for corr in cooccurrence_correlations:
            correlations.append({
                "type": "co_occurrence",
                "entity1": corr["entity1"],
                "entity2": corr["entity2"],
                "frequency": corr["frequency"],
                "significance": "high" if corr["frequency"] > 5 else "medium" if corr["frequency"] > 3 else "low"
            })
        
        return correlations
    
    def _detect_anomalies(self, entity_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect anomalies and outliers in the knowledge graph.
    
        Args:
            entity_name: Optional entity to focus on
        
        Returns:
            list: Detected anomalies with supporting evidence
        """
        logger.info("Detecting anomalies in knowledge graph")
    
        anomalies = []
    
        # Anomaly 1: Metric outliers (values that deviate significantly from average)
        metric_outlier_query = """
        MATCH (e:Entity)-[:HAS_METRIC]->(m:Metric)
        WHERE m.name IS NOT NULL AND m.value IS NOT NULL
        WITH m.name as metric_name, AVG(toFloat(m.value)) as avg_value, 
            STDEV(toFloat(m.value)) as std_value
        MATCH (e:Entity)-[:HAS_METRIC]->(m:Metric)
        WHERE m.name = metric_name AND
            abs(toFloat(m.value) - avg_value) > 2 * std_value
        RETURN e.name as entity, m.name as metric, m.value as value, 
            avg_value, std_value, 
            abs(toFloat(m.value) - avg_value) / std_value as z_score
        ORDER BY z_score DESC
        LIMIT 10
        """
    
        if entity_name:
            metric_outlier_query = """
            MATCH (e:Entity {name: $entity_name})-[:HAS_METRIC]->(m:Metric)
            WHERE m.name IS NOT NULL AND m.value IS NOT NULL
            WITH m.name as metric_name, toFloat(m.value) as entity_value
            MATCH (other:Entity)-[:HAS_METRIC]->(om:Metric)
            WHERE other.name <> $entity_name AND 
                om.name = metric_name
            WITH metric_name, entity_value, AVG(toFloat(om.value)) as avg_value, 
                STDEV(toFloat(om.value)) as std_value
            WHERE abs(entity_value - avg_value) > 1.5 * std_value AND std_value > 0
            RETURN metric_name as metric, entity_value as value, 
                avg_value, std_value, 
                abs(entity_value - avg_value) / std_value as z_score
            ORDER BY z_score DESC
            """
    
        metric_outliers = self.neo4j_manager.execute_query(
            metric_outlier_query, {"entity_name": entity_name} if entity_name else {})
    
        for outlier in metric_outliers:
            z_score = outlier.get("z_score", 0)
            severity = "extreme" if z_score > 3 else "significant" if z_score > 2 else "moderate"
        
            anomaly_type = "above_average" if float(outlier.get("value", 0)) > float(outlier.get("avg_value", 0)) else "below_average"
        
            anomalies.append({
                "type": "metric_outlier",
                "entity": outlier.get("entity", entity_name),
                "metric": outlier["metric"],
                "value": outlier["value"],
                "average": round(float(outlier["avg_value"]), 2),
                "standard_deviation": round(float(outlier["std_value"]), 2),
                "z_score": round(float(z_score), 2),
                "direction": anomaly_type,
                "severity": severity,
                "significance": "high" if severity == "extreme" else "medium" if severity == "significant" else "low"
            })
    
        # Anomaly 2: Structural anomalies (unusually connected or isolated entities)
        connection_anomaly_query = """
        MATCH (e:Entity)
        WITH e, COUNT {(e)--()} as connection_count
        WITH AVG(connection_count) as avg_connections, 
            STDEV(connection_count) as std_connections
        MATCH (e:Entity)
        WITH e, COUNT {(e)--()} as connection_count, avg_connections, std_connections
        WHERE abs(connection_count - avg_connections) > 2 * std_connections
        RETURN e.name as entity, connection_count, 
            avg_connections, std_connections,
            abs(connection_count - avg_connections) / std_connections as z_score
        ORDER BY z_score DESC
        LIMIT 10
        """
    
        if entity_name:
            connection_anomaly_query = """
            MATCH (e:Entity {name: $entity_name})
            WITH e, COUNT {(e)--()} as entity_connections
            MATCH (other:Entity)
            WHERE other.name <> $entity_name
            WITH e, entity_connections, other, COUNT {(other)--()} as other_connections
            WITH e, entity_connections, AVG(other_connections) as avg_connections, 
                STDEV(other_connections) as std_connections
            WHERE abs(entity_connections - avg_connections) > 1.5 * std_connections AND std_connections > 0
            RETURN e.name as entity, entity_connections as connection_count, 
                avg_connections, std_connections,
                abs(entity_connections - avg_connections) / std_connections as z_score
            """
    
        connection_anomalies = self.neo4j_manager.execute_query(
            connection_anomaly_query, {"entity_name": entity_name} if entity_name else {})
    
        for anomaly in connection_anomalies:
            z_score = anomaly.get("z_score", 0)
            severity = "extreme" if z_score > 3 else "significant" if z_score > 2 else "moderate"
        
            anomaly_type = "highly_connected" if int(anomaly.get("connection_count", 0)) > float(anomaly.get("avg_connections", 0)) else "isolated"
        
            anomalies.append({
                "type": "connectivity_anomaly",
                "entity": anomaly["entity"],
                "connection_count": anomaly["connection_count"],
                "average_connections": round(float(anomaly["avg_connections"]), 2),
                "z_score": round(float(z_score), 2),
                "pattern": anomaly_type,
                "severity": severity,
                "significance": "high" if severity == "extreme" else "medium" if severity == "significant" else "low"
            })
    
        # Anomaly 3: Temporal anomalies (sudden changes or irregular patterns)
        if entity_name:
            temporal_anomaly_query = """
            MATCH (e:Entity {name: $entity_name})-[:HAS_METRIC]->(m:Metric)
            WHERE m.timestamp IS NOT NULL
            WITH m.name as metric, m.value as value, m.timestamp as timestamp
            ORDER BY timestamp
            WITH metric, COLLECT({value: value, timestamp: timestamp}) as values
            WHERE size(values) > 3
            RETURN metric, values
            """
        
            temporal_data = self.neo4j_manager.execute_query(
                temporal_anomaly_query, {"entity_name": entity_name})
        
            for series in temporal_data:
                try:
                    # Handle temporal anomalies for entity metrics
                    values = series["values"]
                    if len(values) < 4:  # Need at least 4 points to detect anomalies
                        continue
                
                    # Convert to numeric values and timestamps
                    try:
                        time_series = []
                        for point in values:
                            if isinstance(point["value"], (int, float, str)) and point["timestamp"]:
                                value = float(point["value"])
                                time_series.append((point["timestamp"], value))
                
                        if len(time_series) < 4:
                            continue
                    
                        # Sort by timestamp
                        time_series.sort(key=lambda x: x[0])
                
                        # Calculate rate of change between consecutive points
                        changes = []
                        for i in range(1, len(time_series)):
                            prev_value = time_series[i-1][1]
                            curr_value = time_series[i][1]
                    
                            if prev_value != 0:
                                percent_change = ((curr_value - prev_value) / abs(prev_value)) * 100
                            else:
                                percent_change = 100 if curr_value > 0 else -100 if curr_value < 0 else 0
                        
                            changes.append(percent_change)
                
                        # Calculate mean and standard deviation of changes
                        mean_change = sum(changes) / len(changes)
                        std_change = (sum((x - mean_change) ** 2 for x in changes) / len(changes)) ** 0.5
                
                        # Identify points with anomalous changes
                        anomalous_points = []
                        for i in range(len(changes)):
                            z_score = abs(changes[i] - mean_change) / max(0.0001, std_change)
                            if z_score > 2:  # More than 2 standard deviations
                                anomalous_points.append({
                                    "timestamp": time_series[i+1][0],
                                    "value": time_series[i+1][1],
                                    "percent_change": round(changes[i], 2),
                                    "z_score": round(z_score, 2)
                                })
                
                        if anomalous_points:
                            anomalies.append({
                                "type": "temporal_anomaly",
                                "entity": entity_name,
                                "metric": series["metric"],
                                "anomalous_points": anomalous_points,
                                "mean_change_rate": round(mean_change, 2),
                                "std_change_rate": round(std_change, 2),
                                "significance": "high" if any(point["z_score"] > 3 for point in anomalous_points) else "medium"
                            })
                    except (ValueError, TypeError, ZeroDivisionError, IndexError):
                        # Skip on calculation errors
                        continue
                except Exception as e:
                    # Skip on calculation errors
                    logger.warning(f"Error processing temporal anomaly for series {series.get('metric', 'unknown')}: {e}")
                    continue
    
        return anomalies
    
    def _analyze_network(self, entity_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze network properties of the knowledge graph with better error handling
    
        Args:
            entity_name: Optional entity to focus on
        
        Returns:
            dict: Network analysis results
        """
        logger.info("Performing network analysis")
    
        # Prepare query to get graph data for network analysis
        if entity_name:
            # Focused subgraph for specific entity
            graph_query = """
            MATCH path = (e:Entity {name: $name})-[*1..2]-(connected:Entity)
            UNWIND relationships(path) as rel
            WITH DISTINCT startNode(rel) as source, endNode(rel) as target, type(rel) as rel_type
            WHERE source:Entity AND target:Entity
            RETURN source.name as source, target.name as target, rel_type
            """
        
            params = {"name": entity_name}
        else:
            # Full entity graph (limited to a reasonable size)
            graph_query = """
            MATCH (source:Entity)-[rel]->(target:Entity)
            RETURN source.name as source, target.name as target, type(rel) as rel_type
            LIMIT 1000
            """
        
            params = {}
    
        # Execute query with better error handling
        try:
            relationships = self.neo4j_manager.execute_query(graph_query, params)
        except Exception as e:
            logger.error(f"Error retrieving network data: {e}")
            # Return empty results instead of failing
            return {
                "centrality": [],
                "communities": [],
                "clusters": []
            }
        
        # If no relationships found, return empty results
        if not relationships:
            return {
                "centrality": [],
                "communities": [],
                "clusters": []
            }
    
        try:
            # Build NetworkX graph
            G = nx.DiGraph()
        
            # Add edges
            for rel in relationships:
                source = rel["source"]
                target = rel["target"]
                rel_type = rel["rel_type"]
            
                if source and target:  # Make sure both exist
                    G.add_edge(source, target, type=rel_type)
        
            # Calculate network metrics
            results = {
                "graph_size": {
                    "nodes": G.number_of_nodes(),
                    "edges": G.number_of_edges()
                },
                "centrality": [],
                "communities": [],
                "clusters": []
            }
        
            # Only proceed if we have nodes
            if G.number_of_nodes() > 0:
                # Calculate centrality measures (who's most important)
                try:
                    # Degree centrality
                    degree_centrality = nx.degree_centrality(G)
                
                    # Betweenness centrality (limited to prevent long calculation times)
                    if G.number_of_nodes() <= 100:  # Reduced threshold
                        betweenness_centrality = nx.betweenness_centrality(G, k=min(G.number_of_nodes()//2, 10))
                    else:
                        betweenness_centrality = {}
                    
                    # PageRank (influence) with limited iterations
                    pagerank = nx.pagerank(G, alpha=0.85, max_iter=50)
                
                    # Combine centrality measures
                    centrality_results = []
                    for node in G.nodes():
                        centrality_results.append({
                            "entity": node,
                            "degree_centrality": round(degree_centrality.get(node, 0), 3),
                            "betweenness_centrality": round(betweenness_centrality.get(node, 0), 3),
                            "pagerank": round(pagerank.get(node, 0), 3),
                            "overall_importance": round(
                                degree_centrality.get(node, 0) * 0.3 + 
                                betweenness_centrality.get(node, 0) * 0.3 + 
                                pagerank.get(node, 0) * 0.4, 
                                3
                            )
                        })
                
                    # Sort by overall importance
                    centrality_results.sort(key=lambda x: x["overall_importance"], reverse=True)
                    results["centrality"] = centrality_results[:10]  # Reduced from 20 to 10
                except Exception as e:
                    logger.warning(f"Error calculating centrality metrics: {e}")
            
                # Only perform community detection for smaller graphs
                if G.number_of_nodes() <= 100:
                    try:
                        # Convert to undirected graph for community detection
                        G_undir = G.to_undirected()
                    
                        # Use Louvain community detection algorithm
                        communities = nx.community.louvain_communities(G_undir)
                    
                        # Format communities
                        community_results = []
                        for i, comm in enumerate(communities):
                            if len(comm) > 1:  # Only include communities with more than one entity
                                community_results.append({
                                    "id": i + 1,
                                    "size": len(comm),
                                    "entities": list(comm)[:5],  # Limit to 5 entities per community
                                    "key_entities": list(sorted(
                                        comm, 
                                        key=lambda x: pagerank.get(x, 0), 
                                        reverse=True
                                    ))[:3]  # Top 3 entities by PageRank
                                })
                    
                        results["communities"] = community_results
                    except Exception as e:
                        logger.warning(f"Error detecting communities: {e}")
        
            return results
    
        except Exception as e:
            logger.error(f"Error in network analysis: {e}")
            # Return minimal results
            return {
                "graph_size": {"nodes": 0, "edges": 0},
                "centrality": [],
                "communities": [],
                "clusters": []
            }
    
    def _generate_key_findings(self, entity_name: Optional[str], patterns: List[Dict[str, Any]], 
                              trends: List[Dict[str, Any]], correlations: List[Dict[str, Any]], 
                              anomalies: List[Dict[str, Any]], 
                              network_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate key findings from the extracted insights using LLM.
        
        Args:
            entity_name: Optional focus entity
            patterns: Detected patterns
            trends: Identified trends
            correlations: Found correlations
            anomalies: Detected anomalies
            network_insights: Network analysis results
            
        Returns:
            list: Key findings with explanations
        """
        logger.info("Generating key findings using LLM")
        
        # Filter to high and medium significance insights only
        high_significance = []
        
        # Add patterns
        for pattern in patterns:
            if pattern.get("significance") in ["high", "medium"]:
                high_significance.append({
                    "type": "pattern",
                    "subtype": pattern.get("type", ""),
                    "description": pattern.get("description", ""),
                    "frequency": pattern.get("frequency", 0),
                    "significance": pattern.get("significance", "medium")
                })
        
        # Add trends
        for trend in trends:
            if trend.get("significance") in ["high", "medium"]:
                high_significance.append({
                    "type": "trend",
                    "subtype": trend.get("type", ""),
                    "entity": trend.get("entity", ""),
                    "metric": trend.get("metric", ""),
                    "direction": trend.get("direction", ""),
                    "magnitude": trend.get("magnitude", ""),
                    "percent_change": trend.get("percent_change", 0),
                    "significance": trend.get("significance", "medium")
                })
        
        # Add correlations
        for corr in correlations:
            if corr.get("significance") in ["high", "medium"]:
                high_significance.append({
                    "type": "correlation",
                    "subtype": corr.get("type", ""),
                    "entity1": corr.get("entity1", ""),
                    "entity2": corr.get("entity2", ""),
                    "metric": corr.get("metric", ""),
                    "strength": corr.get("strength", ""),
                    "correlation_coefficient": corr.get("correlation_coefficient", 0),
                    "significance": corr.get("significance", "medium")
                })
        
        # Add anomalies
        for anomaly in anomalies:
            if anomaly.get("significance") in ["high", "medium"]:
                high_significance.append({
                    "type": "anomaly",
                    "subtype": anomaly.get("type", ""),
                    "entity": anomaly.get("entity", ""),
                    "metric": anomaly.get("metric", ""),
                    "severity": anomaly.get("severity", ""),
                    "z_score": anomaly.get("z_score", 0),
                    "significance": anomaly.get("significance", "medium")
                })
        
        # Add network insights
        if network_insights.get("centrality"):
            top_entities = network_insights["centrality"][:3]  # Top 3 entities
            for entity in top_entities:
                high_significance.append({
                    "type": "network",
                    "subtype": "centrality",
                    "entity": entity.get("entity", ""),
                    "importance": entity.get("overall_importance", 0),
                    "significance": "high" if entity.get("overall_importance", 0) > 0.5 else "medium"
                })
        
        # If no significant insights found, return empty list
        if not high_significance:
            return []
        
        # Format insights for LLM prompt
        insights_text = json.dumps(high_significance, indent=2)
        
        # Prepare LLM prompt
        prompt = f"""
        You are an expert business analyst tasked with identifying key insights and findings from data analysis.
        
        Below is a JSON representation of patterns, trends, correlations, anomalies, and network properties
        discovered in a business knowledge graph{' for ' + entity_name if entity_name else ''}.
        
        Insights data:
        {insights_text}
        
        Based on these insights, identify the 3-5 most significant findings that would be valuable for business
        decision-making. For each finding:
        1. Provide a clear, concise title (10 words max)
        2. Write a brief explanation of the finding (1-3 sentences)
        3. Explain the business implications (1-2 sentences)
        
        Return your analysis as a JSON array with the following structure:
        [
          {{
            "title": "Finding title",
            "explanation": "Explanation of the finding",
            "business_implications": "Business implications",
            "category": "pattern|trend|correlation|anomaly|network"
          }},
          ...
        ]
        
        ONLY return the JSON array of findings and nothing else.
        """
        
        # Call the LLM
        try:
            logger.info("Calling LLM for key findings analysis")
            response = requests.post(
                self.model_config['endpoint'],
                json={
                    "model": self.model_config['name'],
                    "prompt": prompt,
                    "stream": False,
                    **self.model_config['parameters']
                }
            )
            
            result = response.json()
            content = result.get('response', '')
            
            # Extract the JSON object from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                findings = json.loads(json_str)
                logger.info(f"Generated {len(findings)} key findings")
                return findings
            else:
                logger.warning("Could not extract JSON from LLM response")
                return self._generate_fallback_findings(high_significance)
                
        except Exception as e:
            logger.error(f"Error in LLM key findings generation: {e}")
            return self._generate_fallback_findings(high_significance)
    
    def _generate_fallback_findings(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate basic findings when LLM fails.
        
        Args:
            insights: List of significant insights
            
        Returns:
            list: Basic findings
        """
        logger.info("Using fallback findings generation")
        
        findings = []
        
        # Sort insights by significance
        sorted_insights = sorted(
            insights, 
            key=lambda x: 0 if x.get("significance") == "high" else 1
        )
        
        # Take top 3 insights (if available)
        top_insights = sorted_insights[:min(3, len(sorted_insights))]
        
        for insight in top_insights:
            insight_type = insight.get("type", "")
            
            if insight_type == "pattern":
                findings.append({
                    "title": f"Recurring {insight.get('subtype', 'pattern')} detected",
                    "explanation": f"Analysis found a {insight.get('significance', 'significant')} pattern: {insight.get('description', '')}.",
                    "business_implications": "This pattern suggests consistent relationships that could be leveraged for strategic planning.",
                    "category": "pattern"
                })
            elif insight_type == "trend":
                findings.append({
                    "title": f"{insight.get('direction', 'Changing')} {insight.get('metric', 'metric')} trend",
                    "explanation": f"The {insight.get('metric', 'metric')} for {insight.get('entity', 'entity')} shows a {insight.get('direction', '')} trend of {insight.get('percent_change', 0)}%.",
                    "business_implications": "This trend indicates changing conditions that may require attention or adjustment of strategies.",
                    "category": "trend"
                })
            elif insight_type == "correlation":
                findings.append({
                    "title": f"{insight.get('strength', 'Strong')} correlation between entities",
                    "explanation": f"Found a {insight.get('direction', '')} correlation between {insight.get('entity1', '')} and {insight.get('entity2', '')} with coefficient {insight.get('correlation_coefficient', 0)}.",
                    "business_implications": "This correlation indicates a relationship that could be used for predictive analysis or strategic decision-making.",
                    "category": "correlation"
                })
            elif insight_type == "anomaly":
                findings.append({
                    "title": f"{insight.get('severity', 'Significant')} anomaly detected",
                    "explanation": f"Found a {insight.get('severity', '')} anomaly for {insight.get('entity', '')} with z-score of {insight.get('z_score', 0)}.",
                    "business_implications": "This anomaly represents a deviation from normal patterns that may indicate risk or opportunity.",
                    "category": "anomaly"
                })
            elif insight_type == "network":
                findings.append({
                    "title": f"High centrality entity identified",
                    "explanation": f"{insight.get('entity', '')} has high centrality with importance score of {insight.get('importance', 0)}.",
                    "business_implications": "Central entities have disproportionate influence and should be key considerations in strategic planning.",
                    "category": "network"
                })
        
        return findings
    
    def _prepare_visualization_data(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for visualizing insights.
        
        Args:
            insights: Extracted insights data
            
        Returns:
            dict: Visualization data for charts and graphs
        """
        logger.info("Preparing visualization data for insights")
        
        visualization_data = {
            "network_graph": self._prepare_network_visualization(insights),
            "trend_charts": self._prepare_trend_visualization(insights),
            "anomaly_charts": self._prepare_anomaly_visualization(insights),
            "correlation_matrix": self._prepare_correlation_visualization(insights),
            "key_metrics": self._prepare_metrics_visualization(insights)
        }
        
        return visualization_data
    
    def _prepare_network_visualization(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare network visualization data.
        
        Args:
            insights: Extracted insights
            
        Returns:
            dict: Network visualization data
        """
        # Extract network data
        network_data = insights.get("networks", {})
        centrality = network_data.get("centrality", [])
        communities = network_data.get("communities", [])
        
        # Prepare nodes and links for visualization
        nodes = []
        node_ids = set()
        
        # Add nodes from centrality data
        for entity in centrality:
            entity_name = entity.get("entity", "")
            if entity_name and entity_name not in node_ids:
                nodes.append({
                    "id": entity_name,
                    "name": entity_name,
                    "importance": entity.get("overall_importance", 0),
                    "size": max(10, min(50, entity.get("overall_importance", 0) * 100)),
                    "group": 1  # Default group
                })
                node_ids.add(entity_name)
        
        # Assign community groupings
        for i, community in enumerate(communities):
            for entity in community.get("entities", []):
                for node in nodes:
                    if node["id"] == entity:
                        node["group"] = i + 1
                        break
        
        # Prepare links from patterns
        links = []
        relationship_patterns = []
        
        for pattern in insights.get("patterns", []):
            if pattern.get("type") == "relationship_chain":
                for instance in pattern.get("instances", []):
                    relationship_patterns.append(instance)
        
        # Create links from relationship patterns
        for pattern in relationship_patterns:
            type1 = pattern.get("type1", "")
            type2 = pattern.get("type2", "")
            
            # We need source and target nodes for these relationships
            # This is a simplified approach - in a real implementation,
            # you'd query the database for actual examples of these patterns
            for source in node_ids:
                for target in node_ids:
                    if source != target:
                        links.append({
                            "source": source,
                            "target": target,
                            "value": pattern.get("frequency", 1),
                            "type": f"{type1} → {type2}"
                        })
                        break  # Just one example
                break  # Just one example
        
        return {
            "type": "network_graph",
            "title": "Entity Relationship Network",
            "description": "Network visualization of entity relationships and communities",
            "data": {
                "nodes": nodes,
                "links": links
            }
        }
    
    def _prepare_trend_visualization(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare trend visualization data.
        
        Args:
            insights: Extracted insights
            
        Returns:
            dict: Trend visualization data
        """
        trends = insights.get("trends", [])
        
        # Filter for metric trends
        metric_trends = [t for t in trends if t.get("type") == "metric_trend"]
        
        # Prepare data for line charts
        datasets = []
        
        for trend in metric_trends:
            entity = trend.get("entity", "")
            metric = trend.get("metric", "")
            values = trend.get("values", [])
            
            if not values:
                continue
                
            # Extract timestamps and values
            data_points = []
            for point in values:
                if "timestamp" in point and "value" in point:
                    try:
                        value = float(point["value"])
                        data_points.append({
                            "x": point["timestamp"],
                            "y": value
                        })
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        continue
            
            # Sort by timestamp
            data_points.sort(key=lambda x: x["x"])
            
            # Add to datasets
            if data_points:
                datasets.append({
                    "label": f"{entity} - {metric}",
                    "data": data_points,
                    "entity": entity,
                    "metric": metric,
                    "direction": trend.get("direction", ""),
                    "percent_change": trend.get("percent_change", 0)
                })
        
        return {
            "type": "line_chart",
            "title": "Metric Trends Over Time",
            "description": "Visualization of how metrics change over time",
            "datasets": datasets
        }
    
    def _prepare_anomaly_visualization(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare anomaly visualization data.
        
        Args:
            insights: Extracted insights
            
        Returns:
            dict: Anomaly visualization data
        """
        anomalies = insights.get("anomalies", [])
        
        # Filter for metric outliers
        metric_outliers = [a for a in anomalies if a.get("type") == "metric_outlier"]
        
        # Prepare data for scatter plot
        scatter_data = []
        
        for outlier in metric_outliers:
            entity = outlier.get("entity", "")
            metric = outlier.get("metric", "")
            value = outlier.get("value", 0)
            average = outlier.get("average", 0)
            z_score = outlier.get("z_score", 0)
            
            try:
                value = float(value)
                scatter_data.append({
                    "entity": entity,
                    "metric": metric,
                    "value": value,
                    "average": average,
                    "z_score": z_score,
                    "color": "red" if z_score > 3 else "orange" if z_score > 2 else "yellow"
                })
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue
        
        # Group by metric
        metric_groups = {}
        for point in scatter_data:
            metric = point["metric"]
            if metric not in metric_groups:
                metric_groups[metric] = []
            metric_groups[metric].append(point)
        
        # Create normalized datasets (scale values relative to average)
        normalized_datasets = []
        for metric, points in metric_groups.items():
            if not points:
                continue
                
            dataset = {
                "metric": metric,
                "average": points[0]["average"],
                "points": [{
                    "entity": p["entity"],
                    "value": p["value"],
                    "normalized_value": p["value"] / max(0.0001, p["average"]),
                    "z_score": p["z_score"],
                    "color": p["color"]
                } for p in points]
            }
            normalized_datasets.append(dataset)
        
        return {
            "type": "scatter_plot",
            "title": "Metric Anomalies",
            "description": "Visualization of metric values that deviate significantly from average",
            "datasets": normalized_datasets
        }
    
    def _prepare_correlation_visualization(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare correlation visualization data.
        
        Args:
            insights: Extracted insights
            
        Returns:
            dict: Correlation visualization data
        """
        correlations = insights.get("correlations", [])
        
        # Filter for metric correlations
        metric_correlations = [c for c in correlations if c.get("type") == "metric_correlation"]
        
        # Prepare data for correlation matrix
        matrix_data = []
        
        for corr in metric_correlations:
            entity1 = corr.get("entity1", "")
            entity2 = corr.get("entity2", "")
            metric = corr.get("metric", "")
            coefficient = corr.get("correlation_coefficient", 0)
            
            if entity1 and entity2 and metric:
                matrix_data.append({
                    "entity1": entity1,
                    "entity2": entity2,
                    "metric": metric,
                    "coefficient": coefficient,
                    "strength": abs(coefficient),
                    "color": "green" if coefficient > 0 else "red"
                })
        
        # Also include co-occurrence correlations
        cooccurrence_correlations = [c for c in correlations if c.get("type") == "co_occurrence"]
        
        for corr in cooccurrence_correlations:
            entity1 = corr.get("entity1", "")
            entity2 = corr.get("entity2", "")
            frequency = corr.get("frequency", 0)
            
            if entity1 and entity2:
                # Normalize frequency to a correlation-like coefficient (-1 to 1)
                # This is a simplification for visualization purposes
                normalized_freq = min(0.9, frequency / 10)  # Max at 0.9 for frequencies >= 10
                
                matrix_data.append({
                    "entity1": entity1,
                    "entity2": entity2,
                    "metric": "co-occurrence",
                    "coefficient": normalized_freq,
                    "strength": normalized_freq,
                    "color": "blue"  # Different color for co-occurrence
                })
        
        return {
            "type": "correlation_matrix",
            "title": "Entity Correlations",
            "description": "Matrix visualization of correlations between entities",
            "data": matrix_data
        }
    
    def _prepare_metrics_visualization(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare key metrics visualization data.
    
        Args:
            insights: Extracted insights
        
        Returns:
            dict: Key metrics visualization data
        """
        # Extract graph metrics
        graph_metrics = insights.get("metrics", {}).get("overall", {})
    
        # Prepare data for metrics dashboard
        metrics_data = [
            {
                "name": "Node Count",
                "value": graph_metrics.get("node_count", 0),
                "description": "Total number of entities in the knowledge graph"
            },
            {
                "name": "Relationship Count",
                "value": graph_metrics.get("relationship_count", 0),
                "description": "Total number of relationships between entities"
            },
            {
                "name": "Graph Density",
                "value": round(graph_metrics.get("density", 0) * 100, 2),
                "unit": "%",
                "description": "Percentage of potential connections that actually exist"
            }
        ]
    
        # Add entity-specific metrics if available
        entity_specific = insights.get("metrics", {}).get("entity_specific", {})
        if entity_specific:
            metrics_data.extend([
                {
                    "name": "Connection Count",
                    "value": entity_specific.get("connection_count", 0),
                    "description": "Number of entities directly connected to the focus entity"
                },
                {
                    "name": "Extended Network Size",
                    "value": entity_specific.get("extended_network_size", 0),
                    "description": "Size of the network within 2 degrees of separation"
                }
            ])
    
        # Add some pattern and trend metrics
        pattern_count = len(insights.get("patterns", []))
        trend_count = len(insights.get("trends", []))
        anomaly_count = len(insights.get("anomalies", []))
    
        metrics_data.extend([
            {
                "name": "Patterns Detected",
                "value": pattern_count,
                "description": "Number of repeating patterns identified in the graph"
            },
            {
                "name": "Trends Identified",
                "value": trend_count,
                "description": "Number of temporal trends identified in the data"
            },
            {
                "name": "Anomalies Found",
                "value": anomaly_count,
                "description": "Number of outliers and anomalies detected"
            }
        ])
    
        return {
            "type": "metrics_dashboard",
            "title": "Key Knowledge Graph Metrics",
            "description": "Summary of important metrics and statistics",
            "metrics": metrics_data
        }
    
    def _save_insights(self, insights: Dict[str, Any], entity_name: Optional[str] = None) -> str:
        """
        Save insights to a JSON file.
        
        Args:
            insights: Extracted insights
            entity_name: Optional entity name for the filename
            
        Returns:
            str: Path to the saved file
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if entity_name:
            filename = f"insights_{entity_name.replace(' ', '_')}_{timestamp}.json"
        else:
            filename = f"insights_global_{timestamp}.json"
            
        # Create file path
        output_path = os.path.join(self.output_dir, filename)
        
        # Save to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, ensure_ascii=False, indent=2)
            logger.info(f"Insights saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving insights: {e}")
            return ""
    
    def visualize_insights(self, insights_file: str) -> Dict[str, Any]:
        """
        Generate visualization outputs for insights.
        
        Args:
            insights_file: Path to the insights JSON file
            
        Returns:
            dict: Visualization configurations for different charts
        """
        logger.info(f"Generating visualizations for insights file: {insights_file}")
        
        # Load insights from file
        try:
            with open(insights_file, 'r', encoding='utf-8') as f:
                insights = json.load(f)
        except Exception as e:
            logger.error(f"Error loading insights file: {e}")
            return {"error": f"Failed to load insights file: {e}"}
        
        # Extract visualization data
        visualization_data = insights.get("visualization_data", {})
        
        # Generate chart configurations
        chart_configs = {
            "network_graph_config": self._generate_network_chart_config(
                visualization_data.get("network_graph", {})),
            "trend_charts_config": self._generate_trend_charts_config(
                visualization_data.get("trend_charts", {})),
            "anomaly_chart_config": self._generate_anomaly_chart_config(
                visualization_data.get("anomaly_charts", {})),
            "correlation_matrix_config": self._generate_correlation_matrix_config(
                visualization_data.get("correlation_matrix", {})),
            "metrics_dashboard_config": self._generate_metrics_dashboard_config(
                visualization_data.get("key_metrics", {}))
        }
        
        # Add insights summary
        key_findings = insights.get("key_findings", [])
        if key_findings:
            chart_configs["insights_summary"] = {
                "title": "Key Business Insights",
                "findings": key_findings
            }
        
        return chart_configs
    
    def _generate_network_chart_config(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration for network graph visualization.
        
        Args:
            network_data: Network visualization data
            
        Returns:
            dict: Chart configuration
        """
        # This would contain library-specific configuration for network graphs
        # For example, for D3.js force-directed graph:
        
        return {
            "type": "network",
            "title": network_data.get("title", "Entity Relationship Network"),
            "description": network_data.get("description", "Network visualization"),
            "data": network_data.get("data", {"nodes": [], "links": []}),
            "config": {
                "width": 800,
                "height": 600,
                "node_color_scale": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "link_color": "#999",
                "link_opacity": 0.6,
                "node_label_display": True,
                "force_strength": -300,
                "force_distance": 100,
                "force_charge": -200
            }
        }
    
    def _generate_trend_charts_config(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration for trend charts.
        
        Args:
            trend_data: Trend visualization data
            
        Returns:
            dict: Chart configuration
        """
        # This would contain configuration for time series charts
        
        return {
            "type": "line_chart",
            "title": trend_data.get("title", "Metric Trends Over Time"),
            "description": trend_data.get("description", "Trend visualization"),
            "datasets": trend_data.get("datasets", []),
            "config": {
                "width": 800,
                "height": 400,
                "x_axis_title": "Date",
                "y_axis_title": "Value",
                "show_legend": True,
                "animation": True,
                "line_styles": [
                    {"stroke": "#1f77b4", "strokeWidth": 2, "fill": "none"},
                    {"stroke": "#ff7f0e", "strokeWidth": 2, "fill": "none"},
                    {"stroke": "#2ca02c", "strokeWidth": 2, "fill": "none"},
                    {"stroke": "#d62728", "strokeWidth": 2, "fill": "none"}
                ],
                "tooltip": True
            }
        }
    
    def _generate_anomaly_chart_config(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration for anomaly visualization.
        
        Args:
            anomaly_data: Anomaly visualization data
            
        Returns:
            dict: Chart configuration
        """
        # This would contain configuration for scatter plots or other anomaly visualizations
        
        return {
            "type": "scatter_plot",
            "title": anomaly_data.get("title", "Metric Anomalies"),
            "description": anomaly_data.get("description", "Anomaly visualization"),
            "datasets": anomaly_data.get("datasets", []),
            "config": {
                "width": 800,
                "height": 400,
                "x_axis_title": "Entity",
                "y_axis_title": "Normalized Value",
                "show_legend": True,
                "point_styles": [
                    {"r": 5, "fill": "red", "fillOpacity": 0.7},
                    {"r": 5, "fill": "orange", "fillOpacity": 0.7},
                    {"r": 5, "fill": "yellow", "fillOpacity": 0.7}
                ],
                "reference_line": {
                    "y": 1.0,
                    "stroke": "#666",
                    "strokeDasharray": "5,5",
                    "label": "Average"
                },
                "tooltip": True
            }
        }
    
    def _generate_correlation_matrix_config(self, correlation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration for correlation matrix visualization.
        
        Args:
            correlation_data: Correlation visualization data
            
        Returns:
            dict: Chart configuration
        """
        # This would contain configuration for heatmaps or matrix visualizations
        
        return {
            "type": "correlation_matrix",
            "title": correlation_data.get("title", "Entity Correlations"),
            "description": correlation_data.get("description", "Correlation visualization"),
            "data": correlation_data.get("data", []),
            "config": {
                "width": 800,
                "height": 600,
                "color_scale": ["#d73027", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", 
                                "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850"],
                "cell_size": 30,
                "show_values": True,
                "margin": {"top": 100, "right": 100, "bottom": 100, "left": 100},
                "tooltip": True
            }
        }
    
    def _generate_metrics_dashboard_config(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration for metrics dashboard.
        
        Args:
            metrics_data: Metrics visualization data
            
        Returns:
            dict: Dashboard configuration
        """
        # This would contain configuration for a metrics dashboard
        
        return {
            "type": "metrics_dashboard",
            "title": metrics_data.get("title", "Key Knowledge Graph Metrics"),
            "description": metrics_data.get("description", "Summary metrics"),
            "metrics": metrics_data.get("metrics", []),
            "config": {
                "layout": "grid",
                "columns": 2,
                "card_styles": {
                    "background": "#f8f9fa",
                    "border": "1px solid #ddd",
                    "borderRadius": "5px",
                    "padding": "15px",
                    "margin": "10px",
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                },
                "value_styles": {
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "color": "#1f77b4"
                },
                "label_styles": {
                    "fontSize": "14px",
                    "color": "#555"
                }
            }
        }

# For testing/demonstration
if __name__ == "__main__":
    import sys
    from knowledge_graph.neo4j_manager import Neo4jManager
    
    # Check if entity name is provided
    entity_name = None
    if len(sys.argv) > 1:
        entity_name = sys.argv[1]
    
    # Initialize Neo4j manager
    neo4j_manager = Neo4jManager()
    neo4j_manager.connect()
    
    try:
        # Initialize insight extractor
        extractor = InsightExtractor(neo4j_manager)
        
        # Extract insights
        print(f"Extracting insights{' for ' + entity_name if entity_name else ''}")
        insights = extractor.extract_insights(entity_name)
        
        # Print summary
        if "error" in insights:
            print(f"Error: {insights['error']}")
        else:
            print(f"Extracted {len(insights.get('key_findings', []))} key findings")
            print(f"Found {len(insights.get('patterns', []))} patterns")
            print(f"Identified {len(insights.get('trends', []))} trends")
            print(f"Discovered {len(insights.get('correlations', []))} correlations")
            print(f"Detected {len(insights.get('anomalies', []))} anomalies")
            
            # Print key findings
            if insights.get("key_findings"):
                print("\nKey Findings:")
                for i, finding in enumerate(insights["key_findings"]):
                    print(f"{i+1}. {finding.get('title')}")
                    print(f"   {finding.get('explanation')}")
                    print(f"   Implications: {finding.get('business_implications')}")
    finally:
        # Close Neo4j connection
        neo4j_manager.close()