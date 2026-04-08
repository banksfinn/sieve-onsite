variable "vpc_id" {
  description = "The VPC ID where the security group will be created"
  type        = string
}

variable "environment" {
  description = "The environment where the ALB will be deployed"
  type        = string
}
