# === File: generate_report.py ===
import openai
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def load_report_template():
    """Load the report prompt template"""
    template_path = Path("templates") / "report_prompt.txt"
    
    try:
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            logger.info("Report template loaded successfully")
            return template
        else:
            # Use default template if file doesn't exist
            logger.warning("Report template file not found, using default")
            return get_default_template()
    
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        return get_default_template()

def get_default_template():
    """Default report template if file is not found"""
    return """You are a professional assistant that converts voice transcripts into well-formatted weekly reports.

TRANSCRIPT TO PROCESS:
{transcript}

Please create a comprehensive weekly report with the following structure:

# Weekly Report - {date}

## 📋 Executive Summary
[Brief overview of the week's main accomplishments and focus areas]

## CHECK Completed Tasks
[List of tasks, projects, or activities completed this week]

## 🔄 In Progress
[Current ongoing projects and their status]

## 📅 Upcoming Priorities
[Tasks and goals for next week]

## 🚧 Challenges & Blockers
[Any issues encountered and how they were addressed]

## CHART Key Metrics & Results
[Quantifiable achievements, numbers, results]

## BULB Notes & Insights
[Additional observations, learnings, or important points]

Format the report as clean HTML with professional styling. Use proper headings, bullet points, and emphasis where appropriate. Make it suitable for email delivery to management."""

