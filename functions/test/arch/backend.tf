terraform {
  backend "s3" {
    bucket = "friction-terraform-state-bucket"
    key    = "lambda_template.tfstate"
    region = "us-east-2"
  }
}