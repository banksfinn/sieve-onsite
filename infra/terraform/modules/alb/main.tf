# Create the ALB
resource "aws_lb" "alb" {
  name               = "${var.environment}-alb"
  # Allow us to reach the outside world
  internal           = false
  load_balancer_type = "application"

  security_groups    = [var.alb_security_group_id]

  subnets            = var.public_subnet_ids

  enable_deletion_protection = true

  tags = {
    Environment = var.environment
  }
}

# Create the target group
# This is what recieves the traffic
resource "aws_lb_target_group" "alb_target_group" {
  name        = "${var.environment}-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id

  target_type = "ip"

  health_check {
    interval            = 30
    path                = "/health"
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
  }

  tags = {
    Environment = var.environment
  }
}

# Create the HTTP listener
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Create the HTTPS listener
resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 443
  protocol          = "HTTPS"

  # TODO: Add the certificate
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.alb_target_group.arn
  }

  depends_on = [aws_lb_target_group.alb_target_group]
}
