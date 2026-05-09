from dotenv import load_dotenv
import os
import json

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

load_dotenv()


# ==========================================
# Initialize LLM
# ==========================================
llm = ChatMistralAI(
    model="mistral-large-latest",

    temperature=0.2
)


# ==========================================
# Resolution Agent
# ==========================================
def resolution_decision(
    issue_type: str,
    severity: str,
    department: str,
    description: str,
    citizen_guidance: str
):

    prompt = f"""
    You are an autonomous civic governance AI assistant.

    Your job:
    1. Decide whether the issue can be solved by AI guidance
    2. Decide whether human escalation is required
    3. Explain why escalation is or is not needed
    4. Generate final citizen response

    Complaint Information:

    Issue Type:
    {issue_type}

    Severity:
    {severity}

    Department:
    {department}

    Description:
    {description}

    Existing AI Guidance:
    {citizen_guidance}

    Rules:
    - Minor FAQs, billing, guidance, informational issues can be resolved by AI.
    - Dangerous, emergency, infrastructure, accident, transformer, major leakage issues require escalation.
    - Keep response professional and citizen-friendly.

    Return ONLY valid JSON in this format:

    {{
        "resolved_by_ai": true,
        "needs_human": false,
        "resolution_reason": "...",
        "final_response": "..."
    }}
    """

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    try:
        cleaned_response = response.content.strip()

        # remove markdown if model returns ```json
        cleaned_response = cleaned_response.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        result = json.loads(cleaned_response)

    except Exception:

        result = {
            "resolved_by_ai": False,
            "needs_human": True,
            "resolution_reason": "Unable to confidently resolve issue.",
            "final_response": "Your issue requires assistance from a human officer."
        }

    return result