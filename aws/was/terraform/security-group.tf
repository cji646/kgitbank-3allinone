
resource "aws_security_group" "was" {
  name        = "SafeTravel-WAS-SG"
  description = "Security group for SafeTravel WAS servers"
  vpc_id      = aws_vpc.was.id

  ingress {
    description = "Web to WAS - Flask 8080"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["10.40.0.0/16"]
  }

  ingress {
    description = "SOC WAS health check"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["172.31.9.124/32"]
  }

  egress {
    description = "Outbound access - initial setup"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "SafeTravel-WAS-SG"
  }
}
