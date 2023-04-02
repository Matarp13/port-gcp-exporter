# Port GCP Exporter
This GCP Function is written in Python and is used to retrieve information about Pub/Sub topics, buckets, and VM instances in your GCP project, and finally - report it to your Port application.

For your comfort, in the Terraform directory you can find a Terraform automation to setup everything in your gcp project.
> Note: This function currently only supports Pub/Sub topics, buckets, and VM instances, and only Scheduled-base triggers.


## Prerequisites

In order to use this GCP Function, you will need to have the following:

- A Google Cloud project - you can [create a free account](https://cloud.google.com/free) on the GCP website.
- [Install Terraform on your environment](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli?in=terraform%2Fgcp-get-started) 
- [Install the gcloud cli](https://cloud.google.com/sdk/docs/install) and configure it to your relevant project
- [Find your Port credentials](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/api/#find-your-port-credentials) for the function to connect with Port's REST API and [save them as secrets](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets) in your Google Cloud project
- Create a Google Service Account , and assign it the following permission: 
  - Cloud Asset Viewer 
  - Pub/Sub Viewer 
  - Secret Manager Secret Accessor
  - Storage Object Viewer
- A config file defining the resources and attributes you want to export - for addition information see the config file explenation in [Ports AWS exporter docs](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/aws/#exporter-aws-serverless-application)
 The config file need to be saved in a [Bucket](https://cloud.google.com/storage/docs/creating-buckets) in your project
 

> Note: First time running the function you might need to enable some APIS in your google account, so make sure to follow the logs in order to see what API is disabled


### Port

- A GCP account with the necessary permissions to access the resources you want to retrieve information about.
- A computer with `gcloud` installed and configured to authenticate with your GCP account.
- A Terraform configuration file and variables file for setting up the function with the Google provider.

## Terraform

The Terraform directory contains the configuration files necessary for setting up the GCP Function. You will need to set up the Google provider in your Terraform configuration file and provide the necessary variables in your variables file. 

To run the Terraform configuration, navigate to the Terraform directory and run the following commands:
