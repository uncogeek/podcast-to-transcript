import ftplib
from datetime import datetime
import os
from config import UPLOAD_BASE_URL

def upload_file(file_path, ftp_host, ftp_user, ftp_pass, ftp_dir):
    # Extract filename and generate new name with timestamp
    original_filename = os.path.basename(file_path)
    file_extension = os.path.splitext(original_filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"transcript_{timestamp}{file_extension}"
    
    # Connect to FTP server and upload file
    with ftplib.FTP(ftp_host) as ftp:
        ftp.login(user=ftp_user, passwd=ftp_pass)
        ftp.cwd(ftp_dir)
        
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {new_filename}', file)
    
    # Construct and return full URL
    return f"{UPLOAD_BASE_URL}{new_filename}"
