import os
from pathlib import Path
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f'cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return None

def clean_directory(directory):
    """Remove all files in the specified directory."""
    try:
        directory = Path(directory)
        if not directory.exists():
            logging.info(f"Directory doesn't exist, skipping: {directory}")
            return 0
        
        count = 0
        for file_path in directory.glob('*'):
            if file_path.is_file():
                # Check file extensions
                if file_path.suffix.lower() in ['.txt', '.mp3', '.log']:
                    file_path.unlink()
                    #logging.info(f"Removed: {file_path}")
                    count += 1
        
        return count
    except Exception as e:
        logging.error(f"Error cleaning directory {directory}: {str(e)}")
        return 0

def main():
    #log_file = setup_logging()
    logging.info("=== Starting Directory Cleanup ===")
    
    try:
        # Get the root directory (where the script is located)
        root_dir = Path(__file__).parent.resolve()
        
        # Define directories to clean
        directories = [
            root_dir / "transcript" / "splitted",
            root_dir / "transcript" / "summary",
            root_dir / "transcript" / "transcript",
            root_dir / "podcast" / "original-podcast",
            root_dir / "podcast" / "splitted-podcast",
            root_dir / "logs"
        ]
        
        total_removed = 0
        
        # Clean each directory
        for directory in directories:
            #logging.info(f"\nCleaning directory: {directory}")
            files_removed = clean_directory(directory)
            total_removed += files_removed
            #logging.info(f"Removed {files_removed} files from {directory}")
        
        #logging.info(f"\nCleanup Summary:")
        logging.info(f"Total files removed: {total_removed}")
        logging.info(f"Directories processed: {len(directories)}")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
    finally:
        logging.info("=== Directory Cleanup Completed ===")
        print("all cleaned.")
        #logging.info(f"Cleanup log saved to: {log_file}")

if __name__ == "__main__":
    main()