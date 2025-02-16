import os
import time
import asyncio
import aiohttp
import aiofiles
import openai
import logging
from pathlib import Path
import subprocess
from datetime import datetime
from config import API_KEY, API_BASE

# Configuration
CONFIG = {
    'API_KEY': API_KEY,
    'API_BASE': API_BASE,
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = CONFIG['API_KEY']
openai.api_base = CONFIG['API_BASE']

async def transcribe_audio(session, file_path):
    """Transcribe audio file using OpenAI API."""
    try:
        logger.info(f"Starting transcription of {file_path.name}")
        
        form_data = aiohttp.FormData()
        form_data.add_field('file', 
                           open(file_path, 'rb'),
                           filename=file_path.name,
                           content_type='audio/mpeg')
        form_data.add_field('model', 'whisper-1')
        
        async with session.post(
            f"{CONFIG['API_BASE']}/audio/transcriptions",
            data=form_data,
            headers={'Authorization': f'Bearer {CONFIG["API_KEY"]}'}
        ) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"Successfully transcribed {file_path.name}")
                return file_path, result.get('text', '')
            else:
                error_text = await response.text()
                logger.error(f"API error for {file_path.name}: {error_text}")
                return file_path, None
                
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {str(e)}")
        return file_path, None

async def save_transcript(transcript, output_path):
    """Save transcript to a text file."""
    try:
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(transcript)
        logger.info(f"Transcript saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving transcript: {str(e)}")
        return False

async def process_and_save(session, mp3_file, splitted_dir):
    """Process single file and save its transcript."""
    file_path, transcript = await transcribe_audio(session, mp3_file)
    if transcript:
        output_file = splitted_dir / f"{file_path.stem}.txt"
        if await save_transcript(transcript, output_file):
            return file_path.stem, transcript
    return None, None

async def main():
    # Get current script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Define directories using relative paths
    input_dir = script_dir / "podcast" / "splitted-podcast"
    splitted_dir = script_dir / "transcript" / "splitted"
    transcript_dir = script_dir / "transcript" / "transcript"
    
    # Create directories if they don't exist
    splitted_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    
    # Find MP3 files
    mp3_files = list(input_dir.glob("*.mp3"))
    if not mp3_files:
        logger.error(f"No MP3 files found in {input_dir}")
        return
    
    logger.info(f"Found {len(mp3_files)} MP3 files to process")
    
    # Process all files concurrently
    async with aiohttp.ClientSession() as session:
        # Create tasks for all files
        tasks = [
            process_and_save(session, mp3_file, splitted_dir)
            for mp3_file in mp3_files
        ]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Filter out failed transcriptions
        successful_results = [(name, transcript) for name, transcript in results if name and transcript]
        
    # Create combined transcript if we have any successful transcriptions
    if successful_results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_content = "\n\n" + "\n\n".join(
        #combined_content = "\n\n" + "="*50 + "\n\n".join(
            #f"File: {filename}\n{transcript}" 
            f"\n{transcript}" 
            for filename, transcript in successful_results
        )
        
        combined_file = transcript_dir / f"transcript_{timestamp}.txt"
        
        if await save_transcript(combined_content, combined_file):
            logger.info(f"Created combined transcript: {combined_file}")
            try:
                subprocess.Popen(['notepad.exe', str(combined_file)])
                logger.info("Opened combined transcript in Notepad")
            except Exception as e:
                logger.error(f"Failed to open Notepad: {str(e)}")
                
        logger.info(f"Successfully processed {len(successful_results)} out of {len(mp3_files)} files")
    else:
        logger.warning("No successful transcriptions to combine")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        logger.info("Program terminated")
