from celery import shared_task
import whisper

@shared_task
def check_and_process_audio_files():
    # assuming there is only 1 file in the folder

    audio_file = '../audios/Hungry.m4a'

    model = whisper.load_model("large")
    result = model.transcribe(audio_file)
    
    transcribed_text = result.get("text", "")
    print("transcribed_text", transcribed_text)
