# Phase 1: WAS network only. No EC2, NAT Gateway, RDS, ALB, or EIP.
resource "aws_vpc" "was" {
  cidr_block           = "10.30.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "SafeTravel-WAS-VPC" }
}

locals {
  was_subnets = {
    public_1  = { cidr = "10.30.1.0/24", az = "ap-northeast-2a" }
    public_2  = { cidr = "10.30.2.0/24", az = "ap-northeast-2c" }
    private_1 = { cidr = "10.30.10.0/24", az = "ap-northeast-2a" }
    private_2 = { cidr = "10.30.20.0/24", az = "ap-northeast-2c" }
  }
}

resource "aws_subnet" "was" {
  for_each = local.was_subnets

  vpc_id                  = aws_vpc.was.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = false

  tags = { Name = "WAS-${replace(each.key, "_", "-")}" }
}

resource "aws_internet_gateway" "was" {
  vpc_id = aws_vpc.was.id
  tags   = { Name = "WAS-IGW" }
}
