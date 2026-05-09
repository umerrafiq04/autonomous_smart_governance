from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlalchemy.orm import Session

from typing import List, Optional

import shutil
import os
import uuid

from backend.database import get_db
from backend.models import Complaint
from backend.schemas import ComplaintResponse

from backend.agents.conversation_manager import (
    handle_conversation
)

router = APIRouter()

UPLOAD_FOLDER = "backend/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# Temporary Session Storage
# =====================================================
chat_sessions = {}


# =====================================================
# CHAT WITH AI
# =====================================================
@router.post("/chat")
async def chat_with_ai(

    message: str = Form(...),

    session_id: Optional[str] = Form(None),

    image: UploadFile = File(None),

    db: Session = Depends(get_db)
):

    try:

        # =========================================
        # Create New Session
        # =========================================
        if not session_id:

            session_id = str(uuid.uuid4())

            chat_sessions[session_id] = {

                "messages": [],

                "data": {},

                "complaint_saved": False
            }

        session = chat_sessions[session_id]

        # =========================================
        # Save Uploaded Image
        # =========================================
        image_path = None

        if image:

            file_extension = image.filename.split(".")[-1]

            unique_filename = (
                f"{uuid.uuid4()}.{file_extension}"
            )

            image_path = os.path.join(
                UPLOAD_FOLDER,
                unique_filename
            )

            with open(image_path, "wb") as buffer:

                shutil.copyfileobj(
                    image.file,
                    buffer
                )

            session["data"]["image_uploaded"] = True

            session["data"]["image_path"] = image_path

        # =========================================
        # Store User Message
        # =========================================
        session["messages"].append({

            "role": "user",

            "content": message
        })

        # =========================================
        # Handle AI Conversation
        # =========================================
        result = handle_conversation(

            session["data"],

            message
        )

        # =========================================
        # Update Session Data
        # =========================================
        session["data"] = result["session_data"]

        # =========================================
        # Store AI Message
        # =========================================
        session["messages"].append({

            "role": "assistant",

            "content": result["message"]
        })

        # =========================================
        # Base Response
        # =========================================
        response = {

            "session_id": session_id,

            "completed": result["completed"],

            "message": result["message"],

            "chat_history": session["messages"]
        }

        # =========================================
        # Save Complaint If Completed
        # =========================================
        if result["completed"]:

            workflow_result = result[
                "workflow_result"
            ]

            response["workflow_result"] = (
                workflow_result
            )

            response["needs_human"] = (
                workflow_result["needs_human"]
            )

            # Avoid duplicate saves
            if not session["complaint_saved"]:

                complaint_data = session["data"]

                description = f"""
Issue:
{complaint_data.get('issue', '')}

Location:
{complaint_data.get('location', '')}

Duration:
{complaint_data.get('duration', '')}

Public Impact:
{complaint_data.get('public_impact', '')}

Contact:
{complaint_data.get('contact', '')}

Email:
{complaint_data.get('email', '')}
"""

                new_complaint = Complaint(

                    title=workflow_result[
                        "issue_type"
                    ],

                    description=description,

                    issue_type=workflow_result[
                        "issue_type"
                    ],

                    severity=workflow_result[
                        "severity"
                    ],

                    department=workflow_result[
                        "department"
                    ],

                    eta=workflow_result[
                        "eta"
                    ],

                    status="AI Analyzed",

                    image_path=complaint_data.get(
                        "image_path"
                    )
                )

                db.add(new_complaint)

                db.commit()

                db.refresh(new_complaint)

                session["complaint_saved"] = True

                session["complaint_id"] = (
                    new_complaint.id
                )

                response["complaint_id"] = (
                    new_complaint.id
                )

        return response

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =====================================================
# ESCALATE TO HUMAN OFFICER
# =====================================================
@router.post("/escalate")
async def escalate_to_human(

    session_id: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        if session_id not in chat_sessions:

            raise HTTPException(

                status_code=404,

                detail="Session not found"
            )

        session = chat_sessions[session_id]

        complaint_id = session.get(
            "complaint_id"
        )

        if not complaint_id:

            raise HTTPException(

                status_code=400,

                detail="Complaint not generated yet."
            )

        complaint = db.query(Complaint).filter(
            Complaint.id == complaint_id
        ).first()

        if not complaint:

            raise HTTPException(

                status_code=404,

                detail="Complaint not found."
            )

        # Update status
        complaint.status = (
            "Escalated To Human Officer"
        )

        db.commit()

        db.refresh(complaint)

        return {

            "message":
            "Complaint escalated successfully.",

            "complaint_id":
            complaint.id,

            "department":
            complaint.department,

            "severity":
            complaint.severity,

            "eta":
            complaint.eta,

            "status":
            complaint.status
        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =====================================================
# GET ALL COMPLAINTS
# =====================================================
@router.get(
    "/",
    response_model=List[ComplaintResponse]
)
def get_all_complaints(

    db: Session = Depends(get_db)
):

    complaints = db.query(Complaint).order_by(
        Complaint.created_at.desc()
    ).all()

    return complaints


# =====================================================
# GET COMPLAINT BY ID
# =====================================================
@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse
)
def get_complaint(

    complaint_id: int,

    db: Session = Depends(get_db)
):

    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:

        raise HTTPException(

            status_code=404,

            detail="Complaint not found"
        )

    return complaint