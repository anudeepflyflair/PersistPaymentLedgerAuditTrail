resource "aws_cloudwatch_event_rule" "monthly_backup_schedule" {
  name                = "monthly_backup_schedule"
  schedule_expression = "cron(0 0 1 * ? *)" # Runs at midnight on the 1st of every month
}

resource "aws_cloudwatch_event_target" "backup_lambda_target" {
  rule      = aws_cloudwatch_event_rule.monthly_backup_schedule.name
  target_id = "dynamodb_backup_target"
  arn       = aws_lambda_function.dynamodb_backup.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dynamodb_backup.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.monthly_backup_schedule.arn
}