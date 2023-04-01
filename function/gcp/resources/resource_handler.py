import copy
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.protobuf.json_format import MessageToDict
from google.cloud import asset_v1
import consts as consts
from port.entities import create_entities_json

logger = logging.getLogger(__name__)


class ResourceHandler:
    def __init__(self, resource_config, port_client, default_region, project_id):
        self.resource_config = copy.deepcopy(resource_config)
        self.port_client = port_client
        self.kind = self.resource_config.get('kind', '')
        selector = self.resource_config.get('selector', {})
        self.selector_query = selector.get('query')
        self.selector_gcp = selector.get('gcp', {})
        self.regions = self.selector_gcp.get('regions', [default_region])
        self.next_token = self.selector_gcp.get('next_token', '')
        self.mappings = self.resource_config.get('port', {}).get('entity', {}).get('mappings', [])
        self.gcp_entities = set()
        self.project_id = project_id
        self.skip_delete = False

    def _organize_entities_list(self, list_response):
        with ThreadPoolExecutor(max_workers=consts.MAX_UPSERT_WORKERS) as executor:
            futures = [executor.submit(self.handle_single_resource_item,
                                       resource) for resource in list_response]
            for completed_future in as_completed(futures):
                result = completed_future.result()
                self.gcp_entities.update(result.get('gcp_entities', set()))
                self.skip_delete = result.get('skip_delete', False) if not self.skip_delete else self.skip_delete

    def handle(self):

        for region in list(self.regions):
            project_scope = f'projects/{self.project_id}'
            gcp_cloudassets_client = asset_v1.AssetServiceClient()
            is_first_resource = True

            while self.next_token or is_first_resource:
                is_first_resource = False
                gcp_request = {"scope": project_scope,
                               "query": f"location={region}",
                               "asset_types": [self.kind],
                               "page_size": consts.GOOGLE_API_PAGE_SIZE}

                if self.next_token:
                    gcp_request['page_token'] = self.next_token

                try:
                    response = gcp_cloudassets_client.search_all_resources(request=gcp_request)
                    self.next_token = response.next_page_token

                except Exception as e:
                    logger.error(
                        f"Failed list kind: {self.kind}, region: {region} {e}")
                    self.skip_delete = True
                    self.next_token = None
                    break

                self._organize_entities_list(response)

            # return {'gcp_entities': self.gcp_entities, 'next_resource_config': None, 'skip_delete': self.skip_delete}
            return {'gcp_entities': self.gcp_entities, 'skip_delete': self.skip_delete}

    def handle_single_resource_item(self, resource, action_type='upsert'):
        entities = []
        skip_delete = False
        try:
            resource_obj = MessageToDict(resource._pb, including_default_value_fields=True)
            resource_name = resource_obj.get('name')

            if action_type == 'upsert':
                logger.info(f"Get resource for kind: {self.kind}, resource id: {resource_name}")
            elif action_type == 'delete':
                resource_obj = {"identifier": resource_name}  # Entity identifier to delete

            entities = create_entities_json(resource_obj, self.selector_query, self.mappings, action_type)
        except Exception as e:
            logger.error(f"Failed to extract or transform resource: {resource_name}, kind: {self.kind}, error: {e}")
            skip_delete = True

        gcp_entities = self._handle_entities(entities, action_type)

        return {'gcp_entities': gcp_entities, 'skip_delete': skip_delete}

    def _handle_entities(self, entities, action_type='upsert'):
        gcp_entities = set()
        for entity in entities:
            blueprint_id = entity.get('blueprint')
            entity_id = entity.get('identifier')

            gcp_entities.add(f"{blueprint_id};{entity_id}")

            try:
                if action_type == 'upsert':
                    self.port_client.upsert_entity(entity)
                elif action_type == 'delete':
                    self.port_client.delete_entity(entity)
            except Exception as e:
                logger.error(
                    f"Failed to handle entity: {entity_id} of blueprint: {blueprint_id}, action: {action_type}; {e}")

        return gcp_entities
