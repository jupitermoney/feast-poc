from datetime import timedelta
import json
from typing import Dict, List, Any

from feast import (
    Entity,
    FeatureView,
    Field,
    FileSource,
    Project,
    FeatureStore,
)
from feast.types import Float32, Float64, Int64, String, Int32

def get_feast_type(feature_type: str):
    """Map feature types to Feast types"""
    type_mapping = {
        "string": String,
        "int": Int64,
        "float": Float64,
        "double": Float64,
        "boolean": Int32,
    }
    return type_mapping.get(feature_type.lower(), String)

def create_feature_store_components(job_json_path: str, repo_path: str = "."):
    """
    Dynamically create and register Feast components based on feature computation job JSON
    
    Args:
        job_json_path: Path to the feature computation job JSON file
        repo_path: Path to the Feast repository
    """
    # Initialize feature store
    store = FeatureStore(repo_path=repo_path)
    
    # Read the feature computation job JSON
    with open(job_json_path, 'r') as f:
        job_config = json.load(f)
    
    # Create project
    project = Project(
        name=job_config.get("name", "default_project"),
        description=job_config.get("metadata", {}).get("description", "Dynamically created project")
    )
    
    # Create entity from the job config
    entity = Entity(
        name=job_config.get("entityKeyColumn", "mmuuid"),
        join_keys=[job_config.get("entityKeyColumn", "mmuuid")],
        description=f"Entity for {job_config.get('name', 'default_project')}"
    )
    entities = {entity.name: entity}
    
    # Create source from the job config
    source = FileSource(
        name=f"{job_config.get('name', 'default')}_source",
        path=job_config.get("sourceTableName", ""),
        timestamp_field="transactiondatetime",  # Based on your JSON, this seems to be the timestamp field
        created_timestamp_column="created"
    )
    sources = {source.name: source}
    
    # Create feature views from transformations
    feature_views = []
    features_by_entity = {}
    
    # First pass: collect all features by entity
    for transformation in job_config.get("transformations", []):
        entity_name = transformation.get("entity")
        if entity_name not in features_by_entity:
            features_by_entity[entity_name] = []
        
        feature = {
            "name": transformation.get("featureName"),
            "type": "string",  # Default type, you might want to infer this from the expression
            "description": f"Feature: {transformation.get('featureName')}",
            "persist": transformation.get("persist", "online")
        }
        features_by_entity[entity_name].append(feature)
    
    # Second pass: create feature views for each entity
    for entity_name, features in features_by_entity.items():
        # Only create feature views for features that should be persisted online
        online_features = [f for f in features if f["persist"] == "online"]
        if online_features:
            schema = [
                Field(
                    name=feature["name"],
                    dtype=get_feast_type(feature["type"]),
                    description=feature["description"]
                )
                for feature in online_features
            ]
            
            feature_view = FeatureView(
                name=f"{entity_name}_features",
                entities=[entities[entity.name]],  # Using the main entity
                ttl=timedelta(days=1),
                schema=schema,
                online=True,
                source=source,
                tags={"team": "feature_platform"}
            )
            feature_views.append(feature_view)
    
    # Apply all components to the feature store
    store.apply(
        [project],
        list(entities.values()),
        feature_views,
        list(sources.values())
    )
    
    return store

# Example usage:
if __name__ == "__main__":
    store = create_feature_store_components("feature_computation_job.json") 