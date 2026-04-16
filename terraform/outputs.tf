output "service_url" {
  description = "Public URL for the Numerix API service"
  value       = google_cloud_run_v2_service.animai_api.uri
}

output "worker_url" {
  description = "Public URL for the Manim worker service"
  value       = google_cloud_run_v2_service.manim_worker.uri
}
