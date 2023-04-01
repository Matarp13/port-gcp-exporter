# Define the provider and set the project ID and region
provider "google" {
  project = var.project_id
  region  = var.function_region
}

# Global Variables
locals {
    function_memory = 256
    function_timeout = 540
    runtime = "python39"
    scheduler_cron_expression = "0 9 * * *"
    function_entry_point = "main"
}


# Parameters
variable "project_id" {
  type    = string
  description = "The GCP project id the function will run in"
}

variable "function_region" {
  type = string
  default = "us-central1"
  description = "The region the function will run at"
}

variable "service_account_email" {
  type = string
  description = "The service account to run the gcp function"
}

variable "source_repository_url" {
  type    = string
  description = "The GCP source repository (Google git repo) for the function code"
}

variable "function_name" {
  type    = string
  default = "port-gcp-exporter"
}

variable "scheduler_name" {
  type    = string
  default = "port-function-scheduler"
  description = "The name of the scheduler that triggers the function"
}

variable "create_topic" {
  type    = bool
  default = true
}

variable "topic_name" {
  type    = string
  default = "port-topic"
}

variable "port_client_id_key" {
  type = string
  default = "port-client-id"
  description = "The secret name where the port api client id is located"
}


variable "port_client_secret_key" {
  type = string
  default = "port-client-secret"
  description = "The secret name where the port api client secret is located"
}

variable "bucket_name" {
  type = string
  default = "port-exporter"
  description = "The name of the bucket where the config file is located"
}

variable "config_file_name" {
  type = string
  default = "config.json"
  description = "The json config file name (including file ending)"
}


# GCP function creation
resource "google_cloudfunctions_function" "function" {
  name        = var.function_name
  description = "The function exports data of your gcp environment and send it to Port via REST API"
  runtime     = local.runtime
  available_memory_mb = local.function_memory

  source_repository {
    url = var.source_repository_url
  }          
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project_id}/topics/${var.topic_name}"
  }

  timeout                      = local.function_timeout
  entry_point                  = local.function_entry_point

  service_account_email = var.service_account_email

  environment_variables = {
    PORT_CLIENT_ID_KEY = var.port_client_id_key
    PORT_CLIENT_SECRET_KEY = var.port_client_secret_key
    BUCKET_NAME = var.bucket_name
    CONFIG_JSON_FILE_KEY = var.config_file_name
  }
}

# Create the Pub/Sub topic
resource "google_pubsub_topic" "port_topic" {
  count = var.create_topic ? 1 : 0
  name = var.topic_name
}

# Create the scheduler
resource "google_cloud_scheduler_job" "port-scheduler" {
  name        = var.scheduler_name
  description = "This scheduler sends an event to a pub/sub topic that triggers the port exporter function"
  schedule    = var.cron_expression

  pubsub_target {
    # topic.id is the topic's full resource name.
    topic_name = "projects/${var.project_id}/topics/${var.topic_name}"
    attributes = {
        "event_type" = "scheduled"
      }
  }
}