# AWS Backup Vault for Payment Ledger & Payment Audit Trail (using the same vault with different encryption)
resource "aws_backup_vault" "payment_backup_vault" {
  name        = "${var.dynamodb_table_name}-LedgerAuditTrail-backup-vault"
  kms_key_arn = aws_kms_key.ledger_audit_key.arn # KMS Key for encryption
}

# AWS Backup Plan for daily backups of DynamoDB tables
resource "aws_backup_plan" "payment_backup_plan" {
  name = "${var.dynamodb_table_name}-LedgerAuditTrail-backup-plan"

  rule {
    rule_name         = "daily-backup"
    schedule          = "cron(0 0 1 * ? *)"                        # 1st day of every month at midnight UTC
    target_vault_name = aws_backup_vault.payment_backup_vault.name # Backup vault to use

    lifecycle {
      cold_storage_after = 30  # Move backups to cold storage after 30 days
      delete_after       = 120 # Delete backups after 120 days
    }
  }
}

# IAM Role for AWS Backup Selection
resource "aws_iam_role" "backup_role" {
  name = "${var.dynamodb_table_name}-LedgerAuditTrail-backup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      }
    ]
  })
}

# AWS Backup Selection to select DynamoDB tables for backup
resource "aws_backup_selection" "payment_backup_selection" {
  name         = "${var.dynamodb_table_name}-LedgerAuditTrail-backup-selection"
  plan_id      = aws_backup_plan.payment_backup_plan.id
  iam_role_arn = aws_iam_role.backup_role.arn # IAM Role for Backup Selection
  resources = [
    aws_dynamodb_table.payment_ledger.arn,     # Reference to payment ledger table
    aws_dynamodb_table.payment_audit_trail.arn # Reference to payment audit trail table
  ]
}