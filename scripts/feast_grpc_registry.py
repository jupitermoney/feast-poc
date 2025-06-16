import grpc
from feast.protos.feast.registry import RegistryServer_pb2
from feast.protos.feast.registry import RegistryServer_pb2_grpc
from feast.protos.feast.core import Entity_pb2
from feast.protos.feast.core import DataSource_pb2
from feast.protos.feast.core import FeatureService_pb2
from feast.protos.feast.core import FeatureView_pb2
from feast.protos.feast.core import OnDemandFeatureView_pb2
from feast.protos.feast.core import StreamFeatureView_pb2
from google.protobuf import empty_pb2


class FeastRegistryClient:
    def __init__(self, server_address: str = 'localhost:6570'):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = RegistryServer_pb2_grpc.RegistryServerStub(self.channel)

    def close(self):
        """Closes the gRPC channel."""
        self.channel.close()

    def list_entities(self, project_name: str, allow_cache: bool = False):
        """
        Lists all entities in a given project.
        """
        try:
            request = RegistryServer_pb2.ListEntitiesRequest(
                project=project_name,
                allow_cache=allow_cache
            )
            print(f"Attempting to list entities from project '{project_name}'...")
            response = self.stub.ListEntities(request)
            if response.entities:
                print("Successfully retrieved entities:")
                for entity in response.entities:
                    print(entity)
                return response.entities
            else:
                print(f"No entities found in project '{project_name}'.")
                return []
        except grpc.RpcError as e:
            print(f"Error calling ListEntities: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_entity(self, project_name: str, entity_name: str):
        """
        Retrieves a single entity from a given project.
        """
        try:
            request = RegistryServer_pb2.GetEntityRequest(
                project=project_name,
                name=entity_name
            )
            print(f"Attempting to get entity '{entity_name}' from project '{project_name}'...")
            response = self.stub.GetEntity(request)
            print("Successfully retrieved entity:")
            print(response)
            return response
        except grpc.RpcError as e:
            print(f"Error calling GetEntity: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def apply_entity(self, project_name: str, entity: Entity_pb2.Entity):
        """
        Applies (creates or updates) an entity.
        """
        try:
            request = RegistryServer_pb2.ApplyEntityRequest(
                project=project_name,
                entity=entity
            )
            print(f"Attempting to apply entity '{entity.name}' to project '{project_name}'...")
            self.stub.ApplyEntity(request)
            print(f"Successfully applied entity '{entity.name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling ApplyEntity: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def delete_entity(self, project_name: str, entity_name: str):
        """
        Deletes an entity.
        """
        try:
            request = RegistryServer_pb2.DeleteEntityRequest(
                project=project_name,
                name=entity_name
            )
            print(f"Attempting to delete entity '{entity_name}' from project '{project_name}'...")
            self.stub.DeleteEntity(request)
            print(f"Successfully deleted entity '{entity_name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling DeleteEntity: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def list_data_sources(self, project_name: str, allow_cache: bool = False):
        """
        Lists all data sources in a given project.
        """
        try:
            request = RegistryServer_pb2.ListDataSourcesRequest(
                project=project_name,
                allow_cache=allow_cache
            )
            print(f"Attempting to list data sources from project '{project_name}'...")
            response = self.stub.ListDataSources(request)
            if response.data_sources:
                print("Successfully retrieved data sources:")
                for ds in response.data_sources:
                    print(ds)
                return response.data_sources
            else:
                print(f"No data sources found in project '{project_name}'.")
                return []
        except grpc.RpcError as e:
            print(f"Error calling ListDataSources: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_data_source(self, project_name: str, data_source_name: str):
        """
        Retrieves a single data source from a given project.
        """
        try:
            request = RegistryServer_pb2.GetDataSourceRequest(
                project=project_name,
                name=data_source_name
            )
            print(f"Attempting to get data source '{data_source_name}' from project '{project_name}'...")
            response = self.stub.GetDataSource(request)
            print("Successfully retrieved data source:")
            print(response)
            return response
        except grpc.RpcError as e:
            print(f"Error calling GetDataSource: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def apply_data_source(self, project_name: str, data_source: DataSource_pb2.DataSource):
        """
        Applies (creates or updates) a data source.
        """
        try:
            request = RegistryServer_pb2.ApplyDataSourceRequest(
                project=project_name,
                data_source=data_source
            )
            print(f"Attempting to apply data source '{data_source.name}' to project '{project_name}'...")
            self.stub.ApplyDataSource(request)
            print(f"Successfully applied data source '{data_source.name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling ApplyDataSource: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
    
    def delete_data_source(self, project_name: str, data_source_name: str):
        """
        Deletes a data source.
        """
        try:
            request = RegistryServer_pb2.DeleteDataSourceRequest(
                project=project_name,
                name=data_source_name
            )
            print(f"Attempting to delete data source '{data_source_name}' from project '{project_name}'...")
            self.stub.DeleteDataSource(request)
            print(f"Successfully deleted data source '{data_source_name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling DeleteDataSource: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def list_feature_views(self, project_name: str, allow_cache: bool = False):
        """
        Lists all feature views in a given project.
        """
        try:
            request = RegistryServer_pb2.ListFeatureViewsRequest(
                project=project_name,
                allow_cache=allow_cache
            )
            print(f"Attempting to list feature views from project '{project_name}'...")
            response = self.stub.ListFeatureViews(request)
            if response.feature_views:
                print("Successfully retrieved feature views:")
                for fv in response.feature_views:
                    print(fv)
                return response.feature_views
            else:
                print(f"No feature views found in project '{project_name}'.")
                return []
        except grpc.RpcError as e:
            print(f"Error calling ListFeatureViews: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    
    def get_feature_view(self, project_name: str, feature_view_name: str):
        """
        Retrieves a single feature view from a given project.
        """
        try:
            request = RegistryServer_pb2.GetFeatureViewRequest(
                project=project_name,
                name=feature_view_name
            )
            print(f"Attempting to get feature view '{feature_view_name}' from project '{project_name}'...")
            response = self.stub.GetFeatureView(request)
            print("Successfully retrieved feature view:")
            print(response)
            return response
        except grpc.RpcError as e:
            print(f"Error calling GetFeatureView: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def apply_feature_view(self, project_name: str, feature_view: FeatureView_pb2.FeatureView):
        """
        Applies (creates or updates) a feature view.
        """
        try:
            request = RegistryServer_pb2.ApplyFeatureViewRequest(
                project=project_name,
                feature_view=feature_view
            )
            print(f"Attempting to apply feature view '{feature_view.name}' to project '{project_name}'...")
            self.stub.ApplyFeatureView(request)
            print(f"Successfully applied feature view '{feature_view.name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling ApplyFeatureView: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def delete_feature_view(self, project_name: str, feature_view_name: str):
        """
        Deletes a feature view.
        """
        try:
            request = RegistryServer_pb2.DeleteFeatureViewRequest(
                project=project_name,
                name=feature_view_name
            )
            print(f"Attempting to delete feature view '{feature_view_name}' from project '{project_name}'...")
            self.stub.DeleteFeatureView(request)
            print(f"Successfully deleted feature view '{feature_view_name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling DeleteFeatureView: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def get_stream_feature_view(self, project_name: str, stream_feature_view_name: str):
        """
        Retrieves a single stream feature view from a given project.
        """
        try:
            request = RegistryServer_pb2.GetStreamFeatureViewRequest(
                project=project_name,
                name=stream_feature_view_name
            )
            print(f"Attempting to get stream feature view '{stream_feature_view_name}' from project '{project_name}'...")
            response = self.stub.GetStreamFeatureView(request)
            print("Successfully retrieved stream feature view:")
            print(response)
            return response
        except grpc.RpcError as e:
            print(f"Error calling GetStreamFeatureView: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def list_stream_feature_views(self, project_name: str, allow_cache: bool = False):
        """
        Lists all stream feature views in a given project.
        """
        try:
            request = RegistryServer_pb2.ListStreamFeatureViewsRequest(
                project=project_name,
                allow_cache=allow_cache
            )
            print(f"Attempting to list stream feature views from project '{project_name}'...")
            response = self.stub.ListStreamFeatureViews(request)
            if response.stream_feature_views:
                print("Successfully retrieved stream feature views:")
                for sfv in response.stream_feature_views:
                    print(sfv)
                return response.stream_feature_views
            else:
                print(f"No stream feature views found in project '{project_name}'.")
                return []
        except grpc.RpcError as e:
            print(f"Error calling ListStreamFeatureViews: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_on_demand_feature_view(self, project_name: str, on_demand_feature_view_name: str):
        """
        Retrieves a single on-demand feature view from a given project.
        """
        try:
            request = RegistryServer_pb2.GetOnDemandFeatureViewRequest(
                project=project_name,
                name=on_demand_feature_view_name
            )
            print(f"Attempting to get on-demand feature view '{on_demand_feature_view_name}' from project '{project_name}'...")
            response = self.stub.GetOnDemandFeatureView(request)
            print("Successfully retrieved on-demand feature view:")
            print(response)
            return response
        except grpc.RpcError as e:
            print(f"Error calling GetOnDemandFeatureView: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def list_on_demand_feature_views(self, project_name: str, allow_cache: bool = False):
        """
        Lists all on-demand feature views in a given project.
        """
        try:
            request = RegistryServer_pb2.ListOnDemandFeatureViewsRequest(
                project=project_name,
                allow_cache=allow_cache
            )
            print(f"Attempting to list on-demand feature views from project '{project_name}'...")
            response = self.stub.ListOnDemandFeatureViews(request)
            if response.on_demand_feature_views:
                print("Successfully retrieved on-demand feature views:")
                for odfv in response.on_demand_feature_views:
                    print(odfv)
                return response.on_demand_feature_views
            else:
                print(f"No on-demand feature views found in project '{project_name}'.")
                return []
        except grpc.RpcError as e:
            print(f"Error calling ListOnDemandFeatureViews: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def apply_feature_service(self, project_name: str, feature_service: FeatureService_pb2.FeatureService):
        """
        Applies (creates or updates) a feature service.
        """
        try:
            request = RegistryServer_pb2.ApplyFeatureServiceRequest(
                project=project_name,
                feature_service=feature_service
            )
            print(f"Attempting to apply feature service '{feature_service.name}' to project '{project_name}'...")
            self.stub.ApplyFeatureService(request)
            print(f"Successfully applied feature service '{feature_service.name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling ApplyFeatureService: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def get_feature_service(self, project_name: str, feature_service_name: str):
        """
        Retrieves a single feature service from a given project.
        """
        try:
            request = RegistryServer_pb2.GetFeatureServiceRequest(
                project=project_name,
                name=feature_service_name
            )
            print(f"Attempting to get feature service '{feature_service_name}' from project '{project_name}'...")
            response = self.stub.GetFeatureService(request)
            print("Successfully retrieved feature service:")
            print(response)
            return response
        except grpc.RpcError as e:
            print(f"Error calling GetFeatureService: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def list_feature_services(self, project_name: str, allow_cache: bool = False):
        """
        Lists all feature services in a given project.
        """
        try:
            request = RegistryServer_pb2.ListFeatureServicesRequest(
                project=project_name,
                allow_cache=allow_cache
            )
            print(f"Attempting to list feature services from project '{project_name}'...")
            response = self.stub.ListFeatureServices(request)
            if response.feature_services:
                print("Successfully retrieved feature services:")
                for fs in response.feature_services:
                    print(fs)
                return response.feature_services
            else:
                print(f"No feature services found in project '{project_name}'.")
                return []
        except grpc.RpcError as e:
            print(f"Error calling ListFeatureServices: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def delete_feature_service(self, project_name: str, feature_service_name: str):
        """
        Deletes a feature service.
        """
        try:
            request = RegistryServer_pb2.DeleteFeatureServiceRequest(
                project=project_name,
                name=feature_service_name
            )
            print(f"Attempting to delete feature service '{feature_service_name}' from project '{project_name}'...")
            self.stub.DeleteFeatureService(request)
            print(f"Successfully deleted feature service '{feature_service_name}'.")
            return True
        except grpc.RpcError as e:
            print(f"Error calling DeleteFeatureService: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

if __name__ == "__main__":
    client = FeastRegistryClient()
    project = "my_project"
    entity_name = "user_id"
    data_source_name = "my_data_source"
    feature_view_name = "my_feature_view"
    stream_feature_view_name = "my_stream_feature_view"
    on_demand_feature_view_name = "my_on_demand_feature_view"
    feature_service_name = "my_feature_service"

    # Example calls for each API

    # Entity APIs
    print("\n--- Entity APIs ---")
    client.list_entities(project)
    # client.get_entity(project, entity_name)
    # For apply_entity, you would need to construct an Entity_pb2.Entity object
    # example_entity = Entity_pb2.Entity(name=entity_name, description="Example entity")
    # client.apply_entity(project, example_entity)
    # client.delete_entity(project, entity_name)

    # Data Source APIs
    print("\n--- Data Source APIs ---")
    client.list_data_sources(project)
    # client.get_data_source(project, data_source_name)
    # For apply_data_source, you would need to construct a DataSource_pb2.DataSource object
    # example_data_source = DataSource_pb2.DataSource(name=data_source_name)
    # client.apply_data_source(project, example_data_source)
    # client.delete_data_source(project, data_source_name)

    # Feature View APIs
    print("\n--- Feature View APIs ---")
    client.list_feature_views(project)
    # client.get_feature_view(project, feature_view_name)
    # For apply_feature_view, you would need to construct a FeatureView_pb2.FeatureView object
    # example_feature_view = FeatureView_pb2.FeatureView(name=feature_view_name)
    # client.apply_feature_view(project, example_feature_view)
    # client.delete_feature_view(project, feature_view_name)

    # Stream Feature View APIs
    print("\n--- Stream Feature View APIs ---")
    client.list_stream_feature_views(project)
    # client.get_stream_feature_view(project, stream_feature_view_name)

    # On Demand Feature View APIs
    print("\n--- On Demand Feature View APIs ---")
    client.list_on_demand_feature_views(project)
    # client.get_on_demand_feature_view(project, on_demand_feature_view_name)

    # Feature Service APIs
    print("\n--- Feature Service APIs ---")
    client.list_feature_services(project)
    # client.get_feature_service(project, feature_service_name)
    # For apply_feature_service, you would need to construct a FeatureService_pb2.FeatureService object
    # example_feature_service = FeatureService_pb2.FeatureService(name=feature_service_name)
    # client.apply_feature_service(project, example_feature_service)
    # client.delete_feature_service(project, feature_service_name)

    client.close()