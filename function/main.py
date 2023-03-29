import logging
import json
from config import get_config
from gcp.resources.resources_handler import ResourcesHandler

import requests
CLIENT_ID = 'cEV3b6q2mMdoAYSnNfacikslsmw23nTx'
CLIENT_SECRET = 'X6OwSyjNe3hlJ42C5jRUQIGNRilxWO2bKVhsXxb54oliBPXkW3YKVtLYTykh8Jqr'

API_URL = 'https://api.getport.io/v1'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

data = {
    "event_id": "01234567-89ab-cdef-0123-456789abcdef",
    "timestamp": "2023-03-28T12:34:56.789Z",
    "event_type": "google.pubsub.topic.publish",
    "resource": {
        "service": "pubsub.googleapis.com",
        "name": "projects/my-project/topics/my-topic",
        "type": "type.googleapis.com/google.pubsub.v1.PubsubMessage",
        "metadata": {
            "projectId": "matars-project",
            "region": "us-central1"
        }
    }
}

context = json.dumps(data)


def main(event, context):
    logger.info("Load config")
    config = get_config(event, context)
    print("config: ", config)
    logger.info("Handling resources")
    resources_handler = ResourcesHandler(config, context)
    resources_handler.handle()
    logger.info("Exiting...")


main(None, data)
