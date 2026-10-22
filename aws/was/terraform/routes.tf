resource "aws_route_table" "public" {
  vpc_id = aws_vpc.was.id
  tags   = { Name = "WAS-Public-RTB" }
}

resource "aws_route" "public_default" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.was.id
}

resource "aws_route_table" "private_1" {
  vpc_id = aws_vpc.was.id
  tags   = { Name = "WAS-Private-RTB-1" }
}

resource "aws_route_table" "private_2" {
  vpc_id = aws_vpc.was.id
  tags   = { Name = "WAS-Private-RTB-2" }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.was["public_1"].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.was["public_2"].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.was["private_1"].id
  route_table_id = aws_route_table.private_1.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.was["private_2"].id
  route_table_id = aws_route_table.private_2.id
}
