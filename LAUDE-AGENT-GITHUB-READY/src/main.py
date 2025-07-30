# === File: main.py ===
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

from record_voice import record_multiple_clips
from merge_audio import merge_audio_clips
from transcribe_audio import transcribe_audio
from generate_report import generate_report
from generate_dream_team_email import generate_dream_team_email, save_dream_team_email
from send_email_outlook import send_email_outlook_draft

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
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

def main():
    """Main application workflow"""
    logger = setup_logging()
    setup_directories()
    
    print("MICROPHONE  Welcome to Laude - Your AI Voice Assistant")
    print("=" * 55)
    
    try:
        # Step 1: Record multiple audio clips
        logger.info("Starting audio recording phase")
        print("\nCLAPPER STEP 1: Recording Audio Clips")
        audio_files = record_multiple_clips()
        
        if not audio_files:
            print("CROSS No audio clips recorded. Exiting.")
            return
        
        # Step 2: Merge audio clips
        logger.info("Merging audio clips")
        print("\nWRENCH STEP 2: Merging Audio Clips")
        final_audio_path = merge_audio_clips(audio_files)
        
        # Step 3: Transcribe audio
        logger.info("Transcribing audio")
        print("\nPENCIL STEP 3: Transcribing Audio")
        transcript = transcribe_audio(final_audio_path)
        
        if not transcript:
            print("CROSS Failed to transcribe audio. Exiting.")
            return
        
        # Save transcript
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        transcript_path = Path("transcripts") / f"transcript_{timestamp}.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        print(f"CHECK Transcript saved: {transcript_path}")
        
        # Step 4: Generate clean Dream Team email
        logger.info("Generating Dream Team email")
        print("\nROBOT STEP 4: Generating Dream Team Email")
        dream_team_email = generate_dream_team_email(transcript)
        
        if not dream_team_email:
            print("CROSS Failed to generate Dream Team email. Exiting.")
            return
        
        # Save Dream Team email
        email_filename = save_dream_team_email(dream_team_email)
        
        # Step 5: Show clean email preview
        print("\nEYES STEP 5: Dream Team Email Preview")
        print("=" * 50)
        print(dream_team_email)
        print("=" * 50)
        
        print("\nEMAIL STEP 6: Auto-Send to Outlook")
        print("=" * 30)
        
        # Automatically send the clean email
        logger.info("Auto-sending Dream Team email")
        print("\nSEND Creating Outlook draft...")
        
        if send_email_outlook_draft(dream_team_email, f"Weekly Update - {datetime.now().strftime('%B %d, %Y')}", is_dream_team_format=True):
            print("CHECK Clean Dream Team email created in Outlook!")
            print("WRENCH Email is ready to send - check your Outlook")
            logger.info("Dream Team email draft created successfully")
        else:
            print("CROSS Failed to create email draft. Check logs for details.")
            logger.error("Failed to create email draft")
        
        print("\nPARTY Laude has completed your Dream Team email!")
        print(f"FOLDER Files saved in: {Path.cwd()}")
        
    except KeyboardInterrupt:
        print("\n\nWARNING Process interrupted by user")
        logger.info("Process interrupted by user")
    except Exception as e:
        print(f"\nCROSS Error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()