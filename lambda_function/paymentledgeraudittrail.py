import os
import uuid
import boto3
import json
from datetime import datetime, timezone
from decimal import Decimal
import requests
import logging

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")

# Retrieve table names from environment variables with error handling
PAYMENT_LEDGER_TABLE = os.getenv("DYNAMODB_LEDGER_TABLE_NAME")
AUDIT_TRAIL_TABLE = os.getenv("DYNAMODB_AUDIT_TABLE_NAME")
PROCESSOR_URL = os.getenv("PROCESSOR_URL")
API_KEY = os.getenv("API_KEY")

# Check if the environment variables are set
if not PAYMENT_LEDGER_TABLE or not AUDIT_TRAIL_TABLE or not PROCESSOR_URL or not API_KEY:
    logger.error("Required environment variables are missing")
    raise ValueError("Environment variables are not set correctly")

# Initialize tables dynamically
payment_ledger_table = dynamodb.Table(PAYMENT_LEDGER_TABLE)
audit_table = dynamodb.Table(AUDIT_TRAIL_TABLE)

# Step 1: Create Ledger Entry
def create_ledger_entry(transaction_id, process_type, status, details=None):
    try:
        # Ensure that response_details is always a string (JSON string)
        response_details_str = json.dumps(details) if details else "{}"
        
        payment_ledger_table.put_item(
            Item={
                "transaction_id": transaction_id,
                "process_type": process_type,
                "status": status,
                "timestamp": str(datetime.now(timezone.utc)),
                "response_details": response_details_str,  # Pass as string (JSON format)
            }
        )
    except Exception as e:
        logger.error(f"Error creating ledger entry for {transaction_id}: {str(e)}")
        raise Exception(f"Error creating ledger entry: {str(e)}")

# Step 2: Get Security Token from Payment Processor
def get_security_token():
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        logger.info(f"Requesting security token from {PROCESSOR_URL}/security-token")
        
        response = requests.post(f"{PROCESSOR_URL}/security-token", headers=headers)
        
        # Log the raw response details for debugging
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
        logger.info(f"Response Body: {response.text}")
        
        # Check if the response status code is 200 (OK)
        if response.status_code != 200:
            logger.error(f"Failed to get security token. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise Exception(f"Error generating security token: {response.status_code} {response.text}")
        
        # Check if response is valid JSON
        try:
            return response.json()["token"]
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response received: {response.text}")
            raise Exception("Error generating security token: Invalid JSON response")
    
    except Exception as e:
        logger.error(f"Error generating security token: {str(e)}")
        raise Exception(f"Error generating security token: {str(e)}")

# Step 3: Update Ledger for Payment Pending
def update_ledger_status(transaction_id, status, details=None):
    try:
        # Ensure that response_details is always a string (JSON string)
        response_details_str = json.dumps(details) if details else "{}"
        
        payment_ledger_table.update_item(
            Key={"transaction_id": transaction_id},
            UpdateExpression="SET #st = :s, response_details = :rd",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={
                ":s": status,
                ":rd": response_details_str,  # Pass as string (JSON format)
            },
        )
    except Exception as e:
        logger.error(f"Error updating ledger entry for {transaction_id}: {str(e)}")
        raise Exception(f"Error updating ledger entry: {str(e)}")

# Step 4: Process Payment Intent
def process_payment_intent(transaction_id, amount, token):
    try:
        payload = {"transaction_id": transaction_id, "amount": str(amount), "token": token}
        response = requests.post(f"{PROCESSOR_URL}/payment-intent", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error processing payment intent for {transaction_id}: {str(e)}")
        raise Exception(f"Error processing payment intent: {str(e)}")

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
                "action_details": details,
            }
        )
    except Exception as e:
        logger.error(f"Error creating audit entry for {transaction_id}: {str(e)}")
        raise Exception(f"Error creating audit entry: {str(e)}")

# Step 7: Normalize Processor Response
def normalize_response(response):
    return {
        "status": response.get("status", "unknown"),
        "message": response.get("message", "No message provided"),
        "transaction_id": response.get("transaction_id"),
    }

# Step 8: Return Success Response to API Gateway
def lambda_handler(event, context):
    try:
        # Extract input data
        transaction_id = str(uuid.uuid4())
        process_type = event["process_type"]
        amount = Decimal(str(event["amount"]))

        logger.info(f"Processing transaction: {transaction_id}, amount: {amount}, process_type: {process_type}")

        # Step 1: Create Ledger Entry for Payment Initiation
        create_ledger_entry(transaction_id, process_type, "PAYMENT-INITIATED")

        # Step 2: Generate Security Token
        token = get_security_token()

        # Step 3: Create Ledger Entry for Payment Pending
        update_ledger_status(transaction_id, "PAYMENT-PENDING", {"token": token})

        # Step 4: Process Payment Intent
        processor_response = process_payment_intent(transaction_id, amount, token)

        # Step 5: Log Payment Success
        if processor_response["status"].lower() == "success":
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
            logger.error(f"Payment failed for transaction {transaction_id}: {processor_response}")
            raise Exception(f"Payment failed: {processor_response}")

    except Exception as e:
        # Log errors
        logger.error(f"Error processing transaction: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }