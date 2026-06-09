from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from document_loader import DocumentLoader
from vector_store import VectorStore
from rag_engine import RAGEngine

app = FastAPI(
    title="THIRU's AI Assistant",
    version="1.0"
)

# Allow frontend requests   
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "../uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
vector_store = VectorStore()

# Load saved vector DB if exists
try:
    vector_store.load()
except:
    pass

rag_engine = RAGEngine(vector_store)


@app.get("/")
def home():
    return {
        "message": "AI Document Assistant API Running"
    }


# ---------------------------------------
# Upload Document
# ---------------------------------------
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    text = DocumentLoader.load_document(
        file_path
    )
    vector_store.clear()
    vector_store.add_document(
        text,
        file.filename
    )

    vector_store.save()

    return {
        "status": "success",
        "filename": file.filename
    }


# ---------------------------------------
# Ask Question
# ---------------------------------------
@app.post("/ask")
async def ask_question(
    data: dict
):

    question = data.get("question")

    if not question:

        return {
            "error":
            "Question is required"
        }

    result = rag_engine.ask(
        question
    )

    return result


# ---------------------------------------
# Document Summary
# ---------------------------------------
@app.post("/summary")
async def summary(
    data: dict
):

    document_name = data.get(
        "document_name"
    )

    if not document_name:

        return {
            "error":
            "document_name required"
        }

    summary_text = (
        rag_engine.summarize_document(
            document_name
        )
    )

    return {
        "summary": summary_text
    }


# ---------------------------------------
# Extract Profile
# ---------------------------------------
@app.get("/profile")
async def profile():

    profile_data = (
        rag_engine.extract_profile()
    )

    return {
        "profile": profile_data
    }