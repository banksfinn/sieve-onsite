variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "The AWS profile to use"
  type        = string
  default     = "findfi"
}

variable "environment" {
  description = "The environment to deploy resources"
  type        = string
  default     = "staging"
}

variable "findfi_version" {
  default     = "0.0.1"
  description = "The version of FindFi to deploy"
  type        = string
}

variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.10.0.0/16"
}

variable "public_subnets" {
  description = "The public subnets to associate with the VPC"
  type        = map(object({
    cidr = string
    az   = string
  }))
  default = {
    "1a" = { cidr = "10.10.1.0/24", az = "us-west-2a" },
    "2b" = { cidr = "10.10.2.0/24", az = "us-west-2b" }
  }
}

variable "private_subnets" {
  description = "The private subnets to associate with the VPC"
  type        = map(object({
    cidr = string
    az   = string
  }))
  default = {
    "1a" = { cidr = "10.10.3.0/24", az = "us-west-2a" },
    "2b" = { cidr = "10.10.4.0/24", az = "us-west-2b" }
  }
}

