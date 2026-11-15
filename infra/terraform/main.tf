# Кореневий модуль: мережа + сервер застосунку.
# Тип EC2 визначається середовищем, а не задається вручну.

locals {
  instance_types = {
    dev  = "t3.micro"
    prod = "t3.small"
  }
}

module "network" {
  source = "./modules/network"

  name               = "hbt-${var.environment}"
  vpc_cidr           = var.vpc_cidr
  public_subnet_cidr = var.public_subnet_cidr
  availability_zone  = var.availability_zone
}

module "app_server" {
  source = "./modules/app_server"

  name          = "hbt-${var.environment}"
  vpc_id        = module.network.vpc_id
  subnet_id     = module.network.public_subnet_id
  instance_type = local.instance_types[var.environment]
  ami_id        = var.ami_id

  repo_url    = var.repo_url
  git_branch  = var.git_branch
  secret_key  = var.secret_key
  db_password = var.db_password
}
