Payment Processing System
Overview
This system handles payment processing for transactions involving sensitive data, securely storing and managing payment information through AWS services like KMS (Key Management Service), DynamoDB, and Lambda functions. The system includes features such as tokenization, ledger creation, audit trail, and payment status tracking for successful and pending transactions.

Payment Flow Overview
1. Create Ledger Entry for Payment Initiation (PAYMENT-INITIATED)
The persist_payment_ledger function creates an entry in the PaymentLedger DynamoDB table to record the transaction details.
Key information recorded:
TransactionID: Unique identifier for the transaction.
SecureToken: Tokenized payment information.
Amount: The transaction amount.
ProcessorID: Identifies the payment processor (e.g., Payroc).
Status: Set to PAYMENT-INITIATED to mark the start of the transaction.
Outcome
The PaymentLedger stores a record of the payment with the status PAYMENT-INITIATED.
2. Create Security Token (for processor 'Payroc')
The security token (SecureToken) is encrypted using AWS KMS inside the encrypt_token function.
This encryption ensures that sensitive payment data is securely protected before being passed to the payment processor.
The encrypted token is used by the processor (Payroc) to authorize the payment request.
3. Create Ledger Entry for Payment Pending (PAYMENT-PENDING)
After the payment request is initiated but not yet completed, the payment status is updated in the PaymentLedger table to PAYMENT-PENDING.
This reflects that the payment is still being processed by the payment processor.
Outcome
The PaymentLedger entry updates with the status PAYMENT-PENDING.
4. Payment Intent (Processor 'Payroc') Payment Success
Once Payroc processes the payment, it communicates the outcome (success or failure).
If the payment is successful, the payment status is updated to PAYMENT-SUCCESS.
Outcome
The persist_payment_ledger function updates the PaymentLedger table with the new status PAYMENT-SUCCESS.
5. Create Ledger Entry for Payment Success
After a successful payment, a new ledger entry is created to reflect the payment success.
The entry updates the PaymentLedger table with the final payment status.
6. Create Audit Trail for Successful Payment
The persist_payment_audit_trail function creates an audit trail entry for the payment transaction.
The audit logs query details and the response from the payment processor (Payroc).
Both the query details and response are encrypted before being stored in the DynamoDB_AUDIT_TABLE.
Outcome
The audit log is created in the DynamoDB_AUDIT_TABLE with encrypted query details and response information.
7. Normalize Processor Response
After the payment success or failure, the system normalizes the response from the payment processor.
The normalization includes:
Updating payment status in the PaymentLedger.
Logging the success or failure outcome.
8. Success Response to API
After the payment is successfully processed, the system returns a success response to the API, completing the payment flow.
Functions and Operations
encrypt_token Function
Purpose: Encrypts the SecureToken using AWS KMS.
Returns: Encrypted token (Base64-encoded string).
persist_payment_ledger Function
Purpose: Stores payment details (TransactionID, SecureToken, Amount, ProcessorID, Status) in the PaymentLedger DynamoDB table.
Called: When a payment is initiated, updated to pending, or confirmed successful.
persist_payment_audit_trail Function
Purpose: Logs an audit trail for each payment transaction.
Returns: A log of the encrypted query and response details.
Key Components
DynamoDB Tables:

PaymentLedger: Stores transaction details and statuses.
DynamoDB_AUDIT_TABLE: Stores audit logs for transaction-related queries and responses.
AWS KMS: Used for encrypting and decrypting sensitive data (SecureToken).

AWS Lambda: Processes payment flow, encrypts data, updates ledger, and logs audit trails.

Error Handling
Each function is equipped with error handling to ensure that if any issues occur during the payment process, they are logged and returned with relevant error messages.
Environment Variables
PAYMENT_KMS_KEY_ARN: ARN of the KMS key used for encryption.
DYNAMODB_TABLE_NAME: Name of the DynamoDB table for PaymentLedger.
DYNAMODB_AUDIT_TABLE_NAME: Name of the DynamoDB table for audit logs.
Conclusion
This payment processing system provides a secure and efficient flow for handling payment transactions. It ensures data security through tokenization and encryption, tracks payment statuses in a ledger, and logs audit trails for transparency and compliance.