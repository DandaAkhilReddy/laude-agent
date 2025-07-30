# === File: merge_audio.py ===
import wave
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def merge_audio_clips(audio_files):
    """Merge multiple WAV audio files into a single file"""
    if not audio_files:
        logger.error("No audio files provided for merging")
        return None
    
    output_path = Path("final_audio.wav")
    
    try:
        print(f"WRENCH Merging {len(audio_files)} audio clips...")
        
        # Open the first file to get parameters
        with wave.open(audio_files[0], 'rb') as first_file:
            sample_rate = first_file.getframerate()
            channels = first_file.getnchannels()
            sample_width = first_file.getsampwidth()
        
        # Create output file
        with wave.open(str(output_path), 'wb') as output_file:
            output_file.setnchannels(channels)
            output_file.setsampwidth(sample_width)
            output_file.setframerate(sample_rate)
            
            total_frames = 0
            
            # Merge all files
            for i, audio_file in enumerate(audio_files, 1):
                try:
                    print(f"   CLIP Adding clip {i}/{len(audio_files)}: {Path(audio_file).name}")
                    
                    with wave.open(audio_file, 'rb') as input_file:
                        # Verify compatibility
                        if (input_file.getframerate() != sample_rate or 
                            input_file.getnchannels() != channels or 
                            input_file.getsampwidth() != sample_width):
                            
                            logger.warning(f"Audio parameters mismatch in {audio_file}")
                            print(f"   WARNING  Parameter mismatch in {Path(audio_file).name}")
                            continue
                        
                        # Copy audio data
                        frames = input_file.readframes(input_file.getnframes())
                        output_file.writeframes(frames)
                        total_frames += input_file.getnframes()
                
                except Exception as e:
                    logger.error(f"Error processing {audio_file}: {str(e)}")
                    print(f"   CROSS Error with {Path(audio_file).name}: {str(e)}")
                    continue
        
        if total_frames == 0:
            logger.error("No audio data was merged")
            print("CROSS No audio data was successfully merged")
            return None
        
        # Calculate total duration
        total_duration = total_frames / sample_rate
        file_size = output_path.stat().st_size / 1024  # KB
        
        print(f"CHECK Audio merged successfully!")
        print(f"   FOLDER Output: {output_path}")
        print(f"   ⏱️  Duration: {total_duration:.1f} seconds")
        print(f"   CHART Size: {file_size:.1f} KB")
        
        logger.info(f"Audio merge complete: {output_path} ({total_duration:.1f}s, {file_size:.1f}KB)")
        
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Audio merge failed: {str(e)}")
        print(f"CROSS Audio merge failed: {str(e)}")
        return None

def cleanup_temp_files(audio_files):
    """Clean up temporary audio clip files"""
    print("BROOM Cleaning up temporary audio files...")
    
    cleaned_count = 0
    for audio_file in audio_files:
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
                cleaned_count += 1
                print(f"   TRASH  Removed: {Path(audio_file).name}")
        except Exception as e:
            logger.warning(f"Failed to remove {audio_file}: {str(e)}")
            print(f"   WARNING  Could not remove: {Path(audio_file).name}")
    
    print(f"CHECK Cleaned up {cleaned_count}/{len(audio_files)} temporary files")
    logger.info(f"Cleaned up {cleaned_count} temporary audio files")

def convert_to_mp3(wav_file, output_name="final_audio.mp3"):
    """Convert WAV to MP3 using ffmpeg (if available)"""
    try:
        import subprocess
        
        output_path = Path(output_name)
        
        # Check if ffmpeg is available
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        
        print("MUSIC Converting to MP3...")
        
        # Convert WAV to MP3
        cmd = [
            'ffmpeg', '-i', wav_file, 
            '-acodec', 'mp3', 
            '-ab', '128k',
            '-y',  # Overwrite existing file
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"CHECK MP3 conversion complete: {output_path}")
            logger.info(f"WAV to MP3 conversion successful: {output_path}")
            return str(output_path)
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return wav_file  # Return original WAV file
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARNING  FFmpeg not found. Using WAV file for transcription.")
        logger.warning("FFmpeg not available, keeping WAV format")
        return wav_file
    except Exception as e:
        logger.error(f"MP3 conversion error: {str(e)}")
        return wav_file

def get_audio_info(audio_file):
    """Get information about an audio file"""
    try:
        with wave.open(audio_file, 'rb') as wf:
            frames = wf.getnframes()
            sample_rate = wf.getframerate()
            duration = frames / sample_rate
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'frames': frames
            }
    except Exception as e:
        logger.error(f"Error getting audio info for {audio_file}: {str(e)}")
        return None

if __name__ == "__main__":
    # Test mode
    logging.basicConfig(level=logging.INFO)
    
    print("WRENCH Audio Merge Test Mode")
    print("=" * 25)
    
    # Test with dummy files (for demonstration)
    test_files = ["audio_clips/clip_1.wav", "audio_clips/clip_2.wav"]
    
    print(f"Testing merge with: {test_files}")
    result = merge_audio_clips(test_files)
    
    if result:
        info = get_audio_info(result)
        if info:
            print(f"\nCHART Final audio info:")
            print(f"   Duration: {info['duration']:.1f} seconds")
            print(f"   Sample rate: {info['sample_rate']} Hz")
            print(f"   Channels: {info['channels']}")
            print(f"   Sample width: {info['sample_width']} bytes")
    else:
        print("CROSS Merge test failed")