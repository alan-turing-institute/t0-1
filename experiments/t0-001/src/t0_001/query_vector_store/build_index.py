import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from langchain_text_splitters.base import TextSplitter


def setup_embedding_model(
    model_name: str = "sentence-transformers/all-mpnet-base-v2",
) -> HuggingFaceEmbeddings:
    """
    Set up the embedding model using HuggingFaceEmbeddings.

    Parameters
    ----------
    model_name : str
        The name of the model to use. Default is "sentence-transformers/all-mpnet-base-v2".

    Returns
    -------
    Embeddings
        An instance of HuggingFaceEmbeddings.
    """
    logging.info(f"Setting up embedding model: {model_name}")
    logging.info("Loading embeddding model...")
    return HuggingFaceEmbeddings(model_name=model_name)


def setup_text_splitter(
    model_name: str = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: int = 50,
) -> SentenceTransformersTokenTextSplitter:
    """
    Set up the text splitter using SentenceTransformersTokenTextSplitter.

    Parameters
    ----------
    model_name : str
        The name of the model to use. Default is "sentence-transformers/all-mpnet-base-v2".

    Returns
    -------
    TextSplitter
        An instance of SentenceTransformersTokenTextSplitter.
    """
    logging.info(f"Setting up text splitter with model: {model_name}")
    logging.info("Loading text splitter...")
    return SentenceTransformersTokenTextSplitter(
        model_name=model_name,
        chunk_overlap=chunk_overlap,
    )


class DataIndexCreator:
    def __init__(
        self,
        embedding_model: Embeddings,
        text_splitter: TextSplitter,
    ):
        self.embedding_model: Embeddings = embedding_model
        self.text_splitter: TextSplitter = text_splitter
        self.documents: list[Document] = []
        self.db_choice: str | None = None
        self.db: VectorStore | None = None

    def create_index(
        self,
        db: str,
        documents: list[str],
        metadatas: list[dict[str, str]] = None,
    ):
        """
        Create an index using the specified database and documents.

        Parameters
        ----------
        db : str
            The type of database to use. Supported options are "chroma" and "faiss".
        documents : list[str]
            A list of documents to index.
        metadatas : list[dict[str, str]], optional
            A list of metadata dictionaries corresponding to the documents.
            Each dictionary should contain metadata for a single document.
            If not provided, an empty list will be used.

        Raises
        ------
        ValueError
            If the number of documents and metadata do not match.
            If the specified database type is not supported.
        """
        if metadatas is None:
            metadatas = [{}] * len(documents)
        if len(documents) != len(metadatas):
            raise ValueError("The number of documents and metadata must be the same.")
        if db not in ["chroma", "faiss"]:
            raise ValueError(
                f"Unsupported database type: {db}. Supported options are 'chroma' and 'faiss'."
            )

        logging.info(f"Creating index with {db} database")
        logging.info(f"Number of documents: {len(documents)}")
        logging.info("Creating documents...")
        self.documents: list[Document] = self.text_splitter.create_documents(
            texts=documents, metadatas=metadatas
        )
        logging.info(
            f"Number of documents created after splitting: {len(self.documents)}"
        )

        logging.info("Creating vector store...")
        self.db_choice: str = db
        if db == "chroma":
            from langchain_chroma import Chroma

            self.db: VectorStore = Chroma.from_documents(
                self.documents, self.embedding_model
            )
        elif db == "faiss":
            from langchain_community.vectorstores import FAISS

            self.db: VectorStore = FAISS.from_documents(
                self.documents, self.embedding_model
            )
        else:
            raise ValueError(f"Unsupported database type: {db}")

        logging.info("Index created successfully!")
        return self.db

    def save_index(self, index_path: str | Path):
        """
        Save the index to the specified path.

        Parameters
        ----------
        index_path : str | Path
            The path where the index should be saved.

        Raises
        ------
        ValueError
            If the index has not been created yet.
        """
        if not self.db:
            raise ValueError("Index not created. Please create the index first.")
        if self.db_choice == "chroma":
            self.db.save(index_path)
        elif self.db_choice == "faiss":
            self.db.save_local(index_path)
