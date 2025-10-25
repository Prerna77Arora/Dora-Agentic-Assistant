import os
import time
import platform
import gradio as gr
import cv2
from speech_to_text import record_audio, transcribe_with_groq
from ai_agent import ask_agent
from text_to_speech import text_to_speech_with_elevenlabs, text_to_speech_with_gtts
from tools import set_frame_getter

# ---------------- Globals ----------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
AUDIO_DIR = "audio_responses"
os.makedirs(AUDIO_DIR, exist_ok=True)
audio_filepath = os.path.join(AUDIO_DIR, "audio_question.mp3")

camera = None
is_running = False
last_frame = None

# ---------------- Webcam Functions ----------------
def initialize_camera():
    global camera
    if camera is None:
        os_name = platform.system()
        backend = cv2.CAP_DSHOW if os_name == "Windows" else cv2.CAP_AVFOUNDATION
        camera = cv2.VideoCapture(0, backend)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
    return camera is not None and camera.isOpened()

def start_webcam():
    global is_running, last_frame
    is_running = True
    if not initialize_camera():
        print("⚠️ No camera detected!")
        return None
    ret, frame = camera.read()
    if ret:
        last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return last_frame
    return last_frame

def stop_webcam():
    global is_running, camera
    is_running = False
    if camera:
        camera.release()
        camera = None
    return None

def get_webcam_frame():
    global camera, is_running, last_frame
    if not is_running or camera is None:
        return last_frame
    ret, frame = camera.read()
    if ret:
        last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return last_frame
    return last_frame

# ---------------- Share frame getter with tools.py ----------------
def get_current_frame():
    global last_frame
    return last_frame

set_frame_getter(get_current_frame)

# ---------------- Voice + Chat Handling ----------------
def speak_text(response_text: str):
    """
    Converts Dora's text response to speech (using ElevenLabs or gTTS fallback).
    """
    timestamp = str(int(time.time() * 1000))
    audio_path = os.path.join(AUDIO_DIR, f"response_{timestamp}.mp3")
    try:
        text_to_speech_with_elevenlabs(input_text=response_text, output_filepath=audio_path)
    except Exception:
        text_to_speech_with_gtts(input_text=response_text, output_filepath=audio_path)


def process_audio_and_chat():
    """
    Continuous voice conversation mode.
    """
    chat_history = []

    while True:
        try:
            record_audio(file_path=audio_filepath, timeout=10, phrase_time_limit=10)
            user_input = transcribe_with_groq(audio_filepath).strip()

            if not user_input:
                chat_history.append(["(silence)", "No speech detected. Please type your message below 👇"])
                yield chat_history
                continue

            if "goodbye" in user_input.lower():
                response = "Goodbye! 👋"
                chat_history.append([user_input, response])
                speak_text(response)
                yield chat_history
                break

            response = ask_agent(user_query=user_input)
            chat_history.append([user_input, response])
            speak_text(response)
            yield chat_history

        except Exception as e:
            print(f"Error in continuous recording: {e}")
            break


def process_text_input(user_input, chat_history):
    """
    Handles text input queries: get Dora’s response (text + voice).
    """
    if not user_input.strip():
        return chat_history, ""
    
    response = ask_agent(user_query=user_input)
    speak_text(response)  # <— Always speak Dora’s response
    chat_history.append([user_input, response])
    return chat_history, ""

# ---------------- Gradio UI ----------------
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='color: orange; text-align: center; font-size: 3em;'>👧🏼 Dora – Your Personal AI Assistant</h1>")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Webcam Feed")
            start_btn = gr.Button("Start Camera", variant="primary")
            stop_btn = gr.Button("Stop Camera", variant="secondary")
            webcam_output = gr.Image(label="Live Feed", streaming=True, show_label=False, width=640, height=480)
            webcam_timer = gr.Timer(0.033)

        with gr.Column(scale=1):
            gr.Markdown("## Chat Interface")
            chatbot = gr.Chatbot(label="Conversation", height=400, show_label=False)
            user_input = gr.Textbox(placeholder="Type your message here...", show_label=False)
            send_btn = gr.Button("Send", variant="primary")
            speak_btn = gr.Button("🎤 Speak to Dora", variant="secondary")
            clear_btn = gr.Button("Clear Chat", variant="secondary")

    start_btn.click(fn=start_webcam, outputs=webcam_output)
    stop_btn.click(fn=stop_webcam, outputs=webcam_output)
    webcam_timer.tick(fn=get_webcam_frame, outputs=webcam_output, show_progress=False)

    # 🟢 Text input now triggers both text + voice reply
    send_btn.click(fn=process_text_input, inputs=[user_input, chatbot], outputs=[chatbot, user_input])
    user_input.submit(fn=process_text_input, inputs=[user_input, chatbot], outputs=[chatbot, user_input])

    speak_btn.click(fn=process_audio_and_chat, inputs=None, outputs=chatbot)
    clear_btn.click(fn=lambda: [], outputs=chatbot)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
