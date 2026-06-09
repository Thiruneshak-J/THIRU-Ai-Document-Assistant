from vector_store import VectorStore

sample_text = """
Thiru completed B.E Computer Science.

Skills:
Java
Python
HTML
CSS

CGPA: 8.2

Project:
AI Document Assistant
"""

vs = VectorStore()

vs.add_document(
    sample_text,
    "resume.txt"
)

results = vs.search(
    "What are the skills?"
)

print(results)