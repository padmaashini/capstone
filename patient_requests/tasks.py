from celery import shared_task
from django.conf import settings
import os
import whisper
import logging
from dotenv import load_dotenv

from patient_requests.models import MicrophoneBedPatient
from patient_requests.clients.medplum import MedplumClient
# Load .env file
load_dotenv()

# Load the Whisper model when the worker starts to avoid loading it on each task execution
model = whisper.load_model("tiny")

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def check_and_process_audio_files():
    # either get this from the audio file name or from a file 
    microphone_id = 1 

    try:
        audio_file_folder = os.getenv('AUDIO_FILES_DIR')
        audio_file_path = audio_file_folder + '/Hungry.m4a'

        # Transcribe the audio file
        result = model.transcribe(audio_file_path)
        transcribed_text = result.get("text", "")
        logger.info(f"Transcribed Text: {transcribed_text}")
        
        microphone_patient_mapping = MicrophoneBedPatient.objects.get(microphone_id=microphone_id)
        if not microphone_patient_mapping:
            raise Exception("microphone id not found")

        # TO-DO: do some logic here to determine the bucket for the request type

        medplum = MedplumClient()
        res = medplum.create_patient_request(mapping=microphone_patient_mapping, transcribed_text=transcribed_text)
        print('res', res)
        logger.info(f"Client Response: {res}")
    
    except Exception as e:
        logger.error(f"An error occurred during processing of audio file: {e}", exc_info=True)
        raise Exception(f"An error occurred during processing of audio file: {e}")
