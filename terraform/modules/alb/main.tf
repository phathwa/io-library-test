resource "random_id" "suffix" {
  byte_length = 8
}
resource "aws_security_group" "alb_sg" {
  name        = "alb_security_group-${random_id.suffix.hex}"
  description = "Allow HTTP(s) access to ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "main" {
  name               = "my-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnets
}

resource "aws_lb_target_group" "flask_target" {
  name     = "flask-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_lb_target_group.flask_target.arn
    type             = "forward"
  }
}


# ALB Target Group Attachment (only after EC2 is created)
resource "aws_lb_target_group_attachment" "flask_target_attachment" {
  target_group_arn = module.alb.flask_target_group_arn
  target_id        = aws_instance.flask_instance.id
  port             = var.port

  depends_on = [aws_instance.flask_instance]  # Ensure this runs after the instance is created
}
