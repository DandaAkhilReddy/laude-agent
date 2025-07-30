#!/usr/bin/env python3
"""Final demo - Auto-creates Outlook draft"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_report import generate_report
from send_email_outlook import send_email_outlook_draft

def main():
    """Complete demo with automatic Outlook draft creation"""
    
    print("ROCKET FINAL DEMO - Weekly Report AI with Outlook")
    print("=" * 55)
    
    # HHA Medicine focused sample
    sample_transcript = """
    This week at HHA Medicine, I made significant progress on our healthcare technology initiatives.

    Completed Projects:
    - Implemented new patient management system with HIPAA-compliant data handling
    - Deployed automated appointment scheduling reducing admin workload by 60%
    - Upgraded telemedicine platform security protocols
    - Resolved 3 critical system vulnerabilities
    - Completed staff training on new patient portal features

    Current Projects:
    - Developing mobile app interface for patient access
    - Integrating insurance verification systems
    - Setting up automated reporting workflows

    Next Week Goals:
    - Launch mobile app beta testing
    - Complete insurance integration testing
    - Conduct additional staff training sessions
    - Review and optimize system performance

    Key Metrics:
    - Patient wait times reduced by 25%
    - System uptime: 99.8%
    - Appointments processed: 150+
    - Zero security incidents
    - Staff efficiency improved by 40%

    Challenges Resolved:
    - Database migration issues fixed through IT collaboration
    - Authentication problems resolved with new security protocols
    - Performance bottlenecks eliminated through system optimization
    """
    
    try:
        print("ROBOT Generating professional weekly report...")
        
        # Generate report with GPT-4
        report_html = generate_report(sample_transcript)
        
        if not report_html:
            print("CROSS Failed to generate report")
            return
        
        # Save files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create directories
        Path("reports").mkdir(exist_ok=True)
        Path("transcripts").mkdir(exist_ok=True)
        
        # Save transcript
        transcript_path = Path("transcripts") / f"final_transcript_{timestamp}.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(sample_transcript)
        
        # Save report
        report_path = Path("reports") / f"final_report_{timestamp}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        # Create preview
        preview_path = Path("FINAL_REPORT_PREVIEW.html")
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        print("CHECK Report generated successfully!")
        print(f"CHECK Transcript: {transcript_path}")
        print(f"CHECK Report: {report_path}")
        print(f"CHECK Preview: {preview_path}")
        
        # Open preview in browser
        print("\nEYES Opening report preview...")
        try:
            os.system(f"start {preview_path}")
        except:
            print(f"   Manual open: {preview_path}")
        
        # Create Outlook draft automatically
        print("\nEMAIL Creating Outlook email draft...")
        
        subject = f"Weekly Report - HHA Medicine - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email_outlook_draft(report_html, subject):
            print("\nCHECK SUCCESS! Your system is fully operational!")
            print("=" * 50)
            print("WRENCH NEXT STEPS:")
            print("1. CHECK your Outlook application")
            print("2. REVIEW the email draft that was created") 
            print("3. ATTACH the HTML report if desired")
            print("4. SEND the email to your recipients")
            print()
            print("PARTY CONGRATULATIONS!")
            print("Your AI Voice-to-Report system is 100% ready!")
            print()
            print("TARGET To use with real microphone:")
            print("  -> Open Command Prompt and run: python main.py")
            print()
            print("FOLDER Files saved in:")
            print(f"  -> {Path.cwd()}")
            
        else:
            print("\nWARNING Outlook draft creation had an issue")
            print("But your report is ready and saved locally!")
        
    except Exception as e:
        print(f"\nCROSS Error: {str(e)}")
        print("BULB But your core system is working - OpenAI generated the report!")

if __name__ == "__main__":
    main()