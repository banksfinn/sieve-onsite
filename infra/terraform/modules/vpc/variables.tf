variable "environment" {
  description = "The environment where the VPC will be deployed"
  type        = string
}

variable "cidr_block" {
  description = "The CIDR block for the VPC"
  type        = string
}

variable "public_subnets" {
  description = "The public subnets to associate with the VPC"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" {
  description = "The private subnets to associate with the VPC"
  type        = map(object({
    cidr = string
    az   = string
  }))
}
