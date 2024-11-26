
import boto3
import os
import uuid
import json
from datetime import datetime, timezone
from decimal import Decimal
import logging
import requests

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Retrieve environment variables
DYNAMODB_LEDGER_TABLE_NAME = os.getenv('DYNAMODB_LEDGER_TABLE_NAME')
DYNAMODB_AUDIT_TABLE_NAME = os.getenv('DYNAMODB_AUDIT_TABLE_NAME')
KMS_KEY_ARN = os.getenv('KMS_KEY_ARN')
ELAVON_API_URL = os.getenv('ELAVON_API_URL')  # The Elavon API endpoint
ELAVON_API_AUTH_TOKEN = os.getenv('ELAVON_API_AUTH_TOKEN')  # The Elavon API key

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
            KeyId=KMS_KEY_ARN,
            Plaintext=token.encode('utf-8')
        )
        return response['CiphertextBlob']
    except ClientError as e:
        logger.error(f"Error encrypting token: {e.response['Error']['Message']}")
        raise Exception(f"Error encrypting token: {e.response['Error']['Message']}")

# Step 1: Persist Payment Ledger Entry
def persist_payment_ledger(amount, processor_id, source, transaction_type):
    transaction_id = str(uuid.uuid4())
    status = "Initiated"
    try:
        payment_ledger_table.put_item(
            Item={
                'TransactionID': transaction_id,
                'Amount': amount,
                'ProcessorID': processor_id,
                'Status': status,
                'Source': source,  # Include source in the ledger entry
                'TransactionType': transaction_type,  # Store the transaction type
                'Timestamp': str(datetime.utcnow())
            }
        )
        logger.info(f"Payment ledger entry created for transaction {transaction_id} from source {source} of type {transaction_type}")
        return transaction_id
    except ClientError as e:
        logger.error(f"Error storing payment initiation: {e.response['Error']['Message']}")
        raise Exception(f"Error storing payment initiation: {e.response['Error']['Message']}")

# Step 2: Create Payment Intent with Elavon
def create_payment_intent(amount, processor_id, currency="USD"):
    payload = {
        "amount": str(amount),
        "currency": currency,
        "processor_id": processor_id
    }
    headers = {
        "Authorization": f"Bearer {ELAVON_API_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Send POST request to Elavon API to create a payment intent
        response = requests.post(f"{ELAVON_API_URL}/v1/payment-intent", json=payload, headers=headers)
        response.raise_for_status()  # Will raise an error for invalid responses
        response_data = response.json()
        logger.info(f"Payment intent created: {response_data}")
        return response_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating payment intent with Elavon: {str(e)}")
        raise Exception(f"Error creating payment intent with Elavon: {str(e)}")

# Step 3: Update Payment Status (Success/Failure)
def update_payment_status(transaction_id, status):
    try:
        payment_ledger_table.update_item(
            Key={'TransactionID': transaction_id},
            UpdateExpression="set #status = :status",
            ExpressionAttributeNames={'#status': 'Status'},
            ExpressionAttributeValues={':status': status},
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Payment status updated for transaction {transaction_id} to {status}")
    except ClientError as e:
        logger.error(f"Error updating payment status: {e.response['Error']['Message']}")
        raise Exception(f"Error updating payment status: {e.response['Error']['Message']}")

# Step 4: Process Payment Success Response
def process_payment_success(transaction_id, processor_response, source, transaction_type):
    status = processor_response.get('status', '').lower()
    
    try:
        if status == 'success':
            update_payment_status(transaction_id, "Success")
            logger.info(f"Payment successful for transaction {transaction_id}")
            if transaction_type == "Refund":
                logger.info(f"Refund processed successfully for transaction {transaction_id}")
            return {
                'statusCode': 200,
                'body': f"Payment succeeded for transaction {transaction_id}"
            }
        elif status == 'failed':
            update_payment_status(transaction_id, "Failed")
            logger.error(f"Payment failed for transaction {transaction_id}")
            return {
                'statusCode': 400,
                'body': f"Payment failed for transaction {transaction_id}"
            }
        else:
            update_payment_status(transaction_id, "Pending")
            logger.info(f"Payment is pending for transaction {transaction_id}")
            return {
                'statusCode': 202,
                'body': f"Payment is pending for transaction {transaction_id}"
            }
    except Exception as e:
        logger.error(f"Error processing payment success: {str(e)}")
        raise Exception(f"Error processing payment success: {str(e)}")

# Step 5: Persist Payment Audit Trail
def persist_payment_audit_trail(transaction_id, query_details, response_data, source):
    try:
        audit_id = str(uuid.uuid4())
        audit_table.put_item(
            Item={
                'AuditID': audit_id,
                'TransactionID': transaction_id,
                'QueryDetails': query_details,
                'ResponseData': response_data,
                'Source': source,  # Include source in the audit trail
                'Timestamp': str(datetime.now(timezone.utc))
            }
        )
        logger.info(f"Audit trail created for transaction {transaction_id} from source {source}")
    except ClientError as e:
        logger.error(f"Error creating audit trail: {e.response['Error']['Message']}")
        raise Exception(f"Error creating audit trail: {e.response['Error']['Message']}")

# Lambda Handler Function
def lambda_handler(event, context):
    try:
        # Extract and validate input
        amount = Decimal(str(event['amount']))
        processor_id = event['processor_id']
        source = event.get('source', 'unknown')  # Capture source from event, default to 'unknown'
        transaction_type = event.get('transaction_type', 'Sale')  # Default to 'Sale' if not specified
        simulate_status = event.get('simulate_status', '').lower()

        # Step 1: Persist the payment ledger entry
        transaction_id = persist_payment_ledger(amount, processor_id, source, transaction_type)

        # Step 2: Create Payment Intent with Elavon
        payment_intent_response = create_payment_intent(amount, processor_id)

        # Step 3: Simulate the processor response (In a real scenario, this would be a callback or webhook from Elavon)
        processor_response = {
            'status': simulate_status,
            'transaction_id': transaction_id,
            'amount': amount,
            'processor_id': processor_id
        }

        # Step 4: Process the simulated payment success response
        return process_payment_success(transaction_id, processor_response, source, transaction_type)

    except Exception as e:
        logger.error(f"Error in payment processing flow: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error in payment processing flow: {str(e)}"
        }
