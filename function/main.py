import logging
import json
from config import get_config
from gcp.resources.resources_handler import ResourcesHandler


logger = logging.getLogger()
logger.setLevel(logging.INFO)

    # data = {
    #     "event_id": "01234567-89ab-cdef-0123-456789abcdef",
    #     "timestamp": "2023-03-28T12:34:56.789Z",
    #     "event_type": "google.pubsub.topic.publish",
    #     "resource": {
    #         "service": "pubsub.googleapis.com",
    #         "name": "projects/my-project/topics/my-topic",
    #         "type": "type.googleapis.com/google.pubsub.v1.PubsubMessage",
    #         "metadata": {
    #             "projectId": "matars-project",
    #             "region": "us-central1"
    #         }
    #     }
    # }


def main(event, context):

    # TODO - Remove to get it from the terraform parameters
    import os
    os.environ['PORT_CLIENT_ID_KEY'] = "client-id"
    os.environ['PORT_CLIENT_SECRET_KEY'] = "client-secret"
    os.environ['BUCKET_NAME'] = 'port-exporter'
    os.environ['CONFIG_JSON_FILE_KEY'] = 'config.json'

    logger.info("Load config")
    config = get_config(event, context)
    print("config: ", config)
    logger.info("Handling resources")
    resources_handler = ResourcesHandler(config, context)
    resources_handler.handle()
    logger.info("Exiting...")
