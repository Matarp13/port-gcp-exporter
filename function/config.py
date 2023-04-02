import json
import logging
import os

from google.cloud import storage
from google.cloud import secretmanager

#TODO - Remove consts to come dynamically
# PORT_CLIENT_ID_KEY = "client-id"
# PORT_CLIENT_SECRET_KEY = "client-secret"
# os.environ['BUCKET_NAME'] = 'port-exporter'
# os.environ['CONFIG_JSON_FILE_KEY'] = 'config.json'
# key_path = '../examples/config/matars-project-a5bdbb42a6f0.json'

logger = logging.getLogger(__name__)

def get_config(event, context):
    logger.info("Load resources config from s3")
    resources_config = _get_resources_config(event, context)
    logger.info("Load port credentials from secrets manager")
    project_id = context.resource['name'].split('/')[1]
    port_creds = _get_port_credentials(event, project_id)
    return {**{'event': event}, **resources_config, **port_creds}


def _get_resources_config(event, context):
    gcp_storage_client = storage.Client()
    bucket_name = os.getenv('BUCKET_NAME')
    original_config_file_key = os.getenv('CONFIG_JSON_FILE_KEY')

    config_from_s3 = json.loads(gcp_storage_client.bucket(bucket_name).blob(original_config_file_key).download_as_string())

    assert 'resources' in config_from_s3, "resources key is missing from config file json"
    s3_config = {'bucket_name': bucket_name}

    return {**config_from_s3, **s3_config}


def _get_port_credentials(event, project_id):
    gcp_secretmanager_client = secretmanager.SecretManagerServiceClient()

    port_client_id_key = os.environ['PORT_CLIENT_ID_KEY']
    port_client_secret_key = os.environ['PORT_CLIENT_SECRET_KEY']

    # Get the name of the secret you want to access
    client_id_name = f"projects/{project_id}/secrets/{port_client_id_key}/versions/latest"
    client_secret_name = f"projects/{project_id}/secrets/{port_client_secret_key}/versions/latest"

    # Access the secret
    port_client_secret = gcp_secretmanager_client.access_secret_version(name=client_secret_name).payload.data.decode('UTF-8')
    port_client_id = gcp_secretmanager_client.access_secret_version(name=client_id_name).payload.data.decode('UTF-8')

    if event.get('port_client_id'):
        return {**{key: event.get(key) for key in ['port_client_id', 'port_client_secret', 'port_api_url']},
                **{'keep_cred': True}}

    return {'port_client_id': port_client_id, 'port_client_secret': port_client_secret}
