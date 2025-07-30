# === File: transcribe_audio.py ===
import openai
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def transcribe_audio(audio_file_path):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            print(f"CROSS Audio file not found: {audio_file_path}")
            return None
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not found in environment variables")
            print("CROSS OpenAI API key not found. Please check your .env file.")
            return None
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Get file info
        file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # MB
        print(f"OUTBOX Uploading audio file ({file_size:.1f} MB)...")
        
        # Transcribe audio
        with open(audio_file_path, 'rb') as audio_file:
            print("ROBOT Transcribing with OpenAI Whisper...")
            
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        if transcript:
            word_count = len(transcript.split())
            print(f"CHECK Transcription complete!")
            print(f"   PENCIL Word count: {word_count}")
            print(f"   PAGE Preview: {transcript[:100]}...")
            
            logger.info(f"Transcription successful: {word_count} words")
            return transcript
        else:
            logger.error("Empty transcription received")
            print("CROSS Empty transcription received")
            return None
    
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        print(f"CROSS OpenAI API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        print(f"CROSS Transcription error: {str(e)}")
        return None

def transcribe_with_timestamps(audio_file_path):
    """Transcribe audio with timestamp information"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        client = openai.OpenAI(api_key=api_key)
        
        with open(audio_file_path, 'rb') as audio_file:
            print("ROBOT Transcribing with timestamps...")
            
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return transcript
    
    except Exception as e:
        logger.error(f"Timestamp transcription error: {str(e)}")
        return None

def format_transcript_with_sections(transcript):
    """Format transcript into logical sections"""
    if not transcript:
        return transcript
    
    # Simple section detection based on common phrases
    section_markers = [
        "this week", "last week", "next week",
        "monday", "tuesday", "wednesday", "thursday", "friday",
        "project", "task", "meeting", "issue", "problem",
        "completed", "finished", "done", "working on",
        "goal", "objective", "target", "deadline"
    ]
    
    sentences = transcript.split('. ')
    formatted_sections = []
    current_section = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Check if sentence contains section markers
        contains_marker = any(marker in sentence.lower() for marker in section_markers)
        
        if contains_marker and current_section:
            # Start new section
            formatted_sections.append('. '.join(current_section) + '.')
            current_section = [sentence]
        else:
            current_section.append(sentence)
    
    # Add remaining section
    if current_section:
        formatted_sections.append('. '.join(current_section) + '.')
    
    return '\n\n'.join(formatted_sections)

def validate_transcript(transcript):
    """Validate transcript quality and content"""
    if not transcript:
        return False, "Empty transcript"
    
    word_count = len(transcript.split())
    
    # Check minimum word count
    if word_count < 10:
        return False, f"Transcript too short ({word_count} words)"
    
    # Check for repetitive content (possible transcription error)
    words = transcript.lower().split()
    unique_words = set(words)
    uniqueness_ratio = len(unique_words) / len(words)
    
    if uniqueness_ratio < 0.3:
        return False, "Transcript appears repetitive (possible audio issue)"
    
    # Check for common transcription artifacts
    artifacts = ["[inaudible]", "[unclear]", "***", "...", "???"]
    artifact_count = sum(transcript.lower().count(artifact) for artifact in artifacts)
    
    if artifact_count > word_count * 0.1:
        return False, "Too many transcription artifacts detected"
    
    return True, "Transcript validation passed"

def save_transcript_segments(transcript_data, output_dir="transcripts"):
    """Save transcript with segment information"""
    try:
        Path(output_dir).mkdir(exist_ok=True)
        
        if hasattr(transcript_data, 'segments'):
            timestamp = Path().name
            segments_file = Path(output_dir) / f"segments_{timestamp}.txt"
            
            with open(segments_file, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(transcript_data.segments):
                    start_time = segment.get('start', 0)
                    end_time = segment.get('end', 0)
                    text = segment.get('text', '')
                    
                    f.write(f"[{start_time:.1f}s - {end_time:.1f}s] {text}\n")
            
            print(f"CHECK Segments saved: {segments_file}")
            return str(segments_file)
    
    except Exception as e:
        logger.error(f"Error saving segments: {str(e)}")
    
    return None

if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.INFO)
    
    print("ROBOT Audio Transcription Test Mode")
    print("=" * 35)
    
    # Test file path
    test_file = "final_audio.wav"
    
    if os.path.exists(test_file):
        print(f"FOLDER Testing with: {test_file}")
        
        # Test basic transcription
        result = transcribe_audio(test_file)
        
        if result:
            # Validate transcript
            is_valid, message = validate_transcript(result)
            print(f"CHECK Validation: {message}")
            
            # Format transcript
            formatted = format_transcript_with_sections(result)
            print(f"\nPENCIL Formatted transcript preview:")
            print("-" * 40)
            print(formatted[:300] + "..." if len(formatted) > 300 else formatted)
        
    else:
        print(f"CROSS Test file not found: {test_file}")
        print("   Create an audio file first using record_voice.py and merge_audio.py")