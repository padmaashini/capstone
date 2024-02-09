from celery import shared_task
from django.conf import settings
import os
import whisper
import logging
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load the Whisper model when the worker starts to avoid loading it on each task execution
model = whisper.load_model("tiny")

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def check_and_process_audio_files():
    try:
        audio_file_folder = os.getenv('AUDIO_FILES_DIR')
        audio_file_path = audio_file_folder + 'Hungry.m4a'

        # Transcribe the audio file
        result = model.transcribe(audio_file_path)
        
        # Extract the transcribed text
        transcribed_text = result.get("text", "")
        logger.info(f"Transcribed text: {transcribed_text}")
        
        # You can then return this text if you wish to use it in further task chains
        return transcribed_text

    except Exception as e:
        # Log exceptions
        logger.error(f"An error occurred during transcription: {e}", exc_info=True)
        # Reraise the exception to ensure the task is marked as failed
        raise

if __name__ == "__main__":
    check_and_process_audio_files()