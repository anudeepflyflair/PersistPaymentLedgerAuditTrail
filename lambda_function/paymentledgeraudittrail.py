import boto3
import os
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timezone
from decimal import Decimal

# Retrieve environment variables
DYNAMODB_LEDGER_TABLE_NAME = os.getenv('DYNAMODB_LEDGER_TABLE_NAME')
DYNAMODB_AUDIT_TABLE_NAME = os.getenv('DYNAMODB_AUDIT_TABLE_NAME')
KMS_KEY_ARN = os.getenv('KMS_KEY_ARN')

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
kms_client = boto3.client('kms')

# Connect to DynamoDB tables
payment_ledger_table = dynamodb.Table(DYNAMODB_LEDGER_TABLE_NAME)
audit_table = dynamodb.Table(DYNAMODB_AUDIT_TABLE_NAME)

# Helper Function: Encrypt SecureToken using KMS
def encrypt_token(token):
    try:
        response = kms_client.encrypt(
            KeyId=KMS_KEY_ARN,  # KMS Key ARN
            Plaintext=token.encode('utf-8')
        )
        return response['CiphertextBlob']
    except ClientError as e:
        raise Exception(f"Error encrypting token: {e.response['Error']['Message']}")

# Step 1: Persist Payment Ledger Entry (Payment Initiation)
def persist_payment_ledger(amount, processor_id):
    transaction_id = str(uuid.uuid4())  # Unique Transaction ID
    status = "PAYMENT-INITIATED"
    
    try:
        # Create ledger entry for payment initiation
        payment_ledger_table.put_item(
            Item={
                'TransactionID': transaction_id,
                'Amount': amount,
                'ProcessorID': processor_id,
                'Status': status,
                'Timestamp': str(datetime.utcnow())
            }
        )
        return transaction_id
    except ClientError as e:
        raise Exception(f"Error storing payment initiation: {e.response['Error']['Message']}")

# Step 2: Encrypt Token for Processor
def create_secure_token(amount, processor_id):
    token = f"TokenFor:{amount}:{processor_id}"  # Create a mock token (this would usually be data-sensitive)
    encrypted_token = encrypt_token(token)
    return encrypted_token

# Step 3: Update Payment Status to Pending
def update_payment_status(transaction_id, status):
    try:
        # Update ledger with payment pending status
        payment_ledger_table.update_item(
            Key={'TransactionID': transaction_id},
            UpdateExpression="set #status = :status",
            ExpressionAttributeNames={'#status': 'Status'},
            ExpressionAttributeValues={':status': status},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        raise Exception(f"Error updating payment status: {e.response['Error']['Message']}")

# Step 4: Process Payment Success
def process_payment_success(transaction_id, amount, processor_id):
    status = "PAYMENT-SUCCESS"
    
    try:
        # Update ledger with payment success status
        payment_ledger_table.update_item(
            Key={'TransactionID': transaction_id},
            UpdateExpression="set #status = :status",
            ExpressionAttributeNames={'#status': 'Status'},
            ExpressionAttributeValues={':status': status},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        raise Exception(f"Error processing payment success: {e.response['Error']['Message']}")

# Step 5: Persist Payment Success Ledger Entry
def persist_payment_success(transaction_id, amount, processor_id):
    status = "PAYMENT-SUCCESS"
    
    try:
        # Create new ledger entry for payment success
        payment_ledger_table.put_item(
            Item={
                'TransactionID': transaction_id,
                'Amount': amount,
                'ProcessorID': processor_id,
                'Status': status,
                'Timestamp': str(datetime.utcnow())
            }
        )
    except ClientError as e:
        raise Exception(f"Error creating payment success entry: {e.response['Error']['Message']}")

# Step 6: Create Audit Trail for Successful Payment
def persist_payment_audit_trail(transaction_id, query_details, response_data):
    try:
        # Generate a unique AuditID
        audit_id = str(uuid.uuid4())  # Ensure a unique ID for the audit entry
        
        # Add the AuditID to the audit item
        audit_table.put_item(
            Item={
                'AuditID': audit_id,               # Unique primary key
                'TransactionID': transaction_id,   # Foreign key to payment ledger
                'QueryDetails': query_details,     # Audit information
                'ResponseData': response_data,     # Processor response or other details
                'Timestamp': str(datetime.now(timezone.utc))  # Time in UTC with timezone
            }
        )
    except ClientError as e:
        raise Exception(f"Error creating audit trail: {e.response['Error']['Message']}")

# Step 7: Normalize Processor Response
def normalize_processor_response(response):
    if response['status'] == 'success':
        return 'PAYMENT-SUCCESS'
    elif response['status'] == 'failure':
        return 'PAYMENT-FAILED'
    else:
        return 'PAYMENT-PENDING'

# Step 8: Send Success Response to API
def send_payment_success_response(transaction_id):
    return {
        'statusCode': 200,
        'body': f'Payment completed successfully for transaction {transaction_id}'
    }

# Main Handler Function
def lambda_handler(event, context):
    try:
        # Step 1: Persist Payment Initiation
        amount = Decimal(str(event['amount']))
        processor_id = event['processor_id']
        transaction_id = persist_payment_ledger(amount, processor_id)
        
        # Step 2: Create and Encrypt Secure Token
        encrypted_token = create_secure_token(amount, processor_id)
        
        # Step 3: Update Payment Status to Pending
        update_payment_status(transaction_id, "PAYMENT-PENDING")
        
        # Step 4: Simulate Payment Processor Response (Example: Payroc)
        processor_response = {
            'status': 'success',  # Simulate a successful payment response from Payroc
            'transaction_id': transaction_id,
            'amount': amount,
            'processor_id': processor_id
        }
        
        # Step 5: Process Payment Success
        if processor_response['status'] == 'success':
            process_payment_success(transaction_id, amount, processor_id)
        
        # Step 6: Persist Payment Success Ledger Entry
        persist_payment_success(transaction_id, amount, processor_id)
        
        # Step 7: Create Audit Trail for Payment
        query_details = f"Payment initiated with amount: {amount} and processor: {processor_id}"
        response_data = f"Payment processed successfully with status: {processor_response['status']}"
        persist_payment_audit_trail(transaction_id, query_details, response_data)
        
        # Step 8: Send Success Response to API
        return send_payment_success_response(transaction_id)
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error in payment processing flow: {str(e)}"
        }