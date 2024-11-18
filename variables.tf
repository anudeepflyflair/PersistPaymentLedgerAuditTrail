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