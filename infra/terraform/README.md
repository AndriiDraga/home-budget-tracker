# Infrastructure as Code (Terraform)

Етап 4 плану проєкту: опис хмарної інфраструктури Home Budget Tracker кодом
і автоматизоване тестування цієї інфраструктури.

```
infra/terraform/
├── versions.tf / variables.tf / main.tf / outputs.tf   кореневий модуль
├── env/dev.tfvars, env/prod.tfvars                      параметри середовищ
├── terraform.tfvars.example                              шаблон секретів
├── modules/network/      VPC, Internet Gateway, публічна підмережа
├── modules/app_server/   Security Group + EC2 (user_data: Docker Compose)
└── tests/app.tftest.hcl  terraform test з mock_provider
```

Що створюється: VPC → публічна підмережа → EC2 (dev: t3.micro, prod: t3.small),
який під час першого запуску встановлює Docker, клонує репозиторій і виконує
`docker compose up -d --build` (web + PostgreSQL + nginx, порт 8080).

Секрети (`secret_key`, `db_password`) - змінні з `sensitive = true` і
перевіркою довжини; значення - у `terraform.tfvars`, який не потрапляє в Git.

## Команди (PowerShell, з цієї папки)

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars   # вписати власні значення
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -var-file="env/dev.tfvars"
terraform test
```

Режим `offline = true` (за замовчуванням) працює без облікового запису AWS.
Для реального розгортання: `-var="offline=false" -var="ami_id="`, облікові
дані AWS і `terraform apply -var-file="env/dev.tfvars"`.
