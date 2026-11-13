variable "name" {
  description = "Префікс назв ресурсів"
  type        = string
}

variable "vpc_cidr" {
  type = string
}

variable "public_subnet_cidr" {
  type = string
}

variable "availability_zone" {
  type = string
}
