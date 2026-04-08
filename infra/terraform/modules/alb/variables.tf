variable "vpc_id" {
  description = "The ID of the VPC where the ALB will be deployed"
  type        = string
}

variable "environment" {
  description = "The environment where the ALB will be deployed"
  type        = string
}

variable "alb_security_group_id" {
  description = "The ID of the ALB security group"
  type        = string
}

variable "public_subnet_ids" {
  description = "The subnets to associate with the ALB"
  type        = list(string)
}

variable "certificate_arn" {
  description = "The ARN of the certificate to use for the ALB"
  type        = string
}

