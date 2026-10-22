terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}

provider "aws" {
  # VS Code can launch a new PowerShell; using the saved profile avoids
  # accidentally falling back to a different/default AWS account.
  profile             = "safetravel-terraform"
  region              = "ap-northeast-2"
  allowed_account_ids = ["423333378996"]

  default_tags {
    tags = {
      Project   = "SafeTravel"
      Role      = "WAS"
      ManagedBy = "Terraform"
    }
  }
}
