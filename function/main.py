import logging
from config import get_config
from gcp.resources.resources_handler import ResourcesHandler

import requests
CLIENT_ID = 'cEV3b6q2mMdoAYSnNfacikslsmw23nTx'
CLIENT_SECRET = 'X6OwSyjNe3hlJ42C5jRUQIGNRilxWO2bKVhsXxb54oliBPXkW3YKVtLYTykh8Jqr'

API_URL = 'https://api.getport.io/v1'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(event, context):
    logger.info("Load config")
    config = get_config(event, context)
    logger.info("Handling resources")
    resources_handler = ResourcesHandler(config, context)
    resources_handler.handle()
    logger.info("Exiting...")
