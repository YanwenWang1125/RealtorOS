"""Test script for sending emails via Amazon SES using boto3.

This script sends a test email using environment variables for configuration.
Required environment variables:
- AWS_REGION: AWS region for SES (e.g., 'us-east-1')
- SES_FROM_EMAIL: Verified sender email address
- SES_TO_EMAIL: Recipient email address

Before running, ensure:
1. AWS credentials are configured (via AWS CLI or environment variables)
2. The sender email is verified in AWS SES
3. boto3 is installed: pip install boto3
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
load_dotenv()


def check_environment_variables():
    """Check if all required environment variables are set."""
    required_vars = ['AWS_REGION', 'SES_FROM_EMAIL', 'SES_TO_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set the required environment variables before running this script.")
        print("Example:")
        print("  export AWS_REGION=us-east-1")
        print("  export SES_FROM_EMAIL=your-email@example.com")
        print("  export SES_TO_EMAIL=recipient@example.com")
        sys.exit(1)


def send_test_email():
    """Send a test email using Amazon SES."""
    # Check environment variables before proceeding
    check_environment_variables()
    
    # Get configuration from environment variables
    aws_region = os.getenv('AWS_REGION')
    from_email = os.getenv('SES_FROM_EMAIL')
    to_email = os.getenv('SES_TO_EMAIL')
    
    try:
        # Create SES client
        ses = boto3.client('ses', region_name=aws_region)
        
        # Send email
        response = ses.send_email(
            Source=from_email,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': 'Test Email from Amazon SES'},
                'Body': {'Text': {'Data': 'Hello from RealtorOS! This is a test message sent using Amazon SES.'}}
            }
        )
        
        # Print success message with MessageId
        print("✅ Email sent successfully!")
        print(f"Message ID: {response['MessageId']}")
        
    except NoCredentialsError:
        print("Error: AWS credentials not found!")
        print("\nPlease configure your AWS credentials:")
        print("  - Run: aws configure")
        print("  - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        sys.exit(1)
        
    except ClientError as e:
        # Print full error message
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"Error sending email ({error_code}): {error_message}")
        sys.exit(1)
        
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == '__main__':
    send_test_email()

