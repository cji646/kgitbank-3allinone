data "aws_caller_identity" "current" {}

output "aws_account_id" {
  value       = data.aws_caller_identity.current.account_id
  description = "Your AWS account ID"
}

output "was_vpc_id" {
  value       = aws_vpc.was.id
  description = "WAS VPC ID"
}

output "was_vpc_cidr" {
  value = aws_vpc.was.cidr_block
}

output "subnet_ids" {
  value = { for role, subnet in aws_subnet.was : role => subnet.id }
}

output "soc_peering_id" {
  value       = aws_vpc_peering_connection.was_to_soc.id
  description = "Send this pcx ID to SOC teammate"
}

output "soc_peering_message" {
  value = "역할: WAS | 계정 ID: ${data.aws_caller_identity.current.account_id} | VPC ID: ${aws_vpc.was.id} | CIDR: 10.30.0.0/16 | Peering ID: ${aws_vpc_peering_connection.was_to_soc.id} | 리전: ap-northeast-2"
}

output "service_peering_ids" {
  value       = { for role, pcx in aws_vpc_peering_connection.service : role => pcx.id }
  description = "Web/DB peers (empty until explicitly configured)"
}
