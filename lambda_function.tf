resource "aws_lambda_function" "paymentledgeraudittrail" {
  function_name    = "${var.dynamodb_table_name}-ledgeraudittrail"
  role             = aws_iam_role.paymentaudittrail_role.arn
  handler          = "paymentledgeraudittrail.lambda_handler"
  runtime          = "python3.8"
  filename         = "lambda_function/paymentledgeraudittrail.zip"
  source_code_hash = filebase64sha256("lambda_function/paymentledgeraudittrail.zip")

  environment {
    variables = {
      DYNAMODB_LEDGER_TABLE_NAME = aws_dynamodb_table.payment_ledger.name
      DYNAMODB_AUDIT_TABLE_NAME  = aws_dynamodb_table.payment_audit_trail.name
      KMS_KEY_ARN          = aws_kms_alias.ledger_audit_key_alias.arn
      PAYROC_API_URL              = var.payroc_api_url
      PAYROC_AUTH_TOKEN                    = var.payroc_auth_token
    }
  }

  timeout = 300

  vpc_config {
    subnet_ids         = [data.aws_subnet.private_subnet.id]
    security_group_ids = [data.aws_security_group.private_sg.id]
  }
}

resource "aws_lambda_function" "dynamodb_backup" {
  filename      = "lambda_function/dynamodb_backup.zip"
  function_name = "LedgerAuditTrail-dynamodb_backup"
  role          = aws_iam_role.paymentaudittrail_role.arn
  handler       = "dynamodb_backup.lambda_handler"
  runtime       = "python3.9"

  environment {
    variables = {
      DYNAMODB_LEDGER_TABLE_NAME = aws_dynamodb_table.payment_ledger.name
      DYNAMODB_AUDIT_TABLE_NAME  = aws_dynamodb_table.payment_audit_trail.name
      S3_BACKUP_BUCKET_NAME      = aws_s3_bucket.dynamodb_backup.id
    }
  }

  timeout = 300

  vpc_config {
    subnet_ids         = [data.aws_subnet.private_subnet.id]
    security_group_ids = [data.aws_security_group.private_sg.id]
  }
}