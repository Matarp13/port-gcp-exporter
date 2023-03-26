import json
import logging
import os

from google.cloud import storage
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials

#TODO - Remove consts to come dynamically
PROJECT_ID = "642420321411"
PORT_CLIENT_ID_KEY = "client-id"
PORT_CLIENT_SECRET_KEY = "client-secret"
os.environ['BUCKET_NAME'] = 'port-exporter'
os.environ['CONFIG_JSON_FILE_KEY'] = 'config.json'

logger = logging.getLogger(__name__)

key_path = '../examples/config/matars-project-a5bdbb42a6f0.json'

# TODO - Change it to no service account, need to be ran from GCP Function with permissions
creds = Credentials.from_service_account_file(key_path)
gcp_secretmanager_client = secretmanager.SecretManagerServiceClient(credentials=creds)
gcp_storage_client = storage.Client(credentials=creds)


# TODO - When in gcp function, replace to this
# gcp_secretmanager_client = secretmanager.SecretManagerServiceClient()
# gcp_storage_client = storage.Client()

def get_config(event, lambda_context):
    logger.info("Load resources config from s3")
    resources_config = _get_resources_config(event, lambda_context)
    logger.info("Load port credentials from secrets manager")
    port_creds = _get_port_credentials(event)
    return {**{'event': event}, **resources_config, **port_creds}


def _get_resources_config(event, lambda_context):
    bucket_name = os.getenv('BUCKET_NAME')
    original_config_file_key = os.getenv('CONFIG_JSON_FILE_KEY')
    # next_config_file_key = event.get('next_config_file_key')

    # # Not supposed to happen. Just make sure to not accept the original config as next config, so it won't get deleted
    # assert next_config_file_key != original_config_file_key, "next_config_file_key must not equal CONFIG_JSON_FILE_KEY"
    #
    # config_json_file_key = next_config_file_key or original_config_file_key

    config_from_s3 = json.loads(gcp_storage_client.bucket(bucket_name).blob(original_config_file_key).download_as_string())

    assert 'resources' in config_from_s3, "resources key is missing from config file json"

    # if next_config_file_key:  # In case it's a re-invoked lambda
    #     # Clean config state from s3 after reading it
    #     try:
    #         aws_s3_client.delete_object(Bucket=bucket_name, Key=next_config_file_key)
    #     except Exception as e:
    #         logger.warning(f"Failed to clean config state, bucket: {bucket_name}, key: {next_config_file_key}; {e}")
    # else:
    #     next_config_file_key = os.path.join(os.path.dirname(original_config_file_key), lambda_context.aws_request_id,
    #                                         "config.json")

    # s3_config = {'bucket_name': bucket_name, 'next_config_file_key': next_config_file_key}

    # return {**config_from_s3, **s3_config}
    return {**config_from_s3}


def _get_port_credentials(event):
    # Get the name of the secret you want to access
    client_secret_name = f"projects/{PROJECT_ID}/secrets/{PORT_CLIENT_SECRET_KEY}/versions/latest"
    client_id_name = f"projects/{PROJECT_ID}/secrets/{PORT_CLIENT_ID_KEY}/versions/latest"

    # Access the secret
    port_client_secret = gcp_secretmanager_client.access_secret_version(name=client_secret_name).payload.data.decode('UTF-8')
    port_client_id = gcp_secretmanager_client.access_secret_version(name=client_id_name).payload.data.decode('UTF-8')

    # TODO: Understand what event means here
    # if event.get('port_client_id'):
    #     return {**{key: event.get(key) for key in ['port_client_id', 'port_client_secret', 'port_api_url']},
    #             **{'keep_cred': True}}

    # port_creds = json.loads(aws_secretsmanager_client.get_secret_value(SecretId=secret_arn).get('SecretString', '{}'))
    return {'port_client_id': port_client_id, 'port_client_secret': port_client_secret}