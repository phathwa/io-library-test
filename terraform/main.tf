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
provider "aws" {
  region = var.region
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
}

resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-north-1a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-north-1b"
  map_public_ip_on_launch = true
}

# Create an EC2 instance
resource "aws_instance" "flask_instance" {
  ami                           = var.ami_id
  instance_type                 = var.instance_type
  security_groups               = [module.alb.alb_sg_id]  # Reference SG from alb module
  subnet_id                     = aws_subnet.subnet_a.id
  associate_public_ip_address   = true

  user_data = file("./userdata.sh")

  tags = {
    Name = "FlaskAppInstance"
  }
}

# Internet Gateway and routing setup
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

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

# Call the ALB module
module "alb" {
  source  = "./modules/alb"
  vpc_id  = aws_vpc.main.id
  subnets = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}


