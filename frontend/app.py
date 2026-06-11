import streamlit as st
import requests
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer)
from reportlab.lib.styles import (getSampleStyleSheet)
import tempfile
API_URL = "https://thiru-ai-document-assistant-production.up.railway.app/"
#API_URL = "http://127.0.0.1:8000"

def create_chat_pdf(messages):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    doc = SimpleDocTemplate(
        temp_file.name
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "THIRU's AI Assistant Chat Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 12)
    )

    for msg in messages:

        role = msg["role"].upper()

        content = msg["content"]

        story.append(
            Paragraph(
                f"<b>{role}:</b> {content}",
                styles["BodyText"]
            )
        )

        story.append(
            Spacer(1, 6)
        )

    doc.build(story)

    return temp_file.name

def create_summary_pdf(summary_text):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    doc = SimpleDocTemplate(
        temp_file.name
    )

    styles = getSampleStyleSheet()

    story = [
        Paragraph(
            summary_text,
            styles["BodyText"]
        )
    ]

    doc.build(story)

    return temp_file.name

st.set_page_config(
    page_title="THIRU's AI Assistant",
    page_icon="📄",
    layout="wide"
)

st.title("📄 THIRU's AI Assistant")
st.markdown(
    "Upload documents and ask questions about them."
)

# -----------------------------------
# Sidebar
# -----------------------------------

st.sidebar.title("Document Actions")

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF / DOCX / TXT",
    type=["pdf", "docx", "txt"]
)

if st.sidebar.button("Upload Document"):

    if uploaded_file:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file,
                uploaded_file.type
            )
        }

        response = requests.post(
            f"{API_URL}/upload",
            files=files
        )

        if response.status_code == 200:

            st.sidebar.success(
                f"{uploaded_file.name} uploaded successfully!"
            )

        else:

            st.sidebar.error(
                "Upload failed."
            )

# -----------------------------------
# Profile Extraction
# -----------------------------------

st.sidebar.markdown("---")

if st.sidebar.button("Generate Profile"):

    response = requests.get(
        f"{API_URL}/profile"
    )

    if response.status_code == 200:

        profile = response.json()[
            "profile"
        ]

        st.subheader(
            "Extracted Profile"
        )

        st.write(profile)

# -----------------------------------
# Summary
# -----------------------------------

st.sidebar.markdown("---")

document_name = st.sidebar.text_input(
    "Document Name"
)

if st.sidebar.button(
    "Generate Summary"
):  

    response = requests.post(
        f"{API_URL}/summary",
        json={
            "document_name":
            document_name
        }
    )

    if response.status_code == 200:

        summary = response.json()[
            "summary"
        ]

        st.subheader(
            "Document Summary"
        )

        st.write(summary)

        pdf_path = create_summary_pdf(
            summary
        )

        with open(
            pdf_path,
            "rb"
        ) as pdf_file:

            st.download_button(
                label="📄 Download Summary PDF",
                data=pdf_file,
                file_name="summary.pdf",
                mime="application/pdf"
            )

# -----------------------------------
# Chat Section
# -----------------------------------

st.markdown("---")

if "messages" not in st.session_state:

    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

question = st.chat_input(
    "Ask a question..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    response = requests.post(
        f"{API_URL}/ask",
        json={
            "question": question
        }
    )

    if response.status_code == 200:

        result = response.json()

        answer = result.get(
            "answer",
            "No answer"
        )

        sources = result.get(
            "sources",
            []
        )

        source_text = ""

        if sources:

            source_text = (
                "\n\n**Sources:**\n"
                + "\n".join(
                    [
                        f"- {s}"
                        for s in sources
                    ]
                )
            )

        final_answer = (
            answer
            + source_text
        )

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                final_answer
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content":
                final_answer
            }
        )
    else:
        st.error(
        "Error contacting backend."
        )
# ==========================
# Download Chat PDF
# ==========================

if st.session_state.messages:

    pdf_path = create_chat_pdf(
        st.session_state.messages
    )

    with open(
        pdf_path,
        "rb"
    ) as pdf_file:

        st.download_button(
            label="📄 Download Chat PDF",
            data=pdf_file,
            file_name="THIRU's AI chat_report.pdf",
            mime="application/pdf"
        )