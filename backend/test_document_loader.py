from document_loader import DocumentLoader

text = DocumentLoader.load_document(
    "../uploads/sample.pdf"
)

print(text[:1000])