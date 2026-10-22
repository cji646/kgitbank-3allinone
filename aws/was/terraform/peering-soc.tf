# Existing SOC VPC belongs to another AWS account; the SOC operator
# must accept this request. Do not attempt to auto-accept remotely.
resource "aws_vpc_peering_connection" "was_to_soc" {
  vpc_id        = aws_vpc.was.id
  peer_owner_id = "251376346232"
  peer_vpc_id   = "vpc-0ef0baa11e03982f8"
  peer_region   = "ap-northeast-2"
  auto_accept   = false

  tags = { Name = "WAS-to-SOC" }
}

# Add routes and requester-side DNS options only after the SOC operator
# confirms the pcx is ACTIVE.
resource "aws_route" "soc_private_1" {
  count                     = var.soc_peering_accepted ? 1 : 0
  route_table_id            = aws_route_table.private_1.id
  destination_cidr_block    = "172.31.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.was_to_soc.id
}

resource "aws_route" "soc_private_2" {
  count                     = var.soc_peering_accepted ? 1 : 0
  route_table_id            = aws_route_table.private_2.id
  destination_cidr_block    = "172.31.0.0/16"
  vpc_peering_connection_id = aws_vpc_peering_connection.was_to_soc.id
}

resource "aws_vpc_peering_connection_options" "soc_requester_dns" {
  count                     = var.soc_peering_accepted ? 1 : 0
  vpc_peering_connection_id = aws_vpc_peering_connection.was_to_soc.id

  requester {
    allow_remote_vpc_dns_resolution = true
  }
}

# SOC VPC route - Public Route Table
resource "aws_route" "soc_public" {
  count = var.soc_peering_accepted ? 1 : 0

  route_table_id = aws_route_table.public.id

  destination_cidr_block = "172.31.0.0/16"

  vpc_peering_connection_id = aws_vpc_peering_connection.was_to_soc.id
}
