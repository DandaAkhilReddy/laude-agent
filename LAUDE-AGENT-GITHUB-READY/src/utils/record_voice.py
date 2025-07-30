# === File: record_voice.py ===
import sounddevice as sd
import wave
import numpy as np
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def record_audio_clip(filename, sample_rate=44100):
    """Record a single audio clip until user presses Enter"""
    audio_dir = Path("audio_clips")
    audio_dir.mkdir(exist_ok=True)
    
    filepath = audio_dir / filename
    
    print(f"MICROPHONE Recording {filename}...")
    print("   Press ENTER to stop recording")
    
    # Start recording
    recording = []
    
    def audio_callback(indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        recording.extend(indata[:, 0])  # Mono recording
    
    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=audio_callback):
            input()  # Wait for user to press Enter
        
        if not recording:
            print("CROSS No audio recorded")
            return None
        
        # Convert to numpy array and save as WAV
        audio_data = np.array(recording, dtype=np.float32)
        
        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Convert to 16-bit integers
        audio_data_int = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV file
        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data_int.tobytes())
        
        duration = len(audio_data) / sample_rate
        print(f"CHECK Recorded {duration:.1f} seconds → {filepath}")
        logger.info(f"Recorded audio clip: {filepath} ({duration:.1f}s)")
        
        return str(filepath)
    
    except KeyboardInterrupt:
        print("\nWARNING  Recording cancelled")
        return None
    except Exception as e:
        print(f"CROSS Recording error: {str(e)}")
        logger.error(f"Recording error: {str(e)}")
        return None

def record_multiple_clips():
    """Record multiple audio clips with user confirmation"""
    print("MICROPHONE Multi-Clip Voice Recording")
    print("=" * 35)
    print("Instructions:")
    print("- Each recording starts when you see the prompt")
    print("- Press ENTER to stop each recording")
    print("- You'll be asked if you want to record more")
    print()
    
    audio_files = []
    clip_number = 1
    
    while True:
        print(f"\nCLAPPER Recording Clip {clip_number}")
        print("-" * 25)
        
        filename = f"clip_{clip_number}.wav"
        audio_file = record_audio_clip(filename)
        
        if audio_file:
            audio_files.append(audio_file)
            print(f"CHECK Clip {clip_number} saved successfully")
        else:
            print(f"CROSS Clip {clip_number} failed to record")
        
        # Ask if user wants to record another clip
        while True:
            response = input(f"\nTHINKING Record another clip? (Y/n): ").strip().lower()
            
            if response in ['', 'y', 'yes']:
                break
            elif response in ['n', 'no']:
                if audio_files:
                    print(f"\nPARTY Recording complete! Total clips: {len(audio_files)}")
                    logger.info(f"Recording session complete. Total clips: {len(audio_files)}")
                    return audio_files
                else:
                    print("WARNING  No clips recorded yet. Please record at least one clip.")
                    continue
            else:
                print("WARNING  Please enter 'Y' for yes or 'N' for no")
        
        clip_number += 1
    
    return audio_files

def test_microphone():
    """Test microphone functionality"""
    print("MICROPHONE Testing microphone...")
    
    try:
        # List available audio devices
        devices = sd.query_devices()
        print("\nPHONE Available audio devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"   {i}: {device['name']} (Input)")
        
        # Test recording for 3 seconds
        print("\nTEST Recording 3-second test...")
        sample_rate = 44100
        duration = 3
        
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        
        # Check if audio was recorded
        max_amplitude = np.max(np.abs(audio))
        
        if max_amplitude > 0.01:  # Threshold for detecting sound
            print(f"CHECK Microphone working! Max amplitude: {max_amplitude:.3f}")
            return True
        else:
            print(f"WARNING  Low audio detected. Max amplitude: {max_amplitude:.3f}")
            print("   Check microphone connection and permissions")
            return False
    
    except Exception as e:
        print(f"CROSS Microphone test failed: {str(e)}")
        logger.error(f"Microphone test error: {str(e)}")
        return False

if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.INFO)
    
    print("MICROPHONE Voice Recording Test Mode")
    print("=" * 30)
    
    if test_microphone():
        print("\nMICROPHONE  Starting multi-clip recording test...")
        files = record_multiple_clips()
        print(f"\nFOLDER Recorded files: {files}")
    else:
        print("CROSS Microphone test failed. Fix audio issues before proceeding.")