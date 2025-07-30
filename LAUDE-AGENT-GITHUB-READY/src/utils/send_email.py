# === File: send_email.py ===
import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def send_email(report_html, subject=None, attachment_path=None):
    """Send email with report using Outlook/Office 365 SMTP"""
    try:
        # Get email configuration from environment
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        email_to = os.getenv('EMAIL_TO')
        
        if not all([email_user, email_pass, email_to]):
            logger.error("Email configuration incomplete")
            print("CROSS Email configuration incomplete. Check your .env file:")
            print("   Required: EMAIL_USER, EMAIL_PASS, EMAIL_TO")
            return False
        
        # Parse recipient list
        recipients = [email.strip() for email in email_to.split(',')]
        
        print(f"EMAIL Preparing email...")
        print(f"   From: {email_user}")
        print(f"   To: {recipients}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        
        # Set default subject if not provided
        if not subject:
            subject = f"Weekly Report - {datetime.now().strftime('%B %d, %Y')}"
        
        msg['Subject'] = subject
        msg['From'] = email_user
        msg['To'] = ', '.join(recipients)
        
        # Create plain text version (fallback)
        plain_text = create_plain_text_version(report_html)
        
        # Attach both plain text and HTML versions
        part_text = MIMEText(plain_text, 'plain', 'utf-8')
        part_html = MIMEText(report_html, 'html', 'utf-8')
        
        msg.attach(part_text)
        msg.attach(part_html)
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            attach_file(msg, attachment_path)
        
        # Send email using Office 365 SMTP
        print("OUTBOX Connecting to Office 365 SMTP...")
        
        # Office 365 SMTP settings
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS encryption
            
            print("LOCK Authenticating...")
            server.login(email_user, email_pass)
            
            print("SEND Sending email...")
            text = msg.as_string()
            server.sendmail(email_user, recipients, text)
        
        print("CHECK Email sent successfully!")
        logger.info(f"Email sent to {recipients}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed")
        print("CROSS Email authentication failed. Check your credentials:")
        print("   - Verify EMAIL_USER and EMAIL_PASS in .env")
        print("   - Use app-specific password for Office 365")
        print("   - Enable 2FA and generate app password")
        return False
    
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        print(f"CROSS SMTP error: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        print(f"CROSS Email sending error: {str(e)}")
        return False

def create_plain_text_version(html_content):
    """Create a plain text version of the HTML report"""
    try:
        # Remove HTML tags and format as plain text
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        import html
        text = html.unescape(text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Add email header
        header = f"""
WEEKLY REPORT - {datetime.now().strftime('%B %d, %Y')}
{'=' * 50}

This is a plain text version of your weekly report.
For better formatting, please view the HTML version.

{'=' * 50}

"""
        
        return header + text.strip()
    
    except Exception as e:
        logger.error(f"Error creating plain text version: {str(e)}")
        return "Weekly report attached. Please view HTML version for proper formatting."

def attach_file(msg, file_path):
    """Attach a file to the email message"""
    try:
        filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        
        msg.attach(part)
        print(f"CLIP Attachment added: {filename}")
        
    except Exception as e:
        logger.error(f"Error attaching file {file_path}: {str(e)}")
        print(f"WARNING  Could not attach file: {file_path}")

def test_email_connection():
    """Test email connection and configuration"""
    try:
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        
        if not email_user or not email_pass:
            print("CROSS Email credentials not found in .env file")
            return False
        
        print("SEARCH Testing email connection...")
        print(f"   User: {email_user}")
        
        # Test connection to Office 365
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
        
        print("CHECK Email connection successful!")
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("CROSS Authentication failed. Check credentials and app password.")
        return False
    except Exception as e:
        print(f"CROSS Connection test failed: {str(e)}")
        return False

def send_test_email():
    """Send a test email to verify configuration"""
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Email</title>
    </head>
    <body>
        <h1>EMAIL Email Test Successful!</h1>
        <p>This is a test email from your Weekly Report AI Assistant.</p>
        <p><strong>Time:</strong> {}</p>
        <p>If you received this email, your configuration is working correctly!</p>
    </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d %I:%M %p'))
    
    subject = "Test Email - Weekly Report AI"
    
    return send_email(test_html, subject)

def get_email_templates():
    """Get predefined email templates"""
    templates = {
        'weekly_report': {
            'subject': 'Weekly Report - {date}',
            'intro': 'Please find my weekly report attached below.',
            'outro': 'Please let me know if you have any questions.'
        },
        'status_update': {
            'subject': 'Project Status Update - {date}',
            'intro': 'Here is the latest status update on current projects.',
            'outro': 'Looking forward to your feedback.'
        },
        'monthly_summary': {
            'subject': 'Monthly Summary - {date}',
            'intro': 'Please find the monthly summary report below.',
            'outro': 'Thank you for your continued support.'
        }
    }
    
    return templates

def create_email_signature():
    """Create a professional email signature"""
    signature = """
    <br><br>
    <div style="border-top: 1px solid #ccc; padding-top: 15px; margin-top: 20px; font-size: 0.9em; color: #666;">
        <p><strong>Generated automatically by AI Voice-to-Report Assistant</strong></p>
        <p>📅 {date} | ROBOT Powered by OpenAI</p>
    </div>
    """.format(date=datetime.now().strftime('%Y-%m-%d'))
    
    return signature

if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.INFO)
    
    print("EMAIL Email System Test Mode")
    print("=" * 30)
    
    # Test email connection
    if test_email_connection():
        
        # Ask user if they want to send test email
        response = input("\nTHINKING Send test email? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\nOUTBOX Sending test email...")
            
            if send_test_email():
                print("CHECK Test email sent successfully!")
            else:
                print("CROSS Test email failed")
        else:
            print("CHECK Email connection verified. Skipping test email.")
    
    else:
        print("CROSS Email connection test failed")
        print("\nWRENCH Setup instructions:")
        print("1. Create .env file with EMAIL_USER, EMAIL_PASS, EMAIL_TO")
        print("2. For Office 365, use app-specific password")
        print("3. Enable 2FA and generate app password in Microsoft account")