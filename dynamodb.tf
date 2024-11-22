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
    name = "Amount"
    type = "N"
  }

  attribute {
    name = "Source"
    type = "S"  # Added Source attribute
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
    name = "OriginalTransactionID"
    type = "S" # Reference to the original transaction for voids
  }

  attribute {
    name = "Reason"
    type = "S" # Reason for the void/reversal
  }

  # Global Secondary Indexes for querying by attributes that need indexing
  global_secondary_index {
    name            = "Amount-index"
    hash_key        = "Amount"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Source-index"
    hash_key        = "Source"  # Index for Source
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Status-index"
    hash_key        = "Status"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Timestamp-index"
    hash_key        = "Timestamp"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "OriginalTransactionID-index"
    hash_key        = "OriginalTransactionID"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Reason-index"
    hash_key        = "Reason"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  tags = {
    Name = "${var.dynamodb_table_name}-ledger"
  }
}
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

  attribute {
    name = "VoidTransactionID"
    type = "S" # Index this attribute if you need to query by it
  }

  attribute {
    name = "Reason"
    type = "S" # Index this attribute if you need to query by it
  }

  attribute {
    name = "Source"
    type = "S"  # Added Source attribute
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

  global_secondary_index {
    name            = "VoidTransactionID-Index"
    hash_key        = "VoidTransactionID"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Reason-Index"
    hash_key        = "Reason"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "Source-Index"
    hash_key        = "Source"  # Index for Source
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  tags = {
    Name = "${var.dynamodb_table_name}-audit-trail"
  }
}