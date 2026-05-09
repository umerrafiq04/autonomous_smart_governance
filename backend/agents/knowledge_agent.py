from dotenv import load_dotenv
import os

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
# Department Knowledge Base
# ==========================================
department_knowledge = {

    "Road Department": """
    Road damage and potholes can cause serious traffic accidents.
    Citizens should avoid damaged areas if possible.
    Emergency repair teams usually respond within 24-48 hours.
    """,

    "Water Department": """
    Water leakages near electrical poles can be dangerous.
    Citizens should avoid contaminated water exposure.
    Emergency water issues are typically resolved within 6-24 hours.
    """,

    "Electricity Department": """
    Transformer issues and exposed wires are highly dangerous.
    Citizens should stay away from damaged electrical equipment.
    Emergency electricity teams should be contacted immediately.
    """
}


# ==========================================
# Knowledge Agent
# ==========================================
def generate_guidance(
    department: str,
    issue_type: str,
    description: str
):

    knowledge = department_knowledge.get(
        department,
        "General civic safety guidelines apply."
    )

    prompt = f"""
    You are an intelligent civic governance assistant.

    Department:
    {department}

    Issue Type:
    {issue_type}

    Complaint Description:
    {description}

    Department Knowledge:
    {knowledge}

    Your task:
    1. Provide helpful citizen guidance
    2. Give safety instructions
    3. Explain what citizens should do temporarily
    4. Keep response short and professional

    Generate a citizen-friendly response.
    """

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return response.content