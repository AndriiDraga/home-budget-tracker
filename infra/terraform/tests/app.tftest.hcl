# Автоматизовані тести інфраструктури (terraform test).
# mock_provider підміняє AWS: тести виконуються без облікового запису й
# без створення ресурсів, лише на етапі plan.

mock_provider "aws" {}

variables {
  environment = "dev"
  ami_id      = "ami-0abcdef1234567890"
  secret_key  = "test-secret-key-0123456789abcdefghijklmn"
  db_password = "test-db-password-123"
}

run "dev_uses_small_instance" {
  command = plan

  assert {
    condition     = output.instance_type == "t3.micro"
    error_message = "Для dev очікується t3.micro."
  }
}

run "prod_uses_bigger_instance" {
  command = plan

  variables {
    environment = "prod"
  }

  assert {
    condition     = output.instance_type == "t3.small"
    error_message = "Для prod очікується t3.small."
  }
}

run "only_http_port_is_open" {
  command = plan

  assert {
    condition     = output.ingress_ports == [8080]
    error_message = "Має бути відкритий лише порт 8080."
  }

  assert {
    condition     = !contains(output.ingress_ports, 22)
    error_message = "SSH (22) не повинен бути відкритий."
  }
}

run "instance_is_hardened" {
  command = plan

  assert {
    condition     = output.imds_http_tokens == "required"
    error_message = "Потрібен лише IMDSv2."
  }

  assert {
    condition     = output.root_volume_encrypted == true
    error_message = "Кореневий диск має бути зашифрований."
  }
}

run "short_secret_key_is_rejected" {
  command = plan

  variables {
    secret_key = "too-short"
  }

  expect_failures = [var.secret_key]
}

run "unknown_environment_is_rejected" {
  command = plan

  variables {
    environment = "qa"
  }

  expect_failures = [var.environment]
}
