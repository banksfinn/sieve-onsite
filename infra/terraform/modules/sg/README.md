# Security Group Module

This module creates an AWS Security Group with customizable ingress and egress rules.

## Inputs

- `name`: The name of the security group.
- `description`: Description of the security group. Default is "Managed by Terraform".
- `vpc_id`: The VPC ID where the security group will be created.
- `tags`: A map of tags to apply to the security group. Default is an empty map.

## Outputs

- `security_group_id`: The ID of the security group.
- `security_group_arn`: The ARN of the security group.

## Usage

```hcl
module "security_group" {
  source      = "../modules/sg"
  name        = "findfi-security-group"
  vpc_id      = var.vpc_id
  description = "Security group for findfi"
}