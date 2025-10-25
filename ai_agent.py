from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools import analyze_image_with_query

# ---------------- System Prompt ----------------
system_prompt = """You are Dora — a witty, clever, and helpful assistant.
Here’s how you operate:
    - If the user asks a question that requires looking via the webcam, call the analyze_image_with_query tool.
    - Always provide natural, witty, and human-sounding responses.
    - You can give advice on fashion, outfit choices, and style based on the user's appearance in the webcam feed.
    - If the question does not require a live image, answer using your own knowledge and reasoning.
"""

# ---------------- LLM Setup ----------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
)

# Keywords to detect fashion-related questions
FASHION_KEYWORDS = ["outfit", "clothes", "dress", "style", "fashion", "look", "what should i wear", "fashion advice"]

# ---------------- Agent Function ----------------
def ask_agent(user_query: str) -> str:
    """
    Detects fashion-related queries and uses live webcam analysis if needed.
    Returns Dora's response as a string.
    """
    query_lower = user_query.lower()
    use_webcam_tool = any(word in query_lower for word in FASHION_KEYWORDS)

    if use_webcam_tool:
        # Automatically analyze current outfit via webcam
        response = analyze_image_with_query(f"Give fashion advice for this outfit: {user_query}")
        return response

    # Otherwise, use LLM reasoning without live image
    agent = create_react_agent(
        model=llm,
        tools=[analyze_image_with_query],  # still available if needed
        prompt=system_prompt
    )

    input_messages = {"messages": [{"role": "user", "content": user_query}]}
    response = agent.invoke(input_messages)

    return response['messages'][-1].content
