from dotenv import load_dotenv
import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()


# ==========================================
# Initialize Gemini
# ==========================================
from langchain_mistralai import ChatMistralAI

llm = ChatMistralAI(
    model="mistral-large-latest",
    
)


# ==========================================
# Governance Decision Agent
# ==========================================
def governance_decision(
    issue_type: str,
    severity: str,
    department: str,
    description: str
):

    prompt = f"""
    You are an AI Governance Decision Agent.

    Complaint Information:

    Issue Type:
    {issue_type}

    Severity:
    {severity}

    Department:
    {department}

    Description:
    {description}

    Your responsibilities:
    1. Confirm issue priority
    2. Generate official governance response
    3. Create tracking status
    4. Recommend escalation if required

    Return ONLY valid JSON in this format:

    {{
        "priority": "...",
        "tracking_status": "...",
        "official_response": "...",
        "escalation_required": "Yes/No"
    }}
    """

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    try:
        result = json.loads(response.content)

    except Exception:

        result = {
            "priority": severity,
            "tracking_status": "Complaint Registered",
            "official_response": "Your complaint has been forwarded to the concerned department.",
            "escalation_required": "No"
        }

    return result