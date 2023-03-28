PORT_API_URL = 'https://api.getport.io/v1'
PORT_AWS_EXPORTER_NAME = "port-aws-exporter"
MAX_UPSERT_WORKERS = 2
MAX_DELETE_WORKERS = 5
REMAINING_TIME_TO_REINVOKE_THRESHOLD = 1000 * 60 * 5  # 5 minutes
ASSET_TYPES = [
        "storage.googleapis.com/Bucket",
        'pubsub.googleapis.com/Topic',
        'compute.googleapis.com/Instance'
    ]
GOOGLE_API_PAGE_SIZE = 1000