variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "ami_id" {
  type    = string
  default = "ami-0658158d7ba8fd573"  # Replace with actual AMI ID
}

variable "instance_type" {
  type    = string
  default = "t3.micro"  # Example instance type
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"  # You can adjust this CIDR block as needed
}
