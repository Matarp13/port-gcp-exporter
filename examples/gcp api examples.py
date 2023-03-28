import os
from google.cloud import compute_v1, pubsub_v1, storage
from google.protobuf.json_format import MessageToJson
from google.oauth2 import service_account
from google.cloud import asset_v1
import json

import requests
CLIENT_ID = 'cEV3b6q2mMdoAYSnNfacikslsmw23nTx'
CLIENT_SECRET = 'X6OwSyjNe3hlJ42C5jRUQIGNRilxWO2bKVhsXxb54oliBPXkW3YKVtLYTykh8Jqr'

API_URL = 'https://api.getport.io/v1'

# def hello_world(request):
#   credentials = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET}
#
#   token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
#
#   access_token = token_response.json()['accessToken']
#
#   # You can now use the value in access_token when making further requests
#
#   headers = {
#       'Authorization': f'Bearer {access_token}'
#   }
#
#   blueprint_id = 'microservice'
#
#   entity = {
#     "identifier": "microservice2",
#     "title": "Matars Go service",
#     "properties": {
#       "language": "GO",
#       "url": "https://matarsthePrince.peles"
#     },
#     "relations": {}
#   }
#
#   response = requests.post(f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true', json=entity, headers=headers)
#   print(response.content)
# hello_world(None)

# response.json() contains the content of the resulting entity

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../examples/config/matars-project-a5bdbb42a6f0.json"
project_id = "matars-project"
project_path = f"projects/{project_id}"


def get_gcp_data():
    # Set up authentication credentials

    # Set up Compute Engine client
    compute_client = compute_v1.InstancesClient()
    zone = "us-east1-b"
    vm_instances = []

    # Get list of VM instances in project and zone
    request = compute_v1.ListInstancesRequest(
        project=project_id,
        zone=zone
    )
    response = compute_client.list(request)
    for instance in response:
        vm_instances.append(instance)

    # Set up Pub/Sub client
    pubsub_client = pubsub_v1.PublisherClient()

    topics = []


    # # Get list of Pub/Sub topics in project

    for topic in pubsub_client.list_topics(request={"project": project_path}):
        topics.append(topic)



    # Set up Storage client
    storage_client = storage.Client(project=project_id)
    buckets = []

    # Get list of Storage buckets in project
    for bucket in storage_client.list_buckets():
        buckets.append(json.dumps(bucket._properties))


    print(topics)
    # Return data as dictionary
    # return {
    #     "VM instances": vm_instances,
    #     "Pub/Sub topics": topic_names,
    #     "Storage buckets": bucket_names
    # }

# get_gcp_data()

def get_gcp_assets():
    from google.cloud import asset_v1

    asset_types = [
        "storage.googleapis.com/Bucket",
        'pubsub.googleapis.com/Topic',
        'compute.googleapis.com/Instance'
    ]
    # TODO project_id = 'Your Google Cloud Project ID'
    # TODO asset_types = 'Your asset type list, e.g.,
    # ["storage.googleapis.com/Bucket","bigquery.googleapis.com/Table"]'
    # TODO page_size = 'Num of assets in one page, which must be between 1 and
    # 1000 (both inclusively)'
    # TODO content_type ="Content type to list"
    # TODO transport = 'Transport to use. Either "grpc" or "rest"'

    project_resource = "projects/{}".format(project_id)
    client = asset_v1.AssetServiceClient()

    # Call ListAssets v1 to list assets.
    response = client.list_assets(
        request={
            "parent": project_resource,
            "read_time": None,
            "asset_types": asset_types,
            "content_type": "RESOURCE",
            "page_size": 1000,
        }
    )

    print(list(response)[0])

    # for asset in response:
    #     json_str = MessageToJson(asset._pb, including_default_value_fields=True)
    #     print(json_str)

    # print(json.dumps(response, default=lambda o: o.__dict__, indent=2))


get_gcp_assets()