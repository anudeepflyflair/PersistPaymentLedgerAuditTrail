
# AWS KMS Key for Encryption &  Decryption

# AWS KMS Key for Payment Audit Trail Encryption & Decryption
resource "aws_kms_key" "ledger_audit_key" {
  description = "KMS key for PaymentLedger Audit Trail encryption"
  key_usage   = "ENCRYPT_DECRYPT"
}

# KMS Alias for Payment Audit Trail Key
resource "aws_kms_alias" "ledger_audit_key_alias" {
  name          = "alias/${var.dynamodb_table_name}-Ledgeraudit-key"
  target_key_id = aws_kms_key.ledger_audit_key.key_id
}