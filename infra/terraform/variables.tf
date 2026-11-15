variable "offline" {
  description = "true - навчальний режим без облікового запису AWS"
  type        = bool
  default     = true
}

variable "aws_region" {
  description = "Регіон AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Середовище: dev або prod"
  type        = string

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment має бути dev або prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR-блок VPC застосунку"
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR публічної підмережі"
  type        = string
  default     = "10.20.1.0/24"
}

variable "availability_zone" {
  description = "Зона доступності для підмережі"
  type        = string
  default     = "us-east-1a"
}

variable "ami_id" {
  description = "ID образу EC2; порожнє значення - пошук актуального Amazon Linux 2023"
  type        = string
  default     = "ami-0abcdef1234567890" # умовний AMI для режиму offline
}

variable "repo_url" {
  description = "Git-репозиторій застосунку"
  type        = string
  default     = "https://github.com/AndriiDraga/home-budget-tracker.git"
}

variable "git_branch" {
  description = "Гілка, з якої сервер розгортає застосунок"
  type        = string
  default     = "feature/devops-iac"
}

# ---------- Секрети ----------
# sensitive = true: значення не виводяться в plan/apply/output.
# Значення задаються у terraform.tfvars (не потрапляє в Git) або через
# змінні середовища TF_VAR_secret_key / TF_VAR_db_password.

variable "secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.secret_key) >= 32
    error_message = "SECRET_KEY має містити щонайменше 32 символи."
  }
}

variable "db_password" {
  description = "Пароль PostgreSQL"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 12
    error_message = "Пароль бази даних має містити щонайменше 12 символів."
  }
}
