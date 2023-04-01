PORT_API_URL = 'https://api.getport.io/v1'
PORT_GCP_EXPORTER_NAME = "port-gcp-exporter"
MAX_UPSERT_WORKERS = 2
MAX_DELETE_WORKERS = 5
ASSET_TYPES = [
        "storage.googleapis.com/Bucket",
        'pubsub.googleapis.com/Topic',
        'compute.googleapis.com/Instance'
    ]
GOOGLE_API_PAGE_SIZE = 100
GCP_EXPORTER_VERSION = 0.1