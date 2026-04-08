output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.findfi_vpc.id
}

output "public_subnets" {
  value = tomap({ for k, v in aws_subnet.public : k => v.id })
  description = "The IDs of the public subnets"
}

output "private_subnets" {
  value = tomap({ for k, v in aws_subnet.private : k => v.id })
  description = "The IDs of the private subnets"
}