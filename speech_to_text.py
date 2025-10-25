import os
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------- Voice Recording ----------------
def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Record audio from the correct microphone and save as MP3.

    Args:
        file_path (str): Path to save the recorded audio file.
        timeout (int): Maximum time to wait for the user to start speaking (seconds).
        phrase_time_limit (int): Maximum duration of recording (seconds).
    """
    recognizer = sr.Recognizer()

    # Set the correct microphone index from `sr.Microphone.list_microphone_names()`
    mic_index = 19  # Built-in laptop mic (change if needed)

    try:
        with sr.Microphone(device_index=mic_index) as source:
            logging.info("Adjusting for ambient noise... Please stay silent.")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            logging.info("Start speaking now...")

            # Record audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")

            # Ensure folder exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Convert to MP3
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")

            logging.info(f"Audio saved to {file_path}")

    except sr.WaitTimeoutError:
        logging.error("No speech detected within timeout. Try speaking closer or louder.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


# ---------------- Transcription via Groq ----------------
def transcribe_with_groq(audio_filepath):
    """
    Convert an audio file to text using Groq's Whisper model.
    
    Args:
        audio_filepath (str): Path to the audio MP3 file.
    
    Returns:
        str: Transcribed text.
    """
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=GROQ_API_KEY)
    stt_model = "whisper-large-v3"

    if not os.path.exists(audio_filepath):
        raise FileNotFoundError(f"Audio file not found: {audio_filepath}")

    with open(audio_filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=stt_model,
            file=audio_file,
            language="en"
        )

    return transcription.text


# ---------------- Optional Test ----------------
if __name__ == "__main__":
    test_path = os.path.join("audio_responses", "test_question.mp3")
    record_audio(file_path=test_path, timeout=20, phrase_time_limit=10)
    if os.path.exists(test_path):
        print("Recording succeeded! File saved at:", test_path)
    else:
        print("Recording failed!")
