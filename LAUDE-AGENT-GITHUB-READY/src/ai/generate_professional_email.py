#!/usr/bin/env python3
"""Generate professional weekly update email from report content"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
import openai
import logging

logger = logging.getLogger(__name__)

def generate_professional_email(transcript_text, user_name="User", user_company="Company", user_department="Team"):
    """Generate a professional weekly update email with numbered bullet points for any user"""
    try:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("CROSS OpenAI API key not found in .env file")
            return None
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        print("ROBOT Generating professional weekly update email...")
        
        # Universal prompt template that works for anyone
        system_message = f"""You are a professional email writing assistant that converts voice transcripts into polished weekly update emails.

Your task: Transform casual spoken updates into professional, well-structured business emails.

EXACT EMAIL FORMAT:
Good morning,

Here is my weekly update:

1. [First accomplishment with specific metrics/results/impact]
2. [Second project with measurable outcomes/progress]
3. [Third achievement with concrete data/improvements]
4. [Fourth task with quantifiable results/benefits]
5. [Fifth milestone with performance indicators/metrics]
6. [Next week's key priorities and planned objectives]

Key metrics: [Extract and highlight specific numbers, percentages, achievements, improvements]

Best regards,
{user_name}
{user_department} • {user_company}

UNIVERSAL FORMATTING RULES:
- Always use numbered bullet points (1, 2, 3, 4, 5, 6)
- Extract and include specific metrics, numbers, percentages when mentioned
- Keep each point concise but informative (1-2 lines maximum)
- Use professional business terminology appropriate to the context
- Focus on accomplishments, results, and measurable impact
- Automatically extract key metrics for the summary line
- Rephrase and improve clarity while maintaining original meaning
- Use clean plain text only - NO HTML or special formatting
- Make the language polished and professional regardless of how casual the input
- If transcript is unclear or repetitive, intelligently structure the content"""

        user_message = f"""TRANSFORM this voice transcript into a polished professional email.
        
The speaker works in: {user_department} at {user_company}
Their voice transcript below may be casual, rambling, or contain filler words.
Your job: Create a clean, professional weekly update email that captures their accomplishments.

TRANSCRIPT:
{transcript_text}

INSTRUCTIONS:
1. Identify key accomplishments, projects, and results from the transcript
2. Rephrase everything in professional business language
3. Structure into exactly 6 numbered points (combine or split content as needed)
4. Extract any numbers, metrics, or measurable results mentioned
5. Create a compelling "Key metrics" summary line
6. Make point #6 about next week's priorities/goals
7. Ensure the email sounds professional regardless of how casual the input was

Remember: Transform their casual speech into polished professional communication."""

        # Generate the email content
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=800,
            temperature=0.1  # Low temperature for consistency
        )
        
        email_content = response.choices[0].message.content.strip()
        
        # Clean up the response and ensure proper format
        email_content = email_content.strip()
        
        # Ensure it starts with professional greeting
        if not email_content.startswith("Good morning"):
            email_content = f"Good morning,\n\nHere is my weekly update:\n\n{email_content}"
        
        # Ensure it ends with proper signature
        signature = f"\n\nBest regards,\n{user_name}\n{user_department} • {user_company}"
        if not email_content.endswith(signature.strip()):
            # Remove any existing signature and add the correct one
            lines = email_content.split('\n')
            # Find where signature might start
            sig_start = -1
            for i, line in enumerate(lines):
                if 'Best regards' in line or 'Sincerely' in line or 'Thanks' in line:
                    sig_start = i
                    break
            
            if sig_start >= 0:
                # Replace existing signature
                email_content = '\n'.join(lines[:sig_start]) + signature
            else:
                # Add signature
                email_content += signature
        
        print("CHECK Professional email generated successfully!")
        return email_content
        
    except Exception as e:
        logger.error(f"Professional email generation error: {str(e)}")
        print(f"CROSS Error generating professional email: {str(e)}")
        return None

def save_professional_email(email_content):
    """Save the professional email to a text file"""
    try:
        # Create emails directory if it doesn't exist
        os.makedirs("emails", exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emails/professional_email_{timestamp}.txt"
        
        # Save the clean text email
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        print(f"DISK Professional email saved: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving professional email: {str(e)}")
        print(f"CROSS Error saving email: {str(e)}")
        return None

def test_professional_generation():
    """Test the professional email generation"""
    print("EMAIL Testing Professional Email Generation")
    print("=" * 40)
    
    test_transcript = """
    This week at HHS Medicine I completed the patient management system upgrade 
    which resulted in 99.7% uptime and improved response times by 45%. 
    I also worked on implementing the new security protocols ensuring full HIPAA compliance
    and zero security incidents. We successfully deployed the telemedicine platform upgrade
    supporting 300% more concurrent video calls. I trained 25 staff members on the new 
    patient portal features. Next week I'm planning to focus on the mobile app launch
    and integration testing. Key metrics this week: 99.7% uptime, 45% performance improvement,
    25 staff trained, zero incidents.
    """
    
    email_content = generate_professional_email(test_transcript, "Akhil Reddy", "HSS Medicine", "Technology Team")
    
    if email_content:
        print("\nCHECK Generated Professional Email:")
        print("-" * 40)
        print(email_content)
        print("-" * 40)
        
        # Save the email
        filename = save_professional_email(email_content)
        
        if filename:
            print(f"\nCHECK Email saved successfully: {filename}")
            print("CHECK Professional email generation test passed!")
        else:
            print("\nCROSS Failed to save email")
    else:
        print("\nCROSS Professional email generation failed")

if __name__ == "__main__":
    test_professional_generation()