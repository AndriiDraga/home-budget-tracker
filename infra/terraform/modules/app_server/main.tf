# Модуль app_server: Security Group + EC2, який під час першого запуску
# (user_data) встановлює Docker, клонує репозиторій і піднімає
# docker compose (web + PostgreSQL + nginx) з ЛР3.
#
# Безпека:
#  - відкрито лише порт 8080 (nginx); SSH (22) закрито;
#  - IMDSv2 обов'язковий (http_tokens = "required");
#  - кореневий диск зашифровано;
#  - секрети приходять як sensitive-змінні й не показуються в plan.
#    У production їх варто брати з AWS Secrets Manager / SSM Parameter Store
#    або Vault, бо user_data доступний через метадані екземпляра.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

data "aws_ami" "amazon_linux" {
  count       = var.ami_id == "" ? 1 : 0
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_security_group" "app" {
  name_prefix = "${var.name}-app-"
  description = "Home Budget Tracker: HTTP via nginx"
  vpc_id      = var.vpc_id

  ingress {
    description = "nginx (docker compose, port 8080)"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.name}-app-sg" }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_instance" "app" {
  ami                    = var.ami_id != "" ? var.ami_id : data.aws_ami.amazon_linux[0].id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.app.id]

  user_data = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    repo_url    = var.repo_url
    git_branch  = var.git_branch
    app_port    = var.app_port
    secret_key  = var.secret_key
    db_password = var.db_password
  })
  user_data_replace_on_change = true

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = { Name = "${var.name}-app" }
}