def generate_report(transcript):
    """Generate a professional report from transcript using GPT-4"""
    try:
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not found")
            print("CROSS OpenAI API key not found. Please check your .env file.")
            return None
        
        # Load template
        template = load_report_template()
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Format the prompt
        prompt = template.format(transcript=transcript, date=current_date)
        
        print("ROBOT Generating report with GPT-4...")
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Generate report with enhanced system training
        system_message = """You are a specialized AI assistant for HHA Medicine healthcare technology team. You create standardized weekly reports with EXACT consistency.

CRITICAL BEHAVIORAL RULES:
1. ALWAYS follow the template structure precisely - never deviate
2. Use IDENTICAL section headings every time
3. Maintain professional healthcare IT terminology consistently
4. Include specific metrics and measurable outcomes
5. Always relate work back to patient care impact
6. Use the same formatting style and HTML structure each time
7. Keep the tone authoritative but accessible to healthcare executives
8. Never skip sections - if information is missing, note "No updates this week"
9. Always quantify achievements with numbers and percentages when possible
10. Maintain consistent bullet point and numbering styles

You are creating reports for healthcare executives who need consistent, predictable formatting to quickly scan and understand technology team progress."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.1  # Lower temperature for more consistent output
        )
        
        if response.choices and response.choices[0].message:
            report_content = response.choices[0].message.content
            
            # Wrap in HTML structure if not already HTML
            if not report_content.strip().startswith('<'):
                report_html = format_as_html(report_content, current_date)
            else:
                report_html = report_content
            
            print("CHECK Report generated successfully!")
            
            # Log token usage
            if hasattr(response, 'usage'):
                print(f"   NUMBERS Tokens used: {response.usage.total_tokens}")
                logger.info(f"GPT-4 tokens used: {response.usage.total_tokens}")
            
            logger.info("Report generation completed")
            return report_html
        
        else:
            logger.error("Empty response from GPT-4")
            print("CROSS Empty response from GPT-4")
            return None
    
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        print(f"CROSS OpenAI API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        print(f"CROSS Report generation error: {str(e)}")
        return None

def format_as_html(content, date):
    """Format plain text content as professional HTML"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Report - HHA Medicine - {date}</title>
    <style>
        body {{
            font-family: 'Calibri', 'Segoe UI', sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        .container {{
            background-color: #ffffff;
            border: 2px solid #1f4e79;
            padding: 40px;
            border-radius: 0;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #1f4e79;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #1f4e79;
            font-size: 28px;
            font-weight: bold;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        h2 {{
            color: #1f4e79;
            font-size: 18px;
            margin: 0;
            font-weight: normal;
        }}
        h3 {{
            color: #1f4e79;
            font-size: 16px;
            font-weight: bold;
            margin-top: 25px;
            margin-bottom: 12px;
            padding-bottom: 5px;
            border-bottom: 1px solid #bdc3c7;
            text-transform: uppercase;
        }}
        ul {{
            padding-left: 20px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        ol {{
            padding-left: 20px;
            margin-bottom: 20px;
        }}
        ol li {{
            margin-bottom: 8px;
            font-weight: 500;
        }}
        strong {{
            color: #1f4e79;
            font-weight: bold;
        }}
        .metrics-section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-left: 5px solid #1f4e79;
            margin: 20px 0;
        }}
        .summary-section {{
            background-color: #e8f4fd;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #1f4e79;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
        .company-logo {{
            color: #1f4e79;
            font-weight: bold;
            font-size: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #1f4e79;
            color: white;
            font-weight: bold;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 10px; }}
            .container {{ padding: 20px; }}
            h1 {{ font-size: 24px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>HHA Medicine Technology Team</h1>
            <h2>Weekly Report - {date}</h2>
        </div>
        {content}
        <div class="footer">
            <div class="company-logo">HHA MEDICINE</div>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d at %I:%M %p')} | AI-Powered Reporting System</p>
            <p>Confidential - For Internal Use Only</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_template

def enhance_report_content(content):
    """Enhance report content with better formatting and structure"""
    
    # Add emoji prefixes to common sections
    emoji_mappings = {
        'Executive Summary': '📋',
        'Completed Tasks': 'CHECK',
        'In Progress': '🔄',
        'Upcoming Priorities': '📅',
        'Challenges': '🚧',
        'Blockers': '🚧',
        'Key Metrics': 'CHART',
        'Results': 'CHART',
        'Notes': 'BULB',
        'Insights': 'BULB'
    }
    
    enhanced_content = content
    
    for section, emoji in emoji_mappings.items():
        # Add emoji to section headers
        enhanced_content = enhanced_content.replace(
            f"## {section}",
            f"## {emoji} {section}"
        )
        enhanced_content = enhanced_content.replace(
            f"# {section}",
            f"# {emoji} {section}"
        )
    
    return enhanced_content

def validate_report(report_html):
    """Validate the generated report"""
    if not report_html:
        return False, "Empty report"
    
    # Check minimum length
    if len(report_html.strip()) < 200:
        return False, "Report too short"
    
    # Check for key sections
    required_sections = ['summary', 'completed', 'progress', 'upcoming']
    found_sections = sum(1 for section in required_sections 
                        if section.lower() in report_html.lower())
    
    if found_sections < 2:
        return False, "Missing key report sections"
    
    # Check HTML structure (if HTML format)
    if '<html>' in report_html.lower():
        if not all(tag in report_html.lower() for tag in ['<body>', '</body>', '<head>', '</head>']):
            return False, "Incomplete HTML structure"
    
    return True, "Report validation passed"

if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.INFO)
    
    print("ROBOT Report Generation Test Mode")
    print("=" * 35)
    
    # Test with sample transcript
    sample_transcript = """
    This week I worked on three main projects. First, I completed the user authentication system 
    for the web application. This involved implementing OAuth integration and password reset functionality. 
    I also fixed several bugs in the payment processing module. 
    
    For next week, I plan to work on the reporting dashboard and start the mobile app development. 
    I had some challenges with the database migration but resolved them by working with the DevOps team.
    
    Key metrics: reduced login time by 30%, fixed 8 critical bugs, deployed 3 new features to production.
    """
    
    print("PENCIL Testing with sample transcript...")
    result = generate_report(sample_transcript)
    
    if result:
        # Validate report
        is_valid, message = validate_report(result)
        print(f"CHECK Validation: {message}")
        
        # Show preview
        print(f"\nPAGE Report preview:")
        print("-" * 50)
        preview = result[:500] + "..." if len(result) > 500 else result
        print(preview)
        
        # Save test report
        test_path = Path("test_report.html")
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\nSAVE Test report saved: {test_path}")
    
    else:
        print("CROSS Report generation test failed")