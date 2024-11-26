provider "aws" {

  region = var.region
  
}

# resource "aws_s3_bucket" "bucket" {
#   bucket = "io-library-code"
# }

# Removed aws_s3_bucket_acl as it was causing issues.
# resource "aws_s3_object" "app_code" {
#   bucket = aws_s3_bucket.bucket.bucket
#   key    = "python-book-library"
#   source = "../api/"
#   acl    = "private"
# }

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
}

# Define two subnets in different Availability Zones
resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-north-1a"  # First Availability Zone
  map_public_ip_on_launch = true  # Ensures EC2 instances in this subnet get public IPs
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-north-1b"  # Second Availability Zone
  map_public_ip_on_launch = true  # Ensures EC2 instances in this subnet get public IPs
}

resource "aws_security_group" "alb_sg" {
  name        = "alb_security_group"
  description = "Allow HTTP(s) access to ALB"
  vpc_id      = aws_vpc.main.id

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
    cidr_blocks = ["0.0.0.0/0"]  # Or more restrictive IP ranges
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create the ALB and specify two subnets for better availability
resource "aws_lb" "main" {
  name               = "my-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}

resource "aws_lb_target_group" "flask_target" {
  name     = "flask-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
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

resource "aws_instance" "flask_instance" {
  ami                           = var.ami_id
  instance_type                 = var.instance_type
  security_groups               = [aws_security_group.alb_sg.id]
  subnet_id                     = aws_subnet.subnet_a.id  # Can also use subnet_b for higher availability
  associate_public_ip_address   = true  # Ensure the instance gets a public IP

  user_data = file("./userdata.sh")

  tags = {
    Name = "FlaskAppInstance"
  }
}

resource "aws_lb_target_group_attachment" "flask_target_attachment" {
  target_group_arn = aws_lb_target_group.flask_target.arn
  target_id        = aws_instance.flask_instance.id
  port             = 80
}

# Add Internet Gateway to the VPC for public access to ALB and EC2 instances
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

# Add a route to the Internet Gateway in the route table for public access
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.main.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

resource "aws_route_table_association" "subnet_a_association" {
  subnet_id      = aws_subnet.subnet_a.id
  route_table_id = aws_route_table.main.id
}

resource "aws_route_table_association" "subnet_b_association" {
  subnet_id      = aws_subnet.subnet_b.id
  route_table_id = aws_route_table.main.id
}
