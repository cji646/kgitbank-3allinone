
# Amazon Linux 2023 (일반 AMI)
data "aws_ami" "was_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-kernel-6.1-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# WAS 서버 정보
locals {
  was_servers = {
    main = {
      name   = "WAS-Main"
      subnet = "private_1"
      ip     = "10.30.10.10"
    }
    backup = {
      name   = "WAS-Backup"
      subnet = "private_2"
      ip     = "10.30.20.10"
    }
  }
}

# EC2 Instance Connect Endpoint 보안 그룹
resource "aws_security_group" "was_eice" {
  name   = "SafeTravel-WAS-EICE-SG"
  vpc_id = aws_vpc.was.id

  egress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.30.0.0/16"]
  }

  tags = {
    Name = "SafeTravel-WAS-EICE-SG"
  }
}

# EC2 SSH 접속 보안 그룹
resource "aws_security_group" "was_ssh" {
  name   = "SafeTravel-WAS-SSH-SG"
  vpc_id = aws_vpc.was.id

  ingress {
    description     = "SSH from Instance Connect Endpoint"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.was_eice.id]
  }

  tags = {
    Name = "SafeTravel-WAS-SSH-SG"
  }
}

# NAT 없이 Private EC2에 접속하기 위한 엔드포인트
resource "aws_ec2_instance_connect_endpoint" "was" {
  subnet_id          = aws_subnet.was["private_1"].id
  security_group_ids = [aws_security_group.was_eice.id]
  preserve_client_ip = false

  tags = {
    Name = "SafeTravel-WAS-EICE"
  }
}

# WAS EC2 두 대
resource "aws_instance" "was_servers" {
  for_each = local.was_servers

  ami           = data.aws_ami.was_linux.id
  instance_type = "t3.micro"

  subnet_id  = aws_subnet.was[each.value.subnet].id
  private_ip = each.value.ip

  associate_public_ip_address = false

  vpc_security_group_ids = [
    aws_security_group.was.id,
    aws_security_group.was_ssh.id
  ]

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 10
    encrypted             = true
    delete_on_termination = true
  }

  metadata_options {
    http_tokens = "required"
  }

  lifecycle {
    ignore_changes = [ami]
  }

  tags = {
    Name = each.value.name
  }
}

# 생성된 서버 정보 출력
output "was_instance_info" {
  value = {
    for name, instance in aws_instance.was_servers :
    name => {
      instance_id = instance.id
      private_ip  = instance.private_ip
    }
  }
}

output "was_eice_id" {
  value = aws_ec2_instance_connect_endpoint.was.id
}
