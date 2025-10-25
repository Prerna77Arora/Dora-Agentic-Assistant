import os
import subprocess
import platform
from elevenlabs.client import ElevenLabs
from elevenlabs import save as eleven_save
from pydub import AudioSegment
from gtts import gTTS

# Load ElevenLabs API key from environment
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def text_to_speech_with_elevenlabs(input_text, output_filepath):
    """
    Convert input text to speech using ElevenLabs and save as MP3.
    Then play the audio.
    """
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=input_text,
        voice_id="ZF6FPAbjXT4488VcRRnw",  # Choose your preferred voice
        model_id="eleven_multilingual_v2",
        output_format="mp3_22050_32",
    )
    eleven_save(audio, output_filepath)
    play_audio(output_filepath)

def text_to_speech_with_gtts(input_text, output_filepath):
    """
    Convert input text to speech using gTTS and save as MP3.
    Then play the audio.
    """
    tts = gTTS(text=input_text, lang="en", slow=False)
    tts.save(output_filepath)
    play_audio(output_filepath)

def play_audio(filepath):
    """
    Play audio file on different OSes.
    On Windows, converts MP3 to WAV to be compatible with Media.SoundPlayer.
    """
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', filepath])
        elif os_name == "Windows":
            # Convert MP3 to WAV for Windows SoundPlayer
            if filepath.lower().endswith(".mp3"):
                wav_path = filepath.replace(".mp3", ".wav")
                audio_segment = AudioSegment.from_mp3(filepath)
                audio_segment.export(wav_path, format="wav")
                filepath = wav_path
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{filepath}").PlaySync();'])
        elif os_name == "Linux":
            if filepath.lower().endswith(".mp3"):
                subprocess.run(['mpg123', filepath])
            else:
                subprocess.run(['aplay', filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"Error playing audio: {e}")
