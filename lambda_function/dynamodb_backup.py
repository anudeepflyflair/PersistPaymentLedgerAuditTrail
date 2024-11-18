import boto3
import json
import os
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
DYNAMODB_LEDGER_TABLE = os.getenv('DYNAMODB_LEDGER_TABLE_NAME')
DYNAMODB_AUDIT_TABLE = os.getenv('DYNAMODB_AUDIT_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BACKUP_BUCKET_NAME')

# Tables
payment_ledger_table = dynamodb.Table(DYNAMODB_LEDGER_TABLE)
payment_audit_table = dynamodb.Table(DYNAMODB_AUDIT_TABLE)

def backup_to_s3(data, file_name):
    try:
        # Store the data in S3 as a JSON file
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f'backup/{file_name}',
            Body=json.dumps(data)
        )
        print(f"Backup successful: {file_name}")
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")

def lambda_handler(event, context):
    try:
        # Query payment ledger and audit trail data
        ledger_data = payment_ledger_table.scan()
        audit_data = payment_audit_table.scan()
        
        # Backup the data to S3
        timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
        backup_to_s3(ledger_data['Items'], f'payment_ledger_backup_{timestamp}.json')
        backup_to_s3(audit_data['Items'], f'payment_audit_backup_{timestamp}.json')
        
        return {
            'statusCode': 200,
            'body': 'Backup completed successfully.'
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error during backup: {str(e)}"
        }