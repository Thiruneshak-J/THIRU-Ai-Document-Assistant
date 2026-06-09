import os
from pypdf import PdfReader
from docx import Document


class DocumentLoader:

    @staticmethod
    def load_pdf(file_path):
        """
        Read PDF and return extracted text.
        """
        text = ""

        try:
            reader = PdfReader(file_path)

            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()

                if page_text:
                    text += f"\n\n--- PAGE {page_num + 1} ---\n"
                    text += page_text

        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

        return text

    @staticmethod
    def load_docx(file_path):
        """
        Read DOCX and return extracted text.
        """
        text = ""

        try:
            doc = Document(file_path)

            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + "\n"

        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

        return text

    @staticmethod
    def load_txt(file_path):
        """
        Read TXT and return extracted text.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()

        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")

    @staticmethod
    def load_document(file_path):
        """
        Automatically detect file type and load content.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            return DocumentLoader.load_pdf(file_path)

        elif extension == ".docx":
            return DocumentLoader.load_docx(file_path)

        elif extension == ".txt":
            return DocumentLoader.load_txt(file_path)

        else:
            raise ValueError(
                "Unsupported file format. "
                "Supported formats: PDF, DOCX, TXT"
            )