resource "aws_s3_bucket" "dynamodb_backup" {
  bucket = var.s3_backup_bucket_name

  tags = {
    Name = var.s3_backup_bucket_name
  }
}

resource "aws_s3_bucket_versioning" "dynamodb_backup_versioning" {
  bucket = aws_s3_bucket.dynamodb_backup.id

  versioning_configuration {
    status = "Enabled"
  }
}