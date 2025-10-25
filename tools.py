import base64
import cv2
import os
from groq import Groq

# Function reference from main.py to get the current live webcam frame
current_frame_getter = None  

def set_frame_getter(func):
    """
    Called once from main.py to share the current live webcam frame.
    """
    global current_frame_getter
    current_frame_getter = func


def capture_image() -> str:
    """
    Gets the latest frame from the shared webcam stream.
    Encodes it as Base64 JPEG.
    """
    if current_frame_getter is None:
        raise RuntimeError("Frame getter not initialized. Call set_frame_getter() from main.py.")
    
    frame = current_frame_getter()
    if frame is None:
        raise RuntimeError("No live frame available from webcam.")

    # Convert from RGB to BGR for OpenCV encoding
    ret, buf = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    if not ret:
        raise RuntimeError("Failed to encode webcam frame.")
    
    return base64.b64encode(buf).decode('utf-8')


def analyze_image_with_query(query: str) -> str:
    """
    Captures the latest live frame and sends it to Groq Vision API for analysis.
    Can be used for fashion advice, object detection, or general visual queries.
    """
    img_b64 = capture_image()
    model = "meta-llama/llama-4-maverick-17b-128e-instruct"

    if not query or not img_b64:
        return "Error: both 'query' and live image frame required."

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}  # Live webcam frame
            ],
        }
    ]

    chat_completion = client.chat.completions.create(messages=messages, model=model)
    return chat_completion.choices[0].message.content
