#!/usr/bin/env python3
"""Outlook-compatible email sending using draft method"""

import os
import webbrowser
from urllib.parse import quote
from datetime import datetime
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def send_email_outlook_draft(report_content, subject=None, is_dream_team_format=False):
    """Create clean text Outlook email draft with Dream Team format"""
    try:
        load_dotenv()
        
        # Get email configuration
        email_user = os.getenv('EMAIL_USER')
        email_to = os.getenv('EMAIL_TO')
        
        if not all([email_user, email_to]):
            print("CROSS Email configuration incomplete. Check your .env file.")
            return False
        
        # Parse recipients
        recipients = email_to.replace(',', ';')  # Outlook uses semicolon
        
        # Set default subject
        if not subject:
            subject = f"Weekly Update - {datetime.now().strftime('%B %d, %Y')}"
        
        print(f"EMAIL Creating clean text Outlook draft...")
        print(f"   From: {email_user}")
        print(f"   To: {recipients}")
        print(f"   Subject: {subject}")
        
        # Create clean Dream Team email format
        if is_dream_team_format or "Dream Team" in str(report_content):
            # Use the Dream Team content as-is (already formatted)
            email_body = convert_html_to_text(report_content) if '<' in str(report_content) else str(report_content)
        else:
            # Convert report to clean Dream Team format
            clean_text = convert_html_to_text(report_content) if '<' in str(report_content) else str(report_content)
            
            # Create Dream Team email format
            email_body = f"""Dream Team,

Here is my weekly update:

{clean_text}

Best regards,
Akhil Reddy
HHA Medicine Technology Team"""
        
        # Create mailto URL for Outlook
        mailto_url = f"mailto:{recipients}?subject={quote(subject)}&body={quote(email_body)}"
        
        # Open Outlook with pre-filled email
        print("SEARCH Opening Outlook with email draft...")
        webbrowser.open(mailto_url)
        
        print("CHECK Outlook email draft created successfully!")
        print("WRENCH Please review the email in Outlook and click Send")
        print("BULB TIP: You can attach the HTML report file if needed")
        
        logger.info(f"Outlook draft created for recipients: {recipients}")
        return True
        
    except Exception as e:
        logger.error(f"Outlook draft creation error: {str(e)}")
        print(f"CROSS Outlook draft creation error: {str(e)}")
        return False

def convert_html_to_text(html_content):
    """Convert HTML report to plain text for email"""
    try:
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        import html
        text = html.unescape(text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Limit length for email body (Outlook has limits)
        if len(text) > 2000:
            text = text[:2000] + "\n\n[Content truncated - see full HTML report]"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"HTML to text conversion error: {str(e)}")
        return "Weekly report generated successfully. Please see HTML file for full content."

def test_outlook_draft():
    """Test the Outlook draft functionality"""
    print("EMAIL Testing Outlook Draft Method")
    print("=" * 35)
    
    test_html = """
    <h1>Weekly Report Test</h1>
    <h2>Completed Tasks</h2>
    <ul>
        <li>Set up AI voice-to-report system</li>
        <li>Configured OpenAI integration</li>
        <li>Created Outlook draft method</li>
    </ul>
    <h2>Next Week</h2>
    <p>Continue improving the automated reporting system.</p>
    """
    
    subject = "Test Email - Weekly Report AI System"
    
    if send_email_outlook_draft(test_html, subject):
        print("\nCHECK Outlook draft test successful!")
        print("CHECK Your system is ready to use with Outlook!")
    else:
        print("\nCROSS Outlook draft test failed")

if __name__ == "__main__":
    test_outlook_draft()