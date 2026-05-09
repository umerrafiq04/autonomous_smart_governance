from dotenv import load_dotenv
import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()


# ==========================================
# Initialize Gemini LLM
# ==========================================
from langchain_mistralai import ChatMistralAI

llm = ChatMistralAI(
    model="mistral-large-latest",
    
)

# -----


# ==========================================
# Complaint Analysis Agent
# ==========================================
def analyze_complaint(title: str, description: str):

    prompt = f"""
    You are an AI complaint analysis agent for a smart governance platform.

    Analyze the following civic complaint.

    Complaint Title:
    {title}

    Complaint Description:
    {description}

    Your task:
    1. Identify issue type
    2. Determine severity level
    3. Assign department
    4. Estimate resolution ETA
    5. Generate short summary
    6. Ask ONE follow-up question

    Return ONLY valid JSON in this format:

    {{
        "issue_type": "...",
        "severity": "...",
        "department": "...",
        "eta": "...",
        "summary": "...",
        "follow_up_question": "..."
    }}
    """

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    try:
        result = json.loads(response.content)

    except Exception:

        # fallback if AI returns invalid JSON
        result = {
            "issue_type": "General Issue",
            "severity": "Medium",
            "department": "General Department",
            "eta": "48 Hours",
            "summary": "Issue submitted successfully.",
            "follow_up_question": "Can you provide more details?"
        }

    return result