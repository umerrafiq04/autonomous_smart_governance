import streamlit as st
import requests
import pandas as pd


# =====================================================
# Page Config
# =====================================================
st.set_page_config(

    page_title="CivicMind AI",

    page_icon="🏛️",

    layout="wide"
)

API_BASE_URL = (
    "http://127.0.0.1:8000/api/complaints"
)


# =====================================================
# Session State
# =====================================================
if "messages" not in st.session_state:

    st.session_state.messages = []

if "session_id" not in st.session_state:

    st.session_state.session_id = None

if "workflow_result" not in st.session_state:

    st.session_state.workflow_result = None


# =====================================================
# Sidebar
# =====================================================
st.sidebar.title("🏛️ CivicMind AI")

page = st.sidebar.radio(

    "Navigation",

    [
        "Citizen AI Assistant",
        "Authority Dashboard"
    ]
)


# =====================================================
# CITIZEN AI ASSISTANT
# =====================================================
if page == "Citizen AI Assistant":

    st.title("🤖 CivicMind AI Assistant")

    st.markdown("""
    Welcome to the AI-powered civic governance assistant.
    
    The assistant will:
    - understand your issue
    - collect required complaint details
    - provide department guidance
    - attempt autonomous resolution
    - escalate to human officers if necessary
    """)

    st.write("---")

    # =================================================
    # Display Chat History
    # =================================================
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])

    # =================================================
    # Upload Image
    # =================================================
    uploaded_image = st.file_uploader(

        "Upload Supporting Image (Optional)",

        type=["png", "jpg", "jpeg"]
    )

    # =================================================
    # Chat Form
    # =================================================
    with st.form(
        "chat_form",
        clear_on_submit=True
    ):

        user_input = st.text_input(
            "Describe your issue"
        )

        send_button = st.form_submit_button(
            "Send"
        )

    # =================================================
    # Send Message
    # =================================================
    if send_button and user_input:

        # Add user message
        st.session_state.messages.append({

            "role": "user",

            "content": user_input
        })

        files = {}

        if uploaded_image:

            files["image"] = (

                uploaded_image.name,

                uploaded_image,

                uploaded_image.type
            )

        data = {

            "message": user_input
        }

        if st.session_state.session_id:

            data["session_id"] = (
                st.session_state.session_id
            )

        # =============================================
        # Call Backend
        # =============================================
        with st.spinner(
            "AI assistant is processing..."
        ):

            response = requests.post(

                f"{API_BASE_URL}/chat",

                data=data,

                files=files
            )

        # =============================================
        # Handle Response
        # =============================================
        if response.status_code == 200:

            result = response.json()

            st.session_state.session_id = (
                result["session_id"]
            )

            ai_message = result["message"]

            # Store assistant message
            st.session_state.messages.append({

                "role": "assistant",

                "content": ai_message
            })

            # Store workflow result
            if result.get("completed"):

                st.session_state.workflow_result = (
                    result.get("workflow_result")
                )

            st.rerun()

        else:

            st.error(
                "Failed to communicate with backend."
            )

            st.write(response.text)

    # =================================================
    # FINAL ANALYSIS SECTION
    # =================================================
    if st.session_state.workflow_result:

        workflow = (
            st.session_state.workflow_result
        )

        st.write("---")

        st.subheader(
            "📋 Final Governance Analysis"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                f"Issue Type: {workflow['issue_type']}"
            )

            st.warning(
                f"Severity: {workflow['severity']}"
            )

        with col2:

            st.success(
                f"Department: {workflow['department']}"
            )

            st.info(
                f"ETA: {workflow['eta']}"
            )

        st.write("---")

        st.subheader("📌 Citizen Guidance")

        st.write(
            workflow["citizen_guidance"]
        )

        st.write("---")

        st.subheader("🤖 AI Resolution")

        st.write(
            workflow["final_response"]
        )

        # =============================================
        # Talk To Human Button
        # =============================================
        if workflow["needs_human"]:

            st.warning(
                "This issue may require assistance from a human officer."
            )

            if st.button(
                "📞 Talk To Human Officer"
            ):

                escalate_response = requests.post(

                    f"{API_BASE_URL}/escalate",

                    data={
                        "session_id":
                        st.session_state.session_id
                    }
                )

                if escalate_response.status_code == 200:

                    escalation_result = (
                        escalate_response.json()
                    )

                    st.success(
                        "Complaint escalated successfully."
                    )

                    st.markdown(f"""
### ✅ Complaint Registered

**Complaint ID:** {escalation_result['complaint_id']}

**Assigned Department:** {escalation_result['department']}

**Severity:** {escalation_result['severity']}

**Estimated Response Time:** {escalation_result['eta']}

**Status:** {escalation_result['status']}
""")

                else:

                    st.error(
                        "Failed to escalate complaint."
                    )


# =====================================================
# AUTHORITY DASHBOARD
# =====================================================
elif page == "Authority Dashboard":

    st.title("📊 Authority Dashboard")

    st.markdown("""
    Governance monitoring dashboard for authorities.
    """)

    with st.spinner(
        "Loading complaints..."
    ):

        response = requests.get(
            API_BASE_URL
        )

    if response.status_code == 200:

        complaints = response.json()

        if complaints:

            total_complaints = len(
                complaints
            )

            critical_count = len([

                c for c in complaints

                if c["severity"] == "Critical"
            ])

            high_count = len([

                c for c in complaints

                if c["severity"] == "High"
            ])

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Total Complaints",
                    total_complaints
                )

            with col2:

                st.metric(
                    "Critical Issues",
                    critical_count
                )

            with col3:

                st.metric(
                    "High Severity",
                    high_count
                )

            st.write("---")

            df = pd.DataFrame(
                complaints
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.info(
                "No complaints found."
            )

    else:

        st.error(
            "Failed to load dashboard."
        )