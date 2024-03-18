from celery import shared_task
from django.conf import settings
import os
import whisper
import logging
from dotenv import load_dotenv

from patient_requests.models import MicrophoneBedPatient, ProcessedAudioFile
from patient_requests.clients.medplum import MedplumClient

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
from transformers import Trainer, TrainingArguments
from openai import OpenAI

# Load .env file
load_dotenv()

# Load the Whisper model when the worker starts to avoid loading it on each task execution
model = whisper.load_model("tiny")

key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=key)

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

CATEGORIES_PRIORITIES = {
  "Emergency": 1,
  "Pain/Discomfort":  2,
  "Medical Needs": 3,
  "Bathroom Needs": 4,
  "Temperature-Related Needs": 5,
  "Food": 6,
  "Thirsty": 7,
  "Shower": 8,
  "Entertainment Related Needs": 9,
  "Questions/General Information": 10,
  "Other - Non-Medical": 11,
  "Uncategorizable": 12
}

def classify_text(text):
  categories = CATEGORIES_PRIORITIES.keys()

  prompt = f"Classify the following text into one of these categories:\
     {', '.join(categories)}.\n\nText: \"{text}\"\n\nCategory:"

  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user", "content": prompt}
    ]
  )  
  return completion.choices[0].message.content.strip()

@shared_task
def check_and_process_audio_files():
    try:
        audio_file_folder = os.getenv('AUDIO_FILES_DIR')
        
        # List all files in the directory
        for audio_file_name in os.listdir(audio_file_folder):
            audio_file_path = os.path.join(audio_file_folder, audio_file_name)

            # Skip if not an audio file or already processed
            if not audio_file_path.endswith('.wav') or ProcessedAudioFile.objects.filter(file_name=audio_file_name).exists():
                continue
            
            microphone_id = int(audio_file_name.split('-')[0])
            print('audio file path', audio_file_path)
            # Transcribe the audio file
            result = model.transcribe(audio_file_path)
            transcribed_text = result.get("text", "")
            logger.info(f"Transcribed Text: {transcribed_text}")
            
            microphone_patient_mapping = MicrophoneBedPatient.objects.get(microphone_id=microphone_id)
            if not microphone_patient_mapping:
                raise Exception("microphone id not found")

            # Bucket the request
            category = classify_text(transcribed_text)
            
            # Make request in Medplum
            medplum = MedplumClient()
            res = medplum.create_patient_request(mapping=microphone_patient_mapping, transcribed_text=transcribed_text, bucket=category)
            logger.info(f"Client Response: {res}")

            # After processing, record the file name in the database
            ProcessedAudioFile.objects.create(file_name=audio_file_name)
            os.remove(audio_file_path)
    except Exception as e:
        logger.error(f"An error occurred during processing of audio file: {e}", exc_info=True)
        raise Exception(f"An error occurred during processing of audio file: {e}")


if __name__ == "__main__":
  res = classify_text("I have to go pee pee")
  print('r', res)