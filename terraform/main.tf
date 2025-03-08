terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  ##?Credentials only needs to be set if you do not have the GOOGLE_APPLICATION_CREDENTIALS set
  # credentials = file(var.credentials)
  project = var.project
  region  = var.region
}


resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  # Optional, but recommended settings:
  storage_class               = var.gcs_storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 15 //days
    }
    action {
      type = "AbortIncompleteMultipartUpload"
      # type = "Delete"
    }
  }
}



resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}

# # Create a VM instance
# resource "google_compute_instance" "vm_instance" {
#   name         = "example-vm"
#   machine_type = "e2-standard-4"
#   zone         = "us-south1-a"

#   boot_disk {
#     initialize_params {
#       image = "ubuntu-os-cloud/ubuntu-2004-lts"
#     }
#   }

#   network_interface {
#     network = "default"

#     access_config {
#       # Required for external IP
#     }
#   }
# }
