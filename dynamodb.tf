# Record all payment transaction details securely in the PaymentLedger DynamoDB

resource "aws_dynamodb_table" "payment_ledger" {
  name           = "${var.dynamodb_table_name}-Ledger"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # Enable Point-in-Time Recovery (PITR)
  point_in_time_recovery {
    enabled = true
  }

  hash_key = "TransactionID"
  attribute {
    name = "TransactionID"
    type = "S"
  }

  attribute {
    name = "SecureToken"
    type = "S"
  }

  attribute {
    name = "Amount"
    type = "N"
  }

  attribute {
    name = "ProcessorID"
    type = "S"
  }

  attribute {
    name = "Status"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "S"
  }

  attribute {
    name = "PaymentProcessor"
    type = "S"
  }

  attribute {
    name = "Metadata"
    type = "S" # Stored as a string (JSON string)
  }

  # Add Global Secondary Index for Amount
  global_secondary_index {
    name            = "Amount-index"
    hash_key        = "Amount"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  # Add Global Secondary Index for SecureToken
  global_secondary_index {
    name            = "SecureToken-index"
    hash_key        = "SecureToken"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  # Add Global Secondary Index for ProcessorID
  global_secondary_index {
    name            = "ProcessorID-index"
    hash_key        = "ProcessorID"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  # Add Global Secondary Index for Status
  global_secondary_index {
    name            = "Status-index"
    hash_key        = "Status"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  # Add Global Secondary Index for Timestamp
  global_secondary_index {
    name            = "Timestamp-index"
    hash_key        = "Timestamp"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  # Add Global Secondary Index for PaymentProcessor
  global_secondary_index {
    name            = "PaymentProcessor-index"
    hash_key        = "PaymentProcessor"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  # Add Global Secondary Index for Metadata (if you need to query it)
  global_secondary_index {
    name            = "Metadata-index"
    hash_key        = "Metadata"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  tags = {
    Name = "${var.dynamodb_table_name}-ledger"
  }
}


# Maintain a log of every access and update to the PaymentLedger for compliance and traceability.

resource "aws_dynamodb_table" "payment_audit_trail" {
  name           = "${var.dynamodb_table_name}-AuditTrail"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # Enable Point-in-Time Recovery (PITR)
  point_in_time_recovery {
    enabled = true
  }

  hash_key = "AuditID"

  attribute {
    name = "AuditID"
    type = "S"
  }

  attribute {
    name = "TransactionID"
    type = "S"
  }

  attribute {
    name = "Action"
    type = "S"
  }

  attribute {
    name = "Actor"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "S"
  }

  attribute {
    name = "QueryDetails"
    type = "S"
  }

  attribute {
    name = "Response"
    type = "S"
  }

  # Global Secondary Indexes (GSI)
  global_secondary_index {
    name            = "TransactionID-Index"
    hash_key        = "TransactionID"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Action-Index"
    hash_key        = "Action"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Timestamp-Index"
    hash_key        = "Timestamp"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Actor-Index"
    hash_key        = "Actor"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "QueryDetails-Index"
    hash_key        = "QueryDetails"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Response-Index"
    hash_key        = "Response"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  tags = {
    Name = "${var.dynamodb_table_name}AuditTrail"
  }
}