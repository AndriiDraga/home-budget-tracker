output "environment" {
  value = var.environment
}

output "instance_type" {
  description = "Тип EC2 для поточного середовища"
  value       = module.app_server.instance_type
}

output "ingress_ports" {
  description = "Порти, відкриті в Security Group"
  value       = module.app_server.ingress_ports
}

output "imds_http_tokens" {
  description = "Режим метаданих EC2 (required = лише IMDSv2)"
  value       = module.app_server.imds_http_tokens
}

output "root_volume_encrypted" {
  value = module.app_server.root_volume_encrypted
}

output "app_url" {
  description = "Адреса застосунку (nginx на порту 8080)"
  value       = "http://${module.app_server.public_ip}:8080"
}
