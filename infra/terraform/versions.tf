# Home Budget Tracker - інфраструктура як код (етап 4 індивідуального проєкту).
# Опис хмарного середовища для запуску застосунку через Docker Compose на EC2.

terraform {
  required_version = ">= 1.7.0" # mock_provider у terraform test - з 1.7

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Режим offline (за замовчуванням): облікового запису AWS немає, тому
# виконуються init / validate / plan / test без звернень до AWS.
# Для реального AWS: -var="offline=false" -var="ami_id=" та справжні облікові дані.
provider "aws" {
  region = var.aws_region

  access_key                  = var.offline ? "mock_access_key" : null
  secret_key                  = var.offline ? "mock_secret_key" : null
  skip_credentials_validation = var.offline
  skip_requesting_account_id  = var.offline
  skip_metadata_api_check     = var.offline

  default_tags {
    tags = {
      Project     = "home-budget-tracker"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
