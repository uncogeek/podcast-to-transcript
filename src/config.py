#------------------------------------------------------------------------------
# Audio Processing Configuration
#------------------------------------------------------------------------------
# Maximum size in megabytes for each audio chunk when splitting MP3 files
# Higher values mean fewer chunks but may impact processing performance
TARGET_SIZE_MB = 1

#------------------------------------------------------------------------------
# API Configuration
#------------------------------------------------------------------------------
# Your authentication key for accessing the API service
# Obtain this from your service provider's dashboard
API_KEY = "YOUR_API_KEY"

# Base URL for API requests
# Examples:
# - Direct OpenAI: https://api.openai.com/v1
# - OpenRouter proxy: https://openrouter.ai/api/v1
API_BASE = "ENDPOINT_URL/v1"

#------------------------------------------------------------------------------
# FTP Server Configuration
#------------------------------------------------------------------------------
# Hostname of your FTP server
# Example: ftp.mywebsite.com
FTP_HOST = "ftp.host.domain"

# FTP account username
# Example: user@mywebsite.com
FTP_USER = "user@host.domain"

# Password for FTP authentication
# Keep this secure and consider using environment variables
FTP_PASSWORD = "FTP_PASSWORD"

# Root directory for FTP operations
# Default '/' uses the FTP user's home directory
# Change only if you need a specific subdirectory
FTP_DIRECTORY = "/"

#------------------------------------------------------------------------------
# Web URL Configuration
#------------------------------------------------------------------------------
# Base URL where uploaded text files will be accessible
# Example: https://mysite.com/uploads
# Must correspond to the FTP directory's web-accessible path
UPLOAD_BASE_URL = "URL"

# API endpoint for retrieving summaries within the application
# Required for in-app summary functionality
# See api-python.php for implementation details
SUMMARY_API_URL = "URL"

# Web URL template for accessing podcast summaries
# Example: https://mywebsite.com/podcast-summary/index.php?file=
# The actual file path will be appended to this URL
SUMMARY_UPLOADED_TEXT_FILE = "URL"