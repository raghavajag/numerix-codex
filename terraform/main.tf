terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_artifact_registry_repository" "animai_repo" {
  location      = var.region
  project       = var.project_id
  repository_id = var.repo_name
  description   = "Artifact Registry repository for AnimAI services"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "manim_worker" {
  name     = var.worker_service_name
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    timeout                          = "900s"
    max_instance_request_concurrency = 1

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = var.worker_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      env {
        name  = "R2_ACCOUNT_ID"
        value = var.r2_account_id
      }

      env {
        name  = "R2_ACCESS_KEY_ID"
        value = var.r2_access_key_id
      }

      env {
        name  = "R2_SECRET_ACCESS_KEY"
        value = var.r2_secret_access_key
      }

      env {
        name  = "R2_BUCKET"
        value = var.r2_bucket
      }

      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 6

        http_get {
          path = "/health"
          port = 8080
        }
      }

      liveness_probe {
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3

        http_get {
          path = "/health"
          port = 8080
        }
      }
    }
  }
}

resource "google_cloud_run_v2_service" "animai_api" {
  name     = var.api_service_name
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    timeout                          = "300s"
    max_instance_request_concurrency = 10

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = var.api_image

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      env {
        name  = "OPENAI_API_KEY"
        value = var.openai_api_key
      }

      env {
        name  = "LANGSMITH_API_KEY"
        value = var.langsmith_api_key
      }

      env {
        name  = "LANGSMITH_PROJECT"
        value = var.langsmith_project
      }

      env {
        name  = "LANGSMITH_TRACING"
        value = var.langsmith_tracing
      }

      env {
        name  = "CHROMA_API_KEY"
        value = var.chroma_api_key
      }

      env {
        name  = "CHROMA_TENANT"
        value = var.chroma_tenant
      }

      env {
        name  = "CHROMA_DATABASE"
        value = var.chroma_database
      }

      env {
        name  = "MANIM_WORKER_URL"
        value = google_cloud_run_v2_service.manim_worker.uri
      }

      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 6

        http_get {
          path = "/health"
          port = 8000
        }
      }

      liveness_probe {
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3

        http_get {
          path = "/health"
          port = 8000
        }
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "api_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.animai_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "worker_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.manim_worker.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
