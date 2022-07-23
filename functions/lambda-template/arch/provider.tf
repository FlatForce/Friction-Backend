terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.region

  assume_role {
    role_arn     = var.role_arn
    session_name = "Friction Terraform"
  }
}

