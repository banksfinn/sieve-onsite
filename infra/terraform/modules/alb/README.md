# ALB Module

This module creates an AWS Application Load Balancer (ALB) with associated resources like security groups, target groups, and listeners.

## Inputs

- `alb_name`: The name of the ALB.
- `internal`: Whether the load balancer is internal.
- `subnets`: The subnets to associate with the ALB.
- `vpc_id`: The ID of the VPC where the ALB will be deployed.
- `allowed_cidr_blocks`: CIDR blocks allowed to access the ALB.
- `enable_deletion_protection`: If true, deletion protection will be enabled on the ALB.
- `target_group_name`: The name of the target group.
- `target_group_port`: The port for the target group.
- `target_type`: The target type for the target group (e.g., 'instance' or 'ip').
- `health_check_path`: The path for the health check.
- `security_group_name`: The name of the security group for the ALB.
- `tags`: Tags to apply to resources.

## Outputs

- `alb_arn`: The ARN of the ALB.
- `alb_dns_name`: The DNS name of the ALB.
- `alb_security_group_id`: The ID of the security group associated with the ALB.
- `alb_target_group_arn`: The ARN of the target group.

## Usage

```hcl
module "alb" {
  source             = "../modules/alb"
  alb_name           = "my-alb"
  internal           = false
  subnets            = ["subnet-12345678", "subnet-87654321"]
  vpc_id             = "vpc-12345678"
  allowed_cidr_blocks = ["0.0.0.0/0"]
  enable_deletion_protection = false
  target_group_name  = "my-target-group"
  target_group_port  = 80
  target_type        = "instance"
  health_check_path  = "/health"
  security_group_name = "alb-sg"
  tags               = {
    Environment = "dev"
    Project     = "my-project"
  }
}
