from dotenv import load_dotenv
import os
import json

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

from backend.agents.workflow import (
    run_complaint_workflow
)

load_dotenv()


# =====================================================
# Initialize LLM
# =====================================================
llm = ChatMistralAI(
    model="mistral-large-latest",
    
)


# =====================================================
# Intelligent Conversation Manager
# =====================================================
def handle_conversation(

    session_data,

    user_message
):

    # =============================================
    # Initialize Conversation History
    # =============================================
    if "conversation" not in session_data:

        session_data["conversation"] = []

    # Store user message
    session_data["conversation"].append({

        "role": "user",

        "content": user_message
    })

    # =============================================
    # Build Conversation Text
    # =============================================
    conversation_text = ""

    for msg in session_data["conversation"]:

        conversation_text += (
            f"{msg['role']}: {msg['content']}\n"
        )

    # =============================================
    # Intelligent Intake Prompt
    # =============================================
    prompt = f"""
You are an intelligent civic governance intake assistant.

Your job:
- understand the citizen issue
- collect sufficient complaint details conversationally
- ask intelligent follow-up questions dynamically
- avoid repeating questions
- behave professionally and naturally
- adapt questions based on issue type

Current Conversation:
{conversation_text}

Already Collected Data:
{json.dumps(session_data, indent=2)}

You must determine:
1. What information is already available
2. What critical information is missing
3. What is the BEST next question
4. Whether enough information exists for final complaint analysis

Important Rules:
- NEVER ask repeated questions
- NEVER jump directly to final analysis
- If user has not described issue properly, ask them to explain issue
- Different issue types require different questions
- Drainage/water issues need location + impact
- Electricity issues need danger assessment
- Road issues need location + severity
- Ask naturally like a real support officer
- Keep responses short and professional

Return ONLY valid JSON:

{{
    "enough_information": true/false,
    "issue_type": "...",
    "collected_information": {{
        "issue": "...",
        "location": "...",
        "duration": "...",
        "contact": "...",
        "email": "...",
        "public_impact": "..."
    }},
    "missing_fields": [],
    "next_question": "...",
    "professional_response": "..."
}}
"""

    response = llm.invoke([

        HumanMessage(content=prompt)
    ])

    try:

        cleaned_response = (
            response.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(
            cleaned_response
        )

    except Exception:

        result = {

            "enough_information": False,

            "issue_type": "General",

            "collected_information": {},

            "missing_fields": ["issue"],

            "next_question":
            "Please describe the civic issue you are facing.",

            "professional_response":
            "I need some additional information to assist you properly."
        }

    # =============================================
    # Update Session Data
    # =============================================
    collected_info = result.get(
        "collected_information",
        {}
    )

    for key, value in collected_info.items():

        if value:

            session_data[key] = value

    # =============================================
    # Store AI Message
    # =============================================
    ai_message = (
        result.get("professional_response")
        or result.get("next_question")
    )

    session_data["conversation"].append({

        "role": "assistant",

        "content": ai_message
    })

    # =============================================
    # If Information Is NOT Enough
    # =============================================
    if not result["enough_information"]:

        return {

            "completed": False,

            "message": ai_message,

            "session_data": session_data
        }

    # =============================================
    # Run Full Governance Workflow
    # =============================================
    final_result = run_complaint_workflow(

        title="Civic Complaint",

        description=f"""
Issue:
{session_data.get('issue', '')}

Location:
{session_data.get('location', '')}

Duration:
{session_data.get('duration', '')}

Public Impact:
{session_data.get('public_impact', '')}

Contact:
{session_data.get('contact', '')}

Email:
{session_data.get('email', '')}
"""
    )

    # =============================================
    # Final Structured Response
    # =============================================
    final_message = f"""
## Complaint Analysis Complete

### Issue Type
{final_result['issue_type']}

### Severity
{final_result['severity']}

### Assigned Department
{final_result['department']}

### Estimated Response Time
{final_result['eta']}

---

### Citizen Guidance

{final_result['citizen_guidance']}

---

### AI Resolution Status

{final_result['final_response']}
"""

    session_data["conversation"].append({

        "role": "assistant",

        "content": final_message
    })

    return {

        "completed": True,

        "message": final_message,

        "session_data": session_data,

        "workflow_result": final_result
    }