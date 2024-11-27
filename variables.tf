# AWS Region where resources will be deployed
variable "aws_region" {
  type        = string
  description = "AWS Region to deploy resources"
}

# dynamodb_table_name
variable "dynamodb_table_name" {
  type        = string
  description = "Name of the DynamoDB table for Payment Ledger"
}

# s3_backup_bucket_name
variable "s3_backup_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for DynamoDB backup"
}

# elavon_api_url
variable "paynuity_api_url" {
  type        = string
  description = "Paynuity API URL"
}

# elavon_api
variable "paynuity_api_key" {
  type        = string
  description = "Paynuity API Key"
}