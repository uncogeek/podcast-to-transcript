import asyncio
import logging
from pathlib import Path
import subprocess
import aiohttp
from datetime import datetime
import shutil
import os
import webbrowser
from ftphandler import upload_file
import requests
from tqdm import tqdm
from splitter import process_directory, setup_logging
from transcript import main as transcript_main
from config import SUMMARY_API_URL, FTP_HOST, FTP_USER, FTP_PASSWORD, FTP_DIRECTORY, SUMMARY_UPLOADED_TEXT_FILE

# Configuration
CONFIG = {
    'SUMMARY_API_URL': SUMMARY_API_URL,
}

async def send_to_summary_api(transcript_content):
    """Send transcript to summary API and get response."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                CONFIG['SUMMARY_API_URL'],
                json={'text': transcript_content},
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'response' in result:
                        return result['response']
                    elif 'error' in result:
                        logging.error(f"API error: {result['error']}")
                        return None
                    return None
                else:
                    error_text = await response.text()
                    logging.error(f"API error: {error_text}")
                    return None
    except Exception as e:
        logging.error(f"Error sending to summary API: {str(e)}")
        return None

def get_latest_transcript():
    """Get the most recent transcript file content."""
    try:
        script_dir = Path(__file__).parent.resolve()
        transcript_dir = script_dir / "transcript" / "transcript"
        
        # Get all transcript files
        transcript_files = list(transcript_dir.glob("transcript_*.txt"))
        
        if not transcript_files:
            logging.error("No transcript files found")
            return None
        
        # Get the latest file
        latest_file = max(transcript_files, key=lambda x: x.stat().st_mtime)
        
        # Read content
        with open(latest_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading latest transcript: {str(e)}")
        return None

async def save_summary(summary_text):
    """Save summary to a file and open it."""
    try:
        script_dir = Path(__file__).parent.resolve()
        summary_file = script_dir / "transcript" / "summary" / "summary.txt"
        
        # Save summary with UTF-8 encoding
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        # Open with notepad
        subprocess.Popen(['notepad.exe', str(summary_file)])
        logging.info(f"Summary saved and opened: {summary_file}")
        return True
    except Exception as e:
        logging.error(f"Error saving summary: {str(e)}")
        return False

def download_file(url, destination):
    """Download a file from a URL to a specified destination with progress bar."""
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                progress_bar.update(size)

        logging.info(f"Downloaded file from {url} to {destination}")
        return True
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return False

async def main():
    # Setup logging
    log_file = setup_logging()
    logging.info("=== Starting Podcast Processing Pipeline ===")
    
    try:
        # Delete older MP3 and TXT files in directory
        import cleaner
        cleaner.main()
        
        
        # Get the directory of the Python script
        script_dir = Path(__file__).parent.resolve()
        
        # Ask user to input the audio file path or URL
        print("Please enter the path of the local MP3 file or the URL of an MP3 file:")
        
       
        
        audio_input = input().strip().strip('"')  # Remove quotes if present
        
        
        
        # Determine if input is a URL or local path
        if audio_input.startswith(('http://', 'https://')):
            # It's a URL, download the file
            original_podcast_dir = script_dir / "podcast" / "original-podcast"
            original_podcast_dir.mkdir(parents=True, exist_ok=True)
            file_name = os.path.basename(audio_input)
            new_audio_path = original_podcast_dir / file_name
            
            print(f"Downloading {file_name}...")
            if download_file(audio_input, new_audio_path):
                print(f"Download completed: {new_audio_path}")
            else:
                print("Failed to download audio file")
                return
        else:
            # It's a local path
            audio_file = Path(audio_input)
            if not audio_file.exists():
                logging.error(f"File not found: {audio_input}")
                return
            
            # Copy the file to the original-podcast directory
            original_podcast_dir = script_dir / "podcast" / "original-podcast"
            original_podcast_dir.mkdir(parents=True, exist_ok=True)
            new_audio_path = original_podcast_dir / audio_file.name
            shutil.copy2(audio_file, new_audio_path)
            logging.info(f"Copied audio file to: {new_audio_path}")
        
        # 1. Run splitter.py functionality
        logging.info("Step 1: Splitting MP3 files")
        input_dir = str(original_podcast_dir)
        output_dir = str(script_dir / "podcast" / "splitted-podcast")
        process_directory(input_dir, output_dir)
        
        # 2. Run transcript.py functionality
        logging.info("Step 2: Generating transcripts")
        await transcript_main()
        
        # 3. Get the latest transcript
        logging.info("Step 3: Reading latest transcript")
        transcript_content = get_latest_transcript()
        
        if transcript_content:
            # Save the full transcript
            full_transcript_file = script_dir / "transcript" / "transcript" / "full_transcript.txt"
            with open(full_transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript_content)
            
            # Always summarize (as per your last version)
            summarize = 'yes'
            
            if summarize == 'yes':
                # Upload the full transcript to FTP
                fileurl = upload_file(str(full_transcript_file), FTP_HOST, FTP_USER, FTP_PASSWORD, FTP_DIRECTORY)
                
                # Open the browser with the summary website
                summary_url = f"{SUMMARY_UPLOADED_TEXT_FILE}{fileurl}"
                webbrowser.open(summary_url)
                logging.info(f"Opened summary website: {summary_url}")
            else:
                # Only show the full transcript in notepad
                subprocess.Popen(['notepad.exe', str(full_transcript_file)])
                logging.info(f"Opened full transcript in Notepad: {full_transcript_file}")
        else:
            logging.error("No transcript content found")

            
    except Exception as e:
        logging.error(f"Pipeline error: {str(e)}")
    finally:
        logging.info("=== Podcast Processing Pipeline Completed ===")

if __name__ == "__main__":
    asyncio.run(main())
