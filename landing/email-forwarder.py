import json
import boto3
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def lambda_handler(event, context):
    # Get the S3 bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Initialize S3 and SES clients
    s3 = boto3.client('s3')
    ses = boto3.client('ses', region_name='us-east-1')
    
    try:
        # Get the email from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        email_content = response['Body'].read()
        
        # Parse the email
        msg = email.message_from_bytes(email_content)
        
        # Extract email details
        from_addr = msg.get('From', '')
        to_addr = msg.get('To', '')
        subject = msg.get('Subject', '')
        
        # Create forwarded email
        forward_msg = MIMEMultipart()
        forward_msg['From'] = from_addr
        forward_msg['To'] = 'qspencer@gmail.com'
        forward_msg['Subject'] = f'[FORWARDED] {subject} (Originally to: {to_addr})'
        
        # Add original email details
        forward_text = f"""This email was originally sent to: {to_addr}
Original sender: {from_addr}
Original subject: {subject}

--- Original Message ---
"""
        
        # Get email body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    forward_text += body
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            forward_text += body
        
        forward_msg.attach(MIMEText(forward_text, 'plain'))
        
        # Send the forwarded email
        ses.send_raw_email(
            Source=from_addr,
            Destinations=['qspencer@gmail.com'],
            RawMessage={'Data': forward_msg.as_string()}
        )
        
        # Delete the email from S3 after forwarding
        s3.delete_object(Bucket=bucket, Key=key)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Email forwarded successfully')
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }