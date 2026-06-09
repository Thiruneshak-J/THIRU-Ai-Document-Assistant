from vector_store import VectorStore
from rag_engine import RAGEngine

vs = VectorStore()

sample_text = """
Name: Thiru

Degree:
B.E Computer Science

Skills:
Java
Python
HTML
CSS

CGPA:
8.2

Project:
AI Document Assistant
"""

vs.add_document(
    sample_text,
    "resume.txt"
)

rag = RAGEngine(vs)

result = rag.ask(
    "What is the CGPA?"
)

print(result)