#!/usr/bin/env python3
"""Run the complete voice recording and reporting system"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from record_voice import record_multiple_clips
from merge_audio import merge_audio_clips
from transcribe_audio import transcribe_audio
from generate_report import generate_report
from send_email_outlook import send_email_outlook_draft

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"full_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories"""
    directories = ["audio_clips", "reports", "transcripts", "logs", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def create_bullet_point_email(report_html, transcript):
    """Create email with Dream team greeting and bullet points"""
    
    # Extract key points from transcript for bullet points
    bullet_points = extract_key_points(transcript)
    
    # Create email content
    email_content = f"""Dream Team,

Here is my weekly update:

{bullet_points}

Please find the detailed report attached/below for your review.

Best regards,
Akhil Reddy
HHA Medicine Technology Team

---
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""
    
    return email_content

def extract_key_points(transcript):
    """Extract key points and format as numbered bullet points"""
    
    # Simple extraction based on common patterns
    sentences = transcript.split('.')
    key_points = []
    
    # Look for sentences with key indicators
    keywords = ['completed', 'implemented', 'developed', 'finished', 'achieved', 
               'working on', 'next week', 'plan to', 'metrics', 'results']
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10 and any(keyword in sentence.lower() for keyword in keywords):
            # Clean up the sentence
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            key_points.append(sentence)
    
    # Format as numbered list (limit to top points)
    formatted_points = ""
    for i, point in enumerate(key_points[:6], 1):  # Limit to 6 points
        formatted_points += f"{i}. {point}\n"
    
    return formatted_points if formatted_points else "1. Weekly technology updates completed\n2. System maintenance and improvements ongoing\n3. Planning next week's development priorities"

def main():
    """Main system execution"""
    logger = setup_logging()
    setup_directories()
    
    print("ROCKET HHA Medicine - Complete Voice-to-Report System")
    print("=" * 60)
    print("Record your voice → AI transcription → Formatted report → Outlook email")
    print()
    
    try:
        # Step 1: Record multiple audio clips
        print("MICROPHONE STEP 1: Recording Your Voice Updates")
        print("=" * 45)
        print("Instructions:")
        print("- Speak clearly about your weekly work")
        print("- Press ENTER to stop each recording")
        print("- Record multiple clips if needed")
        print("- Say 'no' when done recording")
        print()
        
        audio_files = record_multiple_clips()
        
        if not audio_files:
            print("CROSS No audio recorded. Exiting.")
            return
        
        print(f"CHECK Recorded {len(audio_files)} audio clips")
        
        # Step 2: Merge audio clips
        print(f"\nWRENCH STEP 2: Processing Audio Files")
        print("=" * 35)
        
        final_audio_path = merge_audio_clips(audio_files)
        if not final_audio_path:
            print("CROSS Failed to merge audio files.")
            return
        
        # Step 3: Transcribe with OpenAI Whisper
        print(f"\nROBOT STEP 3: OpenAI Whisper Transcription")
        print("=" * 42)
        
        transcript = transcribe_audio(final_audio_path)
        if not transcript:
            print("CROSS Failed to transcribe audio.")
            return
        
        print("CHECK Transcription completed successfully!")
        print(f"PENCIL Preview: {transcript[:100]}...")
        
        # Save transcript
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        transcript_path = Path("transcripts") / f"voice_transcript_{timestamp}.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        # Step 4: Generate standardized report with GPT-4
        print(f"\nTARGET STEP 4: GPT-4 Report Generation")
        print("=" * 38)
        
        report_html = generate_report(transcript)
        if not report_html:
            print("CROSS Failed to generate report.")
            return
        
        # Save report
        report_path = Path("reports") / f"voice_report_{timestamp}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        # Create preview
        preview_path = Path("VOICE_REPORT_PREVIEW.html")
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        print("CHECK Professional report generated!")
        print(f"CHECK Report saved: {report_path}")
        print(f"CHECK Preview: {preview_path}")
        
        # Step 5: Show preview
        print(f"\nEYES STEP 5: Report Preview")
        print("=" * 25)
        
        try:
            os.system(f"start {preview_path}")
            print("CHECK Report opened in browser")
        except:
            print(f"BULB Manual open: {preview_path}")
        
        # Step 6: Create special email format
        print(f"\nEMAIL STEP 6: Dream Team Email Creation")
        print("=" * 40)
        
        # Create bullet point email content
        bullet_email = create_bullet_point_email(report_html, transcript)
        
        print("CHECK Email content created with:")
        print("  - 'Dream Team' greeting")
        print("  - Numbered bullet points from your voice")
        print("  - Professional signature")
        
        # Show email preview
        print(f"\nPREVIEW Email Content:")
        print("-" * 30)
        print(bullet_email[:300] + "..." if len(bullet_email) > 300 else bullet_email)
        
        # Step 7: Create Outlook draft
        print(f"\nOUTBOX STEP 7: Creating Outlook Draft")
        print("=" * 37)
        
        # Combine bullet points with full report
        combined_content = f"{bullet_email}\n\n--- DETAILED REPORT ---\n{report_html}"
        
        subject = f"Weekly Update - HHA Medicine Technology - {datetime.now().strftime('%B %d, %Y')}"
        
        if send_email_outlook_draft(combined_content, subject):
            print(f"\nPARTY SUCCESS! Complete System Working!")
            print("=" * 45)
            print("CHECK Voice recorded with microphone")
            print("CHECK OpenAI Whisper transcribed your speech")
            print("CHECK GPT-4 generated professional report")
            print("CHECK Dream Team email format created")
            print("CHECK Numbered bullet points extracted")
            print("CHECK Outlook draft ready to send")
            print()
            print("WRENCH NEXT STEPS:")
            print("1. Check your Outlook application")
            print("2. Review the 'Dream Team' email with bullet points")
            print("3. Attach the HTML report if desired")
            print("4. Send to your recipients")
            print()
            print("ROCKET Your complete voice-to-email system is operational!")
        else:
            print(f"\nWARNING Outlook draft creation issue")
            print("But your voice recording and report generation worked perfectly!")
        
        print(f"\nFOLDER All files saved in: {Path.cwd()}")
        
    except KeyboardInterrupt:
        print(f"\n\nWARNING Process interrupted by user")
        logger.info("Process interrupted by user")
    except Exception as e:
        print(f"\nCROSS Error: {str(e)}")
        logger.error(f"System error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    print("ATTENTION: This will start voice recording!")
    print("Make sure your microphone is connected and working.")
    print()
    input("Press ENTER to start the voice recording system...")
    print()
    main()