variable "environment" {
  description = "The environment to deploy to"
  type        = string
}

variable "ecs_security_group_id" {
  description = "The ID of the security group for the ECS cluster"
  type        = string
}

variable "alb_target_group_arn" {
  description = "The ARN of the target group for the ALB"
  type        = string
}

variable "rds_connection_string" {
  description = "The connection string for the RDS instance"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC where the ECS cluster will be deployed"
  type        = string
}

variable "findfi_version" {
  description = "The version of the application to deploy"
  type        = string
}

variable "ecr_repository_url" {
  description = "The URL of the ECR repository"
  type        = string
}

variable "gateway_desired_count" {
  description = "The desired count of the gateway"
  type        = number
  default     = 1
}

variable "private_subnet_ids" {
  description = "The private subnets to deploy the ECS cluster"
  type        = list(string)
}