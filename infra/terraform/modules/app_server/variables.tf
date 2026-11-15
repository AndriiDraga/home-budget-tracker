variable "name" {
  description = "Префікс назв ресурсів"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "ami_id" {
  description = "ID образу; порожнє значення - пошук Amazon Linux 2023"
  type        = string
  default     = ""
}

variable "app_port" {
  description = "Порт nginx з docker-compose.yml"
  type        = number
  default     = 8080
}

variable "repo_url" {
  type = string
}

variable "git_branch" {
  type = string
}

variable "secret_key" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}
