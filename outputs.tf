# Output the ARN for Payment Audit Key
output "payment_audit_key_arn" {
  value       = aws_kms_key.ledger_audit_key.arn
  description = "ARN of the KMS key used for Payment Audit Trail encryption"
}

# Output the ARN for Payment Ledger Table
output "payment_ledger_table_name" {
  description = "Name of the PaymentLedger DynamoDB table"
  value       = aws_dynamodb_table.payment_ledger.name
}

# Output the ARN for Payment Audit Trail Table
output "payment_audit_trail_table_name" {
  description = "Name of the PaymentAuditTrail DynamoDB table"
  value       = aws_dynamodb_table.payment_audit_trail.name
}

# Output the ARN for the Lambda function
output "lambda_function_arn" {
  description = "ARN of the Lambda function for persisting payment ledger"
  value       = aws_lambda_function.paymentledgeraudittrail.arn
}
# Output the ARN for the Lambda function
output "lambda_function_name" {
  description = "Name of the Lambda function for persisting payment ledger"
  value       = aws_lambda_function.paymentledgeraudittrail.function_name
}

# Output the ARN for the IAM Role
output "iam_role_arn" {
  description = "ARN of the IAM Role used by the Lambda function"
  value       = aws_iam_role.paymentaudittrail_role.arn
}

# backup table output
# Output for Backup Vault ARN
output "payment_backup_vault_arn" {
  description = "The ARN of the AWS Backup Vault for Payment Ledger and Audit Trail"
  value       = aws_backup_vault.payment_backup_vault.arn
}

# Output for Backup Plan ID
output "payment_backup_plan_id" {
  description = "The ID of the AWS Backup Plan for Payment Ledger and Audit Trail"
  value       = aws_backup_plan.payment_backup_plan.id
}

# Output for IAM Role ARN for Backup
output "backup_role_arn" {
  description = "The ARN of the IAM Role used for AWS Backup Selection"
  value       = aws_iam_role.backup_role.arn
}

# Output for Backup Selection ID
output "payment_backup_selection_id" {
  description = "The ID of the AWS Backup Selection for DynamoDB tables"
  value       = aws_backup_selection.payment_backup_selection.id
}

# Backup for DynamoDB to S3
# Output for the DynamoDB Backup Lambda ARN
output "dynamodb_backup_lambda_arn" {
  description = "ARN of the DynamoDB backup Lambda function"
  value       = aws_lambda_function.dynamodb_backup.arn
}

# Output for the S3 Bucket used for DynamoDB Backup
output "dynamodb_backup_s3_bucket" {
  description = "S3 bucket name for DynamoDB backups"
  value       = aws_s3_bucket.dynamodb_backup.bucket
}

# Output for Lambda Function Timeout (for backup Lambda)
output "dynamodb_backup_lambda_timeout" {
  description = "Timeout for the DynamoDB backup Lambda function"
  value       = aws_lambda_function.dynamodb_backup.timeout
}