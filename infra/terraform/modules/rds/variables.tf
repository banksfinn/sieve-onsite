variable "rds_security_group_id" {
  description = "The ID of the security group for the RDS instance"
  type        = string
}

variable "database_name" {
  description = "The name of the database"
  type        = string
}

variable "environment" {
  description = "The environment to deploy to"
  type        = string
}

variable "password" {
  description = "The password for the RDS instance"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC where the RDS instance will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "The IDs of the private subnets where the RDS instance will be deployed"
  type        = list(string)
}