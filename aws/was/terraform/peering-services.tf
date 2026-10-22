# Optional NEXT STAGE: initially empty. Only configure when both teammates
# have supplied real AWS account ID and VPC ID.
resource "aws_vpc_peering_connection" "service" {
  for_each = var.service_peer_vpcs

  vpc_id        = aws_vpc.was.id
  peer_owner_id = each.value.account_id
  peer_vpc_id   = each.value.vpc_id
  peer_region   = "ap-northeast-2"
  auto_accept   = false

  tags = { Name = "WAS-to-${each.key}" }
}

locals {
  accepted_services = {
    for role, peer in var.service_peer_vpcs : role => peer
    if contains(var.accepted_service_peers, role)
  }
}

resource "aws_route" "service_private_1" {
  for_each                  = local.accepted_services
  route_table_id            = aws_route_table.private_1.id
  destination_cidr_block    = each.value.cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.service[each.key].id
}

resource "aws_route" "service_private_2" {
  for_each                  = local.accepted_services
  route_table_id            = aws_route_table.private_2.id
  destination_cidr_block    = each.value.cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.service[each.key].id
}

resource "aws_vpc_peering_connection_options" "service_requester_dns" {
  for_each                  = local.accepted_services
  vpc_peering_connection_id = aws_vpc_peering_connection.service[each.key].id

  requester {
    allow_remote_vpc_dns_resolution = true
  }
}


# IDS/IPS 피어링 라우팅 추가
# 기존 활성화된 피어링 연결 사용

resource "aws_route" "ids_private_1" {
  route_table_id            = aws_route_table.private_1.id
  destination_cidr_block    = "10.50.0.0/16"
  vpc_peering_connection_id = "pcx-01b0aceae200ecc21"
}

resource "aws_route" "ids_private_2" {
  route_table_id            = aws_route_table.private_2.id
  destination_cidr_block    = "10.50.0.0/16"
  vpc_peering_connection_id = "pcx-01b0aceae200ecc21"
}
