import logging
import json
from config import get_config
from gcp.resources.resources_handler import ResourcesHandler


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(event, context):
    logger.info("Load config")
    config = get_config(event, context)
    logger.info("Handling resources")
    resources_handler = ResourcesHandler(config, context)
    resources_handler.handle()
    logger.info("Exiting...")
