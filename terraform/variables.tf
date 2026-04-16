variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "repo_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "animai-repo"
}

variable "api_service_name" {
  description = "Cloud Run API service name"
  type        = string
  default     = "animai-api"
}

variable "worker_service_name" {
  description = "Cloud Run worker service name"
  type        = string
  default     = "manim-worker"
}

variable "api_image" {
  description = "Full container image URL for the API service"
  type        = string
}

variable "worker_image" {
  description = "Full container image URL for the Manim worker service"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "langsmith_api_key" {
  description = "LangSmith API key"
  type        = string
  sensitive   = true
}

variable "langsmith_project" {
  description = "LangSmith project name"
  type        = string
}

variable "langsmith_tracing" {
  description = "LangSmith tracing flag"
  type        = string
  default     = "true"
}

variable "chroma_api_key" {
  description = "Chroma API key"
  type        = string
  sensitive   = true
}

variable "chroma_tenant" {
  description = "Chroma tenant name"
  type        = string
}

variable "chroma_database" {
  description = "Chroma database name"
  type        = string
}

variable "r2_account_id" {
  description = "Cloudflare R2 account ID"
  type        = string
}

variable "r2_access_key_id" {
  description = "Cloudflare R2 access key ID"
  type        = string
  sensitive   = true
}

variable "r2_secret_access_key" {
  description = "Cloudflare R2 secret access key"
  type        = string
  sensitive   = true
}

variable "r2_bucket" {
  description = "Cloudflare R2 bucket name"
  type        = string
  default     = "manim-videos"
}
