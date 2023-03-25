import os
# from google.cloud import compute_v1, pubsub_v1, storage


def hello_world(request):
    """HTTP Cloud Function that returns a greeting."""
    return 'Hello World!'

# def get_gcp_data():
#     # Set up authentication credentials
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/credentials.json"
#
#     # Set up Compute Engine client
#     compute_client = compute_v1.InstancesClient()
#     project_id = "your-project-id"
#     zone = "us-central1-a"
#     vm_instances = []
#
#     # Get list of VM instances in project and zone
#     request = compute_v1.ListInstancesRequest(
#         project=project_id,
#         zone=zone
#     )
#     response = compute_client.list(request)
#     for instance in response:
#         vm_instances.append(instance.name)
#
#     # Set up Pub/Sub client
#     pubsub_client = pubsub_v1.SubscriberClient()
#     topic_names = []
#
#     # Get list of Pub/Sub topics in project
#     project_path = f"projects/{project_id}"
#     for topic in pubsub_client.list_topics(project_path):
#         topic_names.append(topic.name)
#
#     # Set up Storage client
#     storage_client = storage.Client()
#     bucket_names = []
#
#     # Get list of Storage buckets in project
#     for bucket in storage_client.list_buckets():
#         if bucket.project == project_id:
#             bucket_names.append(bucket.name)
#
#     # Return data as dictionary
#     return {
#         "VM instances": vm_instances,
#         "Pub/Sub topics": topic_names,
#         "Storage buckets": bucket_names
#     }
