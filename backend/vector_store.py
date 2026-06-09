import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class VectorStore:

    def __init__(
        self,
        embedding_model="all-MiniLM-L6-v2"
    ):
        """
        Initialize embedding model.
        """

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            embedding_model
        )

        self.text_chunks = []
        self.metadata = []

        self.index = None

    # ----------------------------------------
    # Split Document into Chunks
    # ----------------------------------------
    def split_text(
        self,
        text,
        chunk_size=500,
        chunk_overlap=100
    ):
        """
        Split large document into chunks.
        """

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_text(text)

        return chunks

    # ----------------------------------------
    # Create Embeddings
    # ----------------------------------------
    def create_embeddings(self, chunks):
        """
        Convert chunks into vectors.
        """

        embeddings = self.embedding_model.encode(
            chunks,
            show_progress_bar=True
        )

        return np.array(
            embeddings,
            dtype=np.float32
        )

    # ----------------------------------------
    # Add Document
    # ----------------------------------------
    def add_document(
        self,
        text,
        document_name
    ):
        """
        Add document to vector store.
        """

        chunks = self.split_text(text)

        if len(chunks) == 0:
            raise Exception(
                "No content found in document."
            )

        embeddings = self.create_embeddings(
            chunks
        )

        dimension = embeddings.shape[1]

        if self.index is None:

            self.index = faiss.IndexFlatL2(
                dimension
            )

        self.index.add(embeddings)

        for chunk in chunks:

            self.text_chunks.append(chunk)

            self.metadata.append(
                {
                    "document": document_name
                }
            )

        print(
            f"Added {len(chunks)} chunks "
            f"from {document_name}"
        )

    # ----------------------------------------
    # Search Similar Chunks
    # ----------------------------------------
    def search(
        self,
        query,
        top_k=5
    ):
        """
        Retrieve relevant chunks.
        """

        if self.index is None:

            return []

        query_embedding = self.embedding_model.encode(
            [query]
        )

        query_embedding = np.array(
            query_embedding,
            dtype=np.float32
        )

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for idx in indices[0]:

            if idx < len(self.text_chunks):

                results.append(
                    {
                        "text": self.text_chunks[idx],
                        "document":
                        self.metadata[idx]["document"]
                    }
                )

        return results

    # ----------------------------------------
    # Save Index
    # ----------------------------------------
    def save(
        self,
        folder="vector_db"
    ):
        """
        Save vector database.
        """

        os.makedirs(
            folder,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            os.path.join(
                folder,
                "faiss.index"
            )
        )

        with open(
            os.path.join(
                folder,
                "chunks.pkl"
            ),
            "wb"
        ) as f:

            pickle.dump(
                {
                    "chunks": self.text_chunks,
                    "metadata": self.metadata
                },
                f
            )

        print("Vector DB saved.")

    # ----------------------------------------
    # Load Index
    # ----------------------------------------
    def load(
        self,
        folder="vector_db"
    ):
        """
        Load saved vector database.
        """

        index_path = os.path.join(
            folder,
            "faiss.index"
        )

        chunks_path = os.path.join(
            folder,
            "chunks.pkl"
        )

        if (
            not os.path.exists(index_path)
            or
            not os.path.exists(chunks_path)
        ):
            return False

        self.index = faiss.read_index(
            index_path
        )

        with open(
            chunks_path,
            "rb"
        ) as f:

            data = pickle.load(f)

            self.text_chunks = data["chunks"]
            self.metadata = data["metadata"]

        print("Vector DB loaded.")

        return True
    def clear(self):
        self.text_chunks = []
        self.metadata = []

        dimension = 384

        self.index = faiss.IndexFlatL2(dimension)

        self.save()