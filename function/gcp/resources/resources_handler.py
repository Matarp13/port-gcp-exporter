import json
import logging
from concurrent.futures import ThreadPoolExecutor
import os
import consts as consts
from gcp.resources.resource_handler import ResourceHandler
from google.cloud import asset_v1
from port.client import PortClient
import jq

logger = logging.getLogger(__name__)


class ResourcesHandler:
    def __init__(self, config, context):
        self.config = config
        self.context = context
        # split_arn = context.invoked_function_arn.split(':')
        self.region = os.environ.get('FUNCTION_REGION')
        self.project_id = context.resource['name'].split('/')[1]
        self.user_id = f"accountid/{self.project_id} region/{self.region}"
        port_client_id = self.config.get('port_client_id') if self.config.get('keep_cred') else self.config.pop(
            'port_client_id')
        port_client_secret = self.config.get('port_client_secret') if self.config.get('keep_cred') else self.config.pop(
            'port_client_secret')
        self.port_client = PortClient(port_client_id, port_client_secret,
                                      user_agent=f"{consts.PORT_GCP_EXPORTER_NAME}/{consts.GCP_EXPORTER_VERSION} ({self.user_id})",
                                      api_url=self.config.get('port_api_url', consts.PORT_API_URL))
        self.event = self.config.get('event')
        self.bucket_name = self.config['bucket_name']
        self.gcp_entities = set(self.config.get('gcp_entities', []))
        self.resources_config = self.config['resources']
        self.skip_delete = self.config.get('skip_delete', False)

    def handle(self):
        if self.event and self.event.get('data') :  # Single events from SQS
            logger.info("Handle events from GCP Pub/Sub")
            for record in self.event.get('data'):
                try:
                    self._handle_single_resource(json.loads(record))
                except Exception as e:
                    logger.error(f"Failed to handle event: {self.event}, error: {e}")
            return

        logger.info("Starting upsert of GCP resources to Port")

        self._upsert_resources()
        logger.info("Done upsert of GCP resources to Port")

        if not self.skip_delete:
            logger.info("Starting delete process of stale resources from Port")
            self._delete_stale_resources()
            logger.info("Done deleting stale resources from Port")

        logger.info("Done handling your resources")

    def _upsert_resources(self):
        for resource in self.resources_config:
            resource_handler = ResourceHandler(resource, self.port_client, self.region, self.project_id)
            result = resource_handler.handle()
            self.gcp_entities.update(result.get('gcp_entities', set()))

            self.skip_delete = result.get('skip_delete', False) if not self.skip_delete else self.skip_delete

    def _handle_single_resource(self, resource):
        assert 'identifier' in resource, "Event must include 'identifier'"
        assert 'region' in resource, "Event must include 'region'"
        region = jq.first(resource['region'], resource)
        identifier = jq.first(resource['identifier'], resource)

        action_type = str(jq.first(resource.get('action', '"upsert"'), resource)).lower()
        assert action_type in ['upsert', 'delete'], f"Action should be one of 'upsert', 'delete'"

        resource_config = [resource_config for resource_config in self.resources_config
                            if resource_config['kind'] == resource['resource_type'] and resource_config['identifier'] == identifier]
        assert resource_config, f"Resource config not found for kind: {resource['resource_type']}"

        project_scope = f'projects/{self.project_id}'
        gcp_request = {"scope": project_scope,
                       "query": f'resourceProperties.id={identifier}',
                       "asset_types": [self.kind],
                       "page_size": consts.GOOGLE_API_PAGE_SIZE}

        try:
            gcp_cloudassets_client = asset_v1.AssetServiceClient()
            response = gcp_cloudassets_client.search_all_resources(request=gcp_request)
        except Exception as e:
            logger.error(f"Failed to extract or transform resource: {identifier}, kind: {self.kind}, error: {e}")

        for resource in response:
            resource_handler = ResourceHandler(resource_config, self.port_client, self.region, self.project_id)
            resource_handler.handle_single_resource_item(resource, identifier, action_type)

    def _delete_stale_resources(self):
        query = {"combinator": "and",
                 "rules": [{"property": "$datasource", "operator": "contains", "value": consts.PORT_GCP_EXPORTER_NAME},
                           {"property": "$datasource", "operator": "contains", "value": self.user_id}]}
        port_entities = self.port_client.search_entities(query)

        with ThreadPoolExecutor(max_workers=consts.MAX_DELETE_WORKERS) as executor:
            executor.map(self.port_client.delete_entity,
                         [entity for entity in port_entities
                          if f"{entity.get('blueprint')};{entity.get('identifier')}" not in self.gcp_entities])