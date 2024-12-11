# payment_ledger
resource "aws_dynamodb_table" "payment_ledger" {
  name         = "${var.dynamodb_table_name}-Ledger"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "transaction_id"
  range_key    = "process_type"

  attribute {
    name = "transaction_id"
    type = "S"
  }

  attribute {
    name = "process_type"
    type = "S"
  }

  attribute {
    name = "payment_processor"
    type = "S"
  }

  attribute {
    name = "merchant_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "error_code"
    type = "S"
  }

  attribute {
    name = "gateway_response"
    type = "S"
  }

  attribute {
    name = "response_details"
    type = "S"
  }

  attribute {
    name = "transaction_origin"
    type = "S"
  }

  attribute {
    name = "card_type"
    type = "S"
  }

  attribute {
    name = "PNR"
    type = "S"
  }

  global_secondary_index {
    name            = "payment_processor-index"
    hash_key        = "payment_processor"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "merchant_id-index"
    hash_key        = "merchant_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "status-index"
    hash_key        = "status"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "error_code-index"
    hash_key        = "error_code"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "gateway_response-index"
    hash_key        = "gateway_response"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "response_details-index"
    hash_key        = "response_details"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "transaction_origin-index"
    hash_key        = "transaction_origin"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "card_type-index"
    hash_key        = "card_type"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "PNR-index"
    hash_key        = "PNR"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "${var.dynamodb_table_name}-Ledger"
  }
}

# payment_audit_trail
resource "aws_dynamodb_table" "payment_audit_trail" {
  name         = "${var.dynamodb_table_name}-AuditTrail"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "audit_id"
  range_key    = "transaction_id"

  attribute {
    name = "audit_id"
    type = "S"
  }

  attribute {
    name = "transaction_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "action_type"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "source_ip"
    type = "S"
  }

  attribute {
    name = "action_details"
    type = "S"
  }

  attribute {
    name = "payment_result"
    type = "S"
  }

  attribute {
    name = "error_code"
    type = "S"
  }

  attribute {
    name = "PNR"
    type = "S"
  }

  global_secondary_index {
    name            = "transaction_id-index"
    hash_key        = "transaction_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "user_id-index"
    hash_key        = "user_id"
    range_key       = "action_type"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "action_details-index"
    hash_key        = "action_details"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "error_code-index"
    hash_key        = "error_code"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "payment_result-index"
    hash_key        = "payment_result"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "source_ip-index"
    hash_key        = "source_ip"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "PNR-index"
    hash_key        = "PNR"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "${var.dynamodb_table_name}-AuditTrail"
  }
}