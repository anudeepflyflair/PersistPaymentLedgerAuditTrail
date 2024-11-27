import os
import uuid
import boto3
import json
from datetime import datetime, timezone
from decimal import Decimal
import requests
import logging

# Initialize Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")

# Fetch and Validate Environment Variables
PAYMENT_LEDGER_TABLE = os.getenv("DYNAMODB_LEDGER_TABLE_NAME")
AUDIT_TRAIL_TABLE = os.getenv("DYNAMODB_AUDIT_TABLE_NAME")
PROCESSOR_URL = os.getenv("PROCESSOR_URL")
API_KEY = os.getenv("API_KEY")
KMS_KEY_ARN = os.getenv("KMS_KEY_ARN")

if not PAYMENT_LEDGER_TABLE or not AUDIT_TRAIL_TABLE or not PROCESSOR_URL or not API_KEY:
    logger.error("Required environment variables are missing.")
    raise ValueError("Required environment variables are not set correctly.")

# Initialize Tables
payment_ledger_table = dynamodb.Table(PAYMENT_LEDGER_TABLE)
audit_table = dynamodb.Table(AUDIT_TRAIL_TABLE)

# Helper Function: Validate JSON Serialization
def safe_json_serialize(data):
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        logger.error(f"Failed to serialize data to JSON: {data}")
        return "{}"

# Step 1: Create Ledger Entry
def create_ledger_entry(transaction_id, process_type, status, details=None):
    try:
        payment_ledger_table.put_item(
            Item={
                "transaction_id": transaction_id,
                "process_type": process_type,
                "status": status,
                "timestamp": str(datetime.now(timezone.utc)),
                "response_details": safe_json_serialize(details),
            }
        )
    except Exception as e:
        logger.error(f"Error creating ledger entry for transaction {transaction_id}: {str(e)}")
        raise

# Step 2: Get Security Token from Payment Processor
def get_security_token():
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.post(f"{PROCESSOR_URL}/security-token", headers=headers)
        response.raise_for_status()
        token = response.json().get("token")
        if not token:
            raise ValueError("Missing 'token' in processor response")
        return token
    except Exception as e:
        logger.error(f"Error generating security token: {str(e)}")
        raise

# Step 3: Update Ledger for Payment Pending
def update_ledger_status(transaction_id, status, details=None):
    try:
        payment_ledger_table.update_item(
            Key={"transaction_id": transaction_id},
            UpdateExpression="SET #st = :s, response_details = :rd",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={
                ":s": status,
                ":rd": safe_json_serialize(details),
            },
        )
    except Exception as e:
        logger.error(f"Error updating ledger status for transaction {transaction_id}: {str(e)}")
        raise

# Step 4: Process Payment Intent
def process_payment_intent(transaction_id, amount, token):
    try:
        payload = {"transaction_id": transaction_id, "amount": str(amount), "token": token}
        response = requests.post(f"{PROCESSOR_URL}/payment-intent", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error processing payment intent for transaction {transaction_id}: {str(e)}")
        raise

# Step 5: Log Payment Success in Ledger
def log_payment_success(transaction_id, details):
    update_ledger_status(transaction_id, "PAYMENT-SUCCESS", details)

# Step 6: Create Audit Entry for Successful Payment
def create_audit_entry(transaction_id, action_type, details):
    try:
        audit_table.put_item(
            Item={
                "audit_id": str(uuid.uuid4()),
                "transaction_id": transaction_id,
                "action_type": action_type,
                "timestamp": str(datetime.now(timezone.utc)),
                "action_details": safe_json_serialize(details),
            }
        )
    except Exception as e:
        logger.error(f"Error creating audit entry for transaction {transaction_id}: {str(e)}")
        raise

# Step 7: Normalize Processor Response
def normalize_response(response):
    return {
        "status": response.get("status", "unknown"),
        "message": response.get("message", "No message provided"),
        "transaction_id": response.get("transaction_id"),
    }

# Step 8: Lambda Handler
def lambda_handler(event, context):
    try:
        # Extract Input Data
        transaction_id = str(uuid.uuid4())
        process_type = event.get("process_type")
        amount = Decimal(str(event.get("amount", 0)))

        if not process_type or amount <= 0:
            raise ValueError("Invalid input: process_type and amount must be specified and valid")

        logger.info(f"Starting transaction {transaction_id} with amount {amount} and process_type {process_type}")

        # Step 1: Create Ledger Entry for Payment Initiation
        create_ledger_entry(transaction_id, process_type, "PAYMENT-INITIATED")

        # Step 2: Generate Security Token
        token = get_security_token()

        # Step 3: Create Ledger Entry for Payment Pending
        update_ledger_status(transaction_id, "PAYMENT-PENDING", {"token": token})

        # Step 4: Process Payment Intent
        processor_response = process_payment_intent(transaction_id, amount, token)

        # Step 5: Handle Payment Success or Failure
        if processor_response.get("status", "").lower() == "success":
            normalized_response = normalize_response(processor_response)
            log_payment_success(transaction_id, normalized_response)

            # Step 6: Create Audit Entry
            create_audit_entry(transaction_id, "PAYMENT-SUCCESS", normalized_response)

            # Step 8: Return Success Response
            return {
                "statusCode": 200,
                "body": json.dumps({"transaction_id": transaction_id, "status": "success"}),
            }

        else:
            error_message = processor_response.get("message", "Unknown error occurred")
            logger.error(f"Payment failed for transaction {transaction_id}: {error_message}")
            raise ValueError(f"Payment failed: {error_message}")

    except Exception as e:
        logger.error(f"Error in transaction processing: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }