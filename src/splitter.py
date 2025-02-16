import os
from pydub import AudioSegment
import math
import logging
from datetime import datetime
from pathlib import Path
import shutil
from config import TARGET_SIZE_MB

def setup_logging():
    """
    Setup logging configuration
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f'logs/mp3_splitter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    return log_filename

def split_mp3(file_path, target_size_mb=TARGET_SIZE_MB, output_dir=None):
    """
    Split an MP3 file into chunks of approximately target_size_mb each
    """
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    logging.info(f"Processing file: {file_path} (size: {file_size:.2f}MB)")
    
    if file_size <= target_size_mb:
        logging.info(f"File is smaller than {target_size_mb}MB, skipping split")
        return
    
    try:
        # Load the audio file
        logging.info(f"Loading audio file: {file_path}")
        audio = AudioSegment.from_mp3(file_path)
        
        # Calculate total duration and size ratio
        total_duration = len(audio)
        num_chunks = math.ceil(file_size / target_size_mb)
        ms_per_chunk = total_duration // num_chunks
        
        logging.info(f"Will split into {num_chunks} parts of approximately {target_size_mb}MB each")
        
        # Generate new filenames and split the audio
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        extension = os.path.splitext(file_path)[1]
        
        for i in range(num_chunks):
            start_ms = i * ms_per_chunk
            
            # For the last chunk, take all remaining audio
            if i == num_chunks - 1:
                end_ms = total_duration
            else:
                end_ms = (i + 1) * ms_per_chunk
            
            chunk = audio[start_ms:end_ms]
            chunk_path = os.path.join(output_dir, f"{file_name}-{i+1}{extension}")
            
            # Export the chunk
            logging.info(f"Exporting chunk {i+1}/{num_chunks} to {chunk_path}")
            chunk.export(chunk_path, format="mp3")
            
            # Log the actual size of the exported chunk
            chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
            logging.info(f"Chunk {i+1} size: {chunk_size:.2f}MB")
        
        logging.info(f"Successfully split {file_path} into {num_chunks} parts")
        
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        raise

def process_directory(input_dir, output_dir):
    """
    Process all MP3 files in the given directory
    """
    logging.info(f"Starting to process directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    
    if not os.path.exists(input_dir):
        logging.error(f"Input directory not found: {input_dir}")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    
    # Get all MP3 files in the directory, excluding already split files
    mp3_files = [f for f in os.listdir(input_dir) 
                 if f.lower().endswith('.mp3') and not f.lower().rsplit('-', 1)[-1].isdigit()]

    if not mp3_files:
        logging.info("No MP3 files found in the directory")
        return
    
    logging.info(f"Found {len(mp3_files)} MP3 files to process")
    
    successful_splits = 0
    failed_splits = 0
    
    for mp3_file in mp3_files:
        full_path = os.path.join(input_dir, mp3_file)
        try:
            split_mp3(full_path, output_dir=output_dir)
            successful_splits += 1
        except Exception as e:
            failed_splits += 1
            logging.error(f"Failed to process {mp3_file}: {str(e)}")
            continue
    
    logging.info("\nProcessing Summary:")
    logging.info(f"Total files processed: {len(mp3_files)}")
    logging.info(f"Successful splits: {successful_splits}")
    logging.info(f"Failed splits: {failed_splits}")

if __name__ == "__main__":
    log_file = setup_logging()
    logging.info("=== MP3 Splitter Started ===")
    
    try:
        # Get the directory of the Python script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define input and output directories
        input_dir = os.path.join(script_dir, "podcast", "original-podcast")
        output_dir = os.path.join(script_dir, "podcast", "splitted-podcast")
        
        process_directory(input_dir, output_dir)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
    finally:
        logging.info("=== MP3 Splitter Finished ===")
        logging.info(f"Log file created at: {log_file}")
