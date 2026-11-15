output "instance_id" {
  value = aws_instance.app.id
}

output "public_ip" {
  value = aws_instance.app.public_ip
}

output "instance_type" {
  value = aws_instance.app.instance_type
}

output "ingress_ports" {
  value = [for rule in aws_security_group.app.ingress : rule.to_port]
}

output "imds_http_tokens" {
  value = aws_instance.app.metadata_options[0].http_tokens
}

output "root_volume_encrypted" {
  value = aws_instance.app.root_block_device[0].encrypted
}
