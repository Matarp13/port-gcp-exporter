import copy
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.protobuf.json_format import MessageToJson
from google.cloud import asset_v1

import function.consts as consts
from function.port.entities import create_entities_json

logger = logging.getLogger(__name__)

#TODO - Remove after replacing to lambda
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../examples/config/matars-project-a5bdbb42a6f0.json"


class ResourceHandler:
    def __init__(self, resource_config, port_client, default_region, project_id):
        self.resource_config = copy.deepcopy(resource_config)
        self.port_client = port_client
        self.kind = self.resource_config.get('kind', '')
        selector = self.resource_config.get('selector', {})
        self.selector_query = selector.get('query')
        self.selector_gcp = selector.get('gcp', {})
        self.regions = self.selector_gcp.get('regions', [default_region])
        # self.regions_config = self.selector_gcp.get('regions_config', {})
        # self.next_token = self.selector_gcp.get('next_token', '')
        self.mappings = self.resource_config.get('port', {}).get('entity', {}).get('mappings', [])
        self.gcp_entities = set()
        self.project_id = project_id
        # self.skip_delete = False

    def handle(self):
        # Goes over every region listed in the config
        for region in list(self.regions):
            scope = f'projects/{self.project_id}/locations/{region}/{self.kind}'
            gcp_cloudassets_client = asset_v1.AssetServiceClient(scope=scope)
            # resources_models = self.regions_config.get(region, {}).get('resources_models', ["{}"])
            # for resource_model in list(resources_models):
            #     logger.info(f"List kind: {self.kind}, region: {region}, resource_model: {resource_model}")
            #     self.next_token = '' if self.next_token is None else self.next_token
            # while self.next_token is not None:
                # list_resources_params = {'TypeName': self.kind, 'ResourceModel': resource_model}
                # if self.next_token:
                #     list_resources_params['NextToken'] = self.next_token

            try:
                response = gcp_cloudassets_client.list_assets(
                    request={
                        "parent": "projects/{}".format(self.project_id),
                        "read_time": None,
                        "asset_types": self.kind,
                        "content_type": "RESOURCE",
                        "page_size": consts.GOOGLE_API_PAGE_SIZE,
                    }
                )

            except Exception as e:
                logger.error(
                    f"Failed list kind: {self.kind}, region: {region} {e}")
                # self.skip_delete = True
                # self.next_token = None
                break

                self._organize_entities_list(response)

                    # self.next_token = response.get('NextToken')
                    # TODO - aad close to timeout handling in gcp
                    # if self.lambda_context.get_remaining_time_in_millis() < consts.REMAINING_TIME_TO_REINVOKE_THRESHOLD:
                    #     # Lambda timeout is too close, should return checkpoint for next run
                    #     return self._handle_close_to_timeout(resources_models, resource_model, region)

                # self._cleanup_resources_models(resources_models, resource_model, region)

            self._cleanup_regions(region)

        # return {'gcp_entities': self.gcp_entities, 'next_resource_config': None, 'skip_delete': self.skip_delete}
            return {'gcp_entities': self.gcp_entities}

    def _organize_entities_list(self, list_response):
        with ThreadPoolExecutor(max_workers=consts.MAX_UPSERT_WORKERS) as executor:
            futures = [executor.submit(self.handle_single_resource_item,
                                       resource) for resource in list_response]
            for completed_future in as_completed(futures):
                result = completed_future.result()
                self.gcp_entities.update(result.get('gcp_entities', set()))
                # self.skip_delete = result.get('skip_delete', False) if not self.skip_delete else self.skip_delete

    def handle_single_resource_item(self, gcp_, resource, action_type='upsert'):
        entities = []
        # skip_delete = False
        try:
            resource_obj = MessageToJson(resource._pb, including_default_value_fields=True)

            if action_type == 'upsert':
                logger.info(f"Get resource for kind: {self.kind}, resource id: {resource_obj.id}")
            elif action_type == 'delete':
                resource_obj = {"identifier": resource_obj.id}  # Entity identifier to delete

            entities = create_entities_json(resource_obj, self.selector_query, self.mappings, action_type)
        except Exception as e:
            logger.error(f"Failed to extract or transform resource id: {resource_obj.id}, kind: {self.kind}, error: {e}")
            # skip_delete = True

        gcp_entities = self._handle_entities(entities, action_type)

        # return {'gcp_entities': gcp_entities, 'skip_delete': skip_delete}
        return {'gcp_entities': gcp_entities}

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

    # def _handle_close_to_timeout(self, resources_models, current_resource_model, region):
    #     if self.next_token:
    #         self.selector_aws['next_token'] = self.next_token
    #     else:
    #         self.selector_aws.pop('next_token', None)
    #         resources_models = self._cleanup_resources_models(resources_models, current_resource_model, region)
    #         if not resources_models:
    #             self._cleanup_regions(region)
    #             if not self.regions:  # Nothing left to sync
    #                 return {'aws_entities': self.aws_entities, 'next_resource_config': None,
    #                         'skip_delete': self.skip_delete}
    #
    #     if 'selector' not in self.resource_config:
    #         self.resource_config['selector'] = {}
    #     self.resource_config['selector']['aws'] = self.selector_aws
    #
    #     return {'aws_entities': self.aws_entities, 'next_resource_config': self.resource_config,
    #             'skip_delete': self.skip_delete}

    # def _cleanup_resources_models(self, resources_models, current_resource_model, region):
    #     resources_models.remove(current_resource_model)
    #     if region not in self.regions_config:
    #         self.regions_config[region] = {}
    #     self.regions_config[region]['resources_models'] = resources_models
    #     self.selector_aws['regions_config'] = self.regions_config
    #
    #     return resources_models

    def _cleanup_regions(self, region):
        self.regions.remove(region)
        # self.regions_config.pop(region, None)
        self.selector_gcp['regions'] = self.regions
        # self.selector_aws['regions_config'] = self.regions_config