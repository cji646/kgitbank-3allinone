variable "soc_peering_accepted" {
  description = "Change to true only after SOC confirms the Peering request is ACTIVE."
  type        = bool
  default     = false
}

variable "service_peer_vpcs" {
  description = "Future Web/DB peers. Start empty; fill only after actual IDs are received."
  type = map(object({
    account_id = string
    vpc_id     = string
    cidr       = string
  }))
  default = {}
}

variable "accepted_service_peers" {
  description = "Roles whose Web/DB VPC Peering requests were accepted."
  type        = set(string)
  default     = []
}
