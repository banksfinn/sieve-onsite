# Create a security group
resource "aws_security_group" "default" {
  name        = "${var.environment}-default-sg"
  description = "Default security group for ${var.environment}"
  vpc_id      = var.vpc_id
}

# Ingress rules
# HTTP
resource "aws_security_group" "findfi_alb" {
    name = "findfi-alb"
    description = "Security group for findfi-alb"
    vpc_id = var.vpc_id

    # Allow all incoming connections
    ingress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        self        = true
    }

    # Allow all outgoing connections
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        self        = true
    }
}

resource "aws_security_group_rule" "http_ingress" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  security_group_id = aws_security_group.findfi_alb.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# HTTPS
resource "aws_security_group_rule" "https_ingress" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.findfi_alb.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group" "findfi_ecs" {
    name = "findfi-ecs"
    description = "Security group for findfi-ecs"
    vpc_id = var.vpc_id

    # Allow all incoming connections
    ingress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        self        = true
    }

    # Allow all outgoing connections
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        self        = true
    }
}

resource "aws_security_group" "findfi_rds" {
    name = "findfi-rds"
    description = "Security group for findfi-rds"
    vpc_id = var.vpc_id

    # Allow all incoming connections
    ingress {
        from_port   = 5432
        to_port     = 5432
        protocol    = "tcp"
        cidr_blocks = ["10.10.0.0/16"]
    }

    # Allow all outgoing connections
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        self        = true
    }
}