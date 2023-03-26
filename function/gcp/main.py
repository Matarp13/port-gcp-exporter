import os
from google.cloud import compute_v1, pubsub_v1, storage

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

def get_gcp_data():
    # Set up authentication credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./matars-project-7dc58a558e83.json"

    # Set up Compute Engine client
    compute_client = compute_v1.InstancesClient()
    project_id = "matars-project"
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

    # # Set up Pub/Sub client
    # pubsub_client = pubsub_v1.SubscriberClient()
    # topic_names = []
    #
    # # Get list of Pub/Sub topics in project
    # project_path = f"projects/{project_id}"
    # for topic in pubsub_client.list_topics(project_path):
    #     topic_names.append(topic.name)
    #
    # # Set up Storage client
    # storage_client = storage.Client()
    # bucket_names = []
    #
    # # Get list of Storage buckets in project
    # for bucket in storage_client.list_buckets():
    #     if bucket.project == project_id:
    #         bucket_names.append(bucket.name)


    print(vm_instances)
    # Return data as dictionary
    # return {
    #     "VM instances": vm_instances,
    #     "Pub/Sub topics": topic_names,
    #     "Storage buckets": bucket_names
    # }

get_gcp_data()
