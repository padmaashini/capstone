from celery import shared_task
from django.conf import settings
import os
import whisper
import logging
from dotenv import load_dotenv

from patient_requests.models import MicrophoneBedPatient
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

# Load .env file
load_dotenv()

# Load the Whisper model when the worker starts to avoid loading it on each task execution
model = whisper.load_model("tiny")

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

requests = [
    "I want to eat chips",
    "I need a blanket",
    "I am feeling pain in my back",
    "Can I go to the bathroom",
    "I need some ice for my head",
    "I feel sick, need clinical help",
    "I want to go pee", 
    "I need to take a dump",
    'Can I get ice for my drink?',
  'Can you need to use the restroom',
  'I need to see a doctor',
  'Can Can you go to the bathroom?',
  'Can yous the bathroom available?',
  'When is my next checkup?',
  "I'm feeling a sharp pain in my back",
  'Can I have a blanket?',
  'Can I get ice for my drink?',
  "Can you'm feeling a sharp pain in my back",
  'It hurts here',
  'Can you would like to have lunch now',
  'Can Can you get my medication?',
  'What does my test result say?',
  'It hurts here',
  'What does my test result say?',
  'Can Can you go to the bathroom?',
  'When is my next checkup?',
  'My head hurts',
  "I'm craving for some food"
]
categories = ["food", "blanket", "pain", "bathroom", "ice", "clinical", "bathroom", "bathroom", 'ice',
  'bathroom',
  'clinical',
  'bathroom',
  'bathroom',
  'clinical',
  'pain',
  'blanket',
  'ice',
  'pain',
  'pain',
  'food',
  'clinical',
  'clinical',
  'pain',
  'clinical',
  'bathroom',
  'clinical',
  'pain',
  'food']

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
        model = make_pipeline(CountVectorizer(), MultinomialNB())

        # Train the model
        model.fit(requests, categories)

        # Now, predict the category of a new text
        new_texts = ["I want to go pee"]
        predicted_categories = model.predict(new_texts)
        print('predicted_categories', predicted_categories)
        medplum = MedplumClient()
        res = medplum.create_patient_request(mapping=microphone_patient_mapping, transcribed_text=transcribed_text)
        print('res', res)
        logger.info(f"Client Response: {res}")
    
    except Exception as e:
        logger.error(f"An error occurred during processing of audio file: {e}", exc_info=True)
        raise Exception(f"An error occurred during processing of audio file: {e}")
