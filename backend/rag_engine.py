import os
from dotenv import load_dotenv
from groq import Groq


class RAGEngine:

    def __init__(self, vector_store):

        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise Exception(
                "GROQ_API_KEY not found in .env file"
            )

        self.client = Groq(
            api_key=api_key
        )

        self.vector_store = vector_store

    # ----------------------------------------
    # Build Context
    # ----------------------------------------
    def build_context(self, search_results):

        context_parts = []

        for item in search_results:

            context_parts.append(
                f"""
DOCUMENT: {item['document']}

CONTENT:
{item['text']}
"""
            )

        return "\n".join(context_parts)

    # ----------------------------------------
    # Ask Question
    # ----------------------------------------
    def ask(
        self,
        question,
        top_k=10
    ):

        results = self.vector_store.search(
            question,
            top_k=top_k
        )

        if not results:

            return {
                "answer":
                "No documents have been uploaded yet.",
                "sources": []
            }

        print("\n===== RETRIEVED CHUNKS =====")

        for item in results:
            print(item["text"])
            print("-" * 50)

        print("===== END CHUNKS =====\n")

        context = self.build_context(
            results
        )

        prompt = f"""
You are an AI Document Assistant.

STRICT RULES:

1. Answer ONLY using the information present in the provided document context.
2. Do NOT use outside knowledge.
3. Do NOT guess.
4. If the answer is not found in the context, respond exactly:

I could not find this information in the uploaded documents.

5. Keep answers concise.
6. If a person's name, email, phone number, CGPA, skill, project, certification, or education details exist in the context, provide them exactly.

DOCUMENT CONTEXT:

{context}

QUESTION:

{question}

ANSWER:
"""

        try:

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

        except Exception as e:

            answer = (
                f"Groq Error: {str(e)}"
            )

        unique_sources = list(
            set(
                [
                    item["document"]
                    for item in results
                ]
            )
        )

        return {
            "answer": answer,
            "sources": unique_sources
        }

    # ----------------------------------------
    # Summarize Document
    # ----------------------------------------
    def summarize_document(
        self,
        document_name
    ):
        print("Requested document:", document_name)

        for meta in self.vector_store.metadata:
            print("Stored document:", meta["document"])
        relevant_chunks = []

        for i, meta in enumerate(
            self.vector_store.metadata
        ):

            if (
                meta["document"]
                == document_name
            ):

                relevant_chunks.append(
                    self.vector_store.text_chunks[i]
                )

        if len(relevant_chunks) == 0:

            return "Document not found."

        context = "\n".join(
            relevant_chunks[:20]
        )

        prompt = f"""
Summarize this document.

Include:
- Purpose
- Education
- Skills
- Projects
- Certifications
- Important details

DOCUMENT:

{context}
"""

        try:

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            return (
                response
                .choices[0]
                .message
                .content
            )

        except Exception as e:

            return (
                f"Groq Error: {str(e)}"
            )

    # ----------------------------------------
    # Extract Profile
    # ----------------------------------------
    def extract_profile(self):

        context = "\n".join(
            self.vector_store.text_chunks[:50]
        )

        prompt = f"""
Create a structured profile from the uploaded documents.

Extract:

- Full Name
- Email
- Phone Number
- Education
- Skills
- Projects
- Experience
- Certifications
- CGPA
- Achievements

DOCUMENTS:

{context}
"""

        try:

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            return (
                response
                .choices[0]
                .message
                .content
            )

        except Exception as e:

            return (
                f"Groq Error: {str(e)}"
            )