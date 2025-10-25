# Dora — Agentic Assistant

> A local, privacy-preserving personal assistant that combines webcam vision, voice I/O and LLM reasoning. Dora provides text and spoken replies, can analyze the live webcam feed for fashion advice or visual queries, and runs locally via a Gradio UI.

## Highlights

- Live webcam feed with visual analysis via the Groq vision/chat API (used by the `analyze_image_with_query` tool).
- Voice input (recording) and transcription via Groq/Whisper.
- Text-to-speech using ElevenLabs (primary) with a gTTS fallback.
- Simple Gradio UI for chat + webcam streaming (`main.py`).

## Repository layout

- `main.py` — app entrypoint. Launches Gradio UI, wires webcam, voice and chat flows.
- `ai_agent.py` — agent orchestration and system prompt; decides when to call visual analysis tools.
- `tools.py` — helper functions for capturing webcam frames and calling Groq Vision/chat.
- `speech_to_text.py` — audio recording and transcription helper (uses `speech_recognition`, `pydub`, and Groq Whisper).
- `text_to_speech.py` — converts Dora's text responses to audio (ElevenLabs primary, gTTS fallback) and plays audio.
- `audio_responses/` — folder where recorded and generated audio files are stored.
- `requirements.txt` / `Pipfile` — Python dependencies.

## Quick contract (what this project does)

- Input: live webcam frames, microphone audio, typed text.
- Output: text responses (chat) and spoken responses (mp3/wav playback).
- Error modes: missing environment keys, camera or microphone permissions, or incorrect microphone index.

## Requirements

- Python 3.8+ recommended
- Windows / macOS / Linux — the code attempts to play audio cross-platform but this README focuses on Windows (PowerShell) usage.
- Hardware: webcam and microphone for full experience.

Python dependencies are listed in `requirements.txt`. Install using pip or Pipenv.

## Environment variables

Set these before running the app (temporary for current PowerShell session):

```powershell
$env:GROQ_API_KEY = "<your_groq_api_key>"
$env:ELEVENLABS_API_KEY = "<your_elevenlabs_api_key>"
```

To persist across sessions, use `setx` (PowerShell):

```powershell
setx GROQ_API_KEY "<your_groq_api_key>"
setx ELEVENLABS_API_KEY "<your_elevenlabs_api_key>"
```

Notes:

- `GROQ_API_KEY` is required for both image analysis (`tools.py`) and audio transcription (`speech_to_text.py`).
- `ELEVENLABS_API_KEY` is optional; if missing the app uses `gTTS` as a fallback for TTS.

## Installation (Windows PowerShell)

Option A — virtualenv + pip (recommended):

```powershell
# create & activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# install deps
pip install -r requirements.txt
```

Option B — Pipenv (if you prefer Pipfile):

```powershell
pipenv install --dev
pipenv shell
```

## Running the app

Start the Gradio web UI (default: 0.0.0.0:7860):

```powershell
python main.py
```

Open the URL shown in the console (or http://localhost:7860) in your browser.

## How to use

- Webcam: click **Start Camera** in the UI. The feed uses OpenCV; allow camera permissions if prompted.
- Text chat: type in the textbox and click **Send** — Dora replies in text and spoken audio.
- Voice chat: click the microphone button (🎤 Speak to Dora) to start continuous speech mode. Dora records, transcribes, and replies.
- Fashion / outfit advice: Dora will automatically call the `analyze_image_with_query` tool if the question contains fashion-related keywords (see `ai_agent.py` FASHION_KEYWORDS list). You can also instruct Dora to analyze the image explicitly.

## Important configuration notes

- Microphone index: `speech_to_text.py` has a hard-coded `mic_index = 19` (commented "Built-in laptop mic"). Change this to match your system. To list available microphone names and indexes run:

```powershell
python - <<'PY'
import speech_recognition as sr
print(list(enumerate(sr.Microphone.list_microphone_names())))
PY
```

- Camera backend: On Windows the code uses `cv2.CAP_DSHOW` by default. If your camera fails to initialize, try modifying `main.py` to change the video backend or index.

## Troubleshooting

- No camera detected / black feed:
  - Ensure the camera is not in use by another application.
  - Allow camera permission for your terminal or the environment where Python is running.
  - Try switching the backend in `main.py` (comment uses CAP_DSHOW for Windows and CAP_AVFOUNDATION for macOS).

- Microphone not recording / wrong device:
  - Run the microphone listing command above and set the `mic_index` in `speech_to_text.py` to the correct value.
  - Ensure your microphone is enabled in Windows settings and not muted.

- TTS not working:
  - If ElevenLabs API key is missing or invalid, the code falls back to gTTS. gTTS requires internet and may produce slower, lower-fidelity audio.
  - On Windows playback, MP3s are converted to WAV before playing via Media.SoundPlayer. If playback fails, check Pydub dependencies (FFmpeg may be required for some formats) and ensure `ffmpeg` is installed and on PATH.

- Groq API / transcription errors:
  - Ensure `GROQ_API_KEY` is valid and your quota/plan supports the used models.
  - Check network connectivity and inspect exceptions printed to the console.

## Security & privacy

- This project sends captured frames and audio to the Groq API and (optionally) ElevenLabs for processing. Do not run this with sensitive data or on an unsecured network without understanding service privacy policies.

## Extending and development notes

- Models & voices: configure model names and voice IDs in `ai_agent.py`, `tools.py`, and `text_to_speech.py`.
- Replace or extend the TTS / STT providers by editing `text_to_speech.py` / `speech_to_text.py`.
- The `tools.py` function `capture_image()` relies on `set_frame_getter()` being called from `main.py` (see `get_current_frame` and `set_frame_getter`). Keep that contract if you refactor.

## Running tests / quick checks

- Test microphone listing (see earlier snippet).
- Test recording (quick manual run):

```powershell
python -c "from speech_to_text import record_audio; record_audio('audio_responses/test.mp3', timeout=5, phrase_time_limit=5)"
```

Check that `audio_responses/test.mp3` exists afterwards.

## Contribution

Feel free to open issues or PRs. Small improvements that help reproducibility (e.g., a `requirements.lock`, a small setup script, or sample env file) are welcome.

