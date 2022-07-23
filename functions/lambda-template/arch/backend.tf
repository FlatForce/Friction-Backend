terraform {
  backend "s3" {
    bucket = var.state_bucket
    key    = "lambda_template.tfstate"
    region = var.region
  }
}