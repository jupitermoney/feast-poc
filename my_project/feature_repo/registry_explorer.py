import json
from feast import FeatureStore

class FeastRegistryExplorer:
    def __init__(self, repo_path: str):
        """
        Initializes the FeastRegistryExplorer with the path to the feature repository.
        """
        # FeatureStore expects the path to the repository, which contains feature_store.yaml
        self.fs = FeatureStore(repo_path=repo_path)
        print(f"\nInitialized Feast FeatureStore for repository: {repo_path}")

    def print_entities(self):
        """
        Retrieves and prints all entities defined in the Feast Registry.
        """
        print("\n--- Entities ---")
        entities = self.fs.list_entities()
        if entities:
            for entity in entities:
                print(entity) # Print the object directly
        else:
            print("No entities found.")

    def print_feature_views(self):
        """
        Retrieves and prints all feature views defined in the Feast Registry.
        """
        print("\n--- Feature Views ---")
        feature_views = self.fs.list_feature_views()
        if feature_views:
            for fv in feature_views:
                print(fv) # Print the object directly
        else:
            print("No feature views found.")

    def print_data_sources(self):
        """
        Retrieves and prints all data sources defined in the Feast Registry.
        """
        print("\n--- Data Sources ---")
        data_sources = self.fs.list_data_sources()
        if data_sources:
            for ds in data_sources:
                print(ds) # Print the object directly
        else:
            print("No data sources found.")

if __name__ == "__main__":
    # The repo_path should point to the directory containing feature_store.yaml.
    # If you run this script from 'my_project', then '.' is correct for 'feature_repo'.
    repo_path = "." # Corrected path relative to where you run this script

    explorer = FeastRegistryExplorer(repo_path)

    explorer.print_entities()
    explorer.print_feature_views()
    explorer.print_data_sources()