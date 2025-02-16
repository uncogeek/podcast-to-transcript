# Podcast Summary Generator

This application automates the process of generating summaries for podcast episodes. It splits audio files, transcribes them, and produces concise summaries.

## Features

- Audio file splitting
- Transcription of audio to text
- Summary generation
- FTP upload functionality

## Prerequisites

- Python 3.7+
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/podcast-to-transcript.git
   cd podcast-to-transcript/src
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your configuration:
   - Update the values in `config.py` with your API keys and settings

## Usage

1. Don't need to Place your podcast audio file in the project directory.

2. Run the main script:
   ```
   python main.py
   ```

3. Follow the prompts to enter the podcast URL or specify the path of the MP3 file on your Windows device. Additionally, you can simply drag and drop the audio file into the terminal!

4. The script will process the audio, generate a transcript, and open the full transcript. It will then upload the transcript via FTP and pass it to the backend for summarization using AI models.

## Configuration

Edit `config.py` to customize the following settings:

- `TARGET_SIZE_MB`: Target size for audio file splitting
- `API_KEY`: Your API key for
- `API_BASE`: Base URL for the transcription API (OpenAI or proxies such as OpenRouter)
- `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`, `FTP_DIRECTORY`: FTP settings for file upload text file
- `UPLOAD_BASE_URL`: Base URL for accessing uploaded files
- `SUMMARY_API_URL`: URL for the summary generation API

## install ffmpeg on Windows os
<details>
  <summary>How to install ffmpeg on Windows</summary>
  1. **Download FFmpeg**:
   - Go to https://github.com/BtbN/FFmpeg-Builds/releases
   - Download the latest "ffmpeg-master-latest-win64-gpl.zip"

2. **Extract the Files**:
   - Create a folder at `C:\ffmpeg`
   - Extract the downloaded zip file
   - Inside the extracted folder, find the `bin` folder
   - Copy all files from the `bin` folder to `C:\ffmpeg`

3. **Add to System PATH**:
   - Press Win + X and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path"
   - Click "Edit"
   - Click "New"
   - Add `C:\ffmpeg`
   - Click "OK" on all windows

4. **Verify Installation**:
   - Open a new Command Prompt
   - Type `ffmpeg -version`
   - If you see version information, FFmpeg is successfully installed


After installation, restart your os. The pydub warning should be resolved.

</details>


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
