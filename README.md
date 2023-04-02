# Port GCP Exporter
This GCP Function is written in Python and is used to retrieve information about Pub/Sub topics, buckets, and VM instances in your GCP project, and finally - report it to your Port application.

For your comfort, in the Terraform directory you can find a Terraform automation to setup everything in your gcp project.
> Note: This function currently only supports Pub/Sub topics, buckets, and VM instances, and only Scheduled-base triggers.



## How Does it work?


#### Function Startup
In Google Cloud Platform, Functions can be triggred by multiple mechanisms. 
In our case, We have a GCP Scheduler triggering events to a GCP Topic.
The function is subscribed to the same GCP Topic, so whenever the Scheduler triggers an event to the topic,  the function is being invoked.

#### Function Workflow
1. Pulls a config file with the resources and attributes we want to export to Port
2. Pulls to Port's credentials saved in your project Secrets
3. Uses Google Cloud Asset Inventory API to read and map the resources in your GCP Project.
4. Report the relevant resources to Port using Port's REST API.

> For addition information about configuration see the config file explenation in [Ports AWS exporter docs](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/aws/#exporter-aws-serverless-application)


## Prerequisites

In order to use this GCP Function, you will need to have the following:

- A Google Cloud project - you can [create a free account](https://cloud.google.com/free) on the GCP website.
- A Google Cloud account with permission for creating GCP functions, GCP Scheduler and GCP Pub/Sub Topics
- [Install Terraform on your environment](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli?in=terraform%2Fgcp-get-started) 
- [Install the gcloud cli](https://cloud.google.com/sdk/docs/install) and configure it to your relevant project
- Make sure you have `GOOGLE_APPLICATION_CREDENTIALS` environment variable saved and point to a file with your GCP creation account key.
- [Find your Port credentials](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/api/#find-your-port-credentials) for the function to connect with Port's REST API and [save them as secrets](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets) in your Google Cloud project
- Create a Google Service Account , and assign it the following permission: 
  - Cloud Asset Viewer 
  - Pub/Sub Viewer 
  - Secret Manager Secret Accessor
  - Storage Object Viewer
- A config file defining the resources and attributes you want to export - see example in `examples/config.py`
 The config file need to be saved in a [Bucket](https://cloud.google.com/storage/docs/creating-buckets) in your project
 - A GCP Source Repository containing this Git repo (You can [mirror this repo](https://cloud.google.com/source-repositories/docs/mirroring-a-github-repository) directly instead of fork it and copy)
 
> Note: First time running the function you might need to enable some APIS in your google account, so make sure to follow the logs in order to see what API is disabled


## Terraform Configuration
In the terraform directory, you can find a Terraform configuration file (`main.tf`) and a variables file (`vars.tf`) for setting up the GCP function.

To run the Terraform configuration, navigate to the terraform directory and:
1. Set the variables in `vars.tfvars` with your project (Make sure all the required are filled)
2. Run terraform init to initialize the Terraform configuration.
3. Run terraform plan to preview the changes that will be made.
4. Run terraform apply to apply the changes and deploy the function to GCP.

### Additional Information
* See the [Architecture Reference] for visual presentation of the flow.
* See [Google Cloud Docs](https://cloud.google.com/docs?hl=he) for additional documentations.

