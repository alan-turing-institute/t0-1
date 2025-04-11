import logging
import os
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from langchain_text_splitters.base import TextSplitter
from t0_001.query_vector_store.utils import load_conditions, remove_saved_directory


@dataclass
class VectorStoreConfig:
    embedding_model_name: str
    chunk_overlap: int
    db_choice: str
    persist_directory: str | Path | None


DEFAULT_VECTOR_STORE_CONFIG = VectorStoreConfig(
    embedding_model_name="sentence-transformers/all-mpnet-base-v2",
    chunk_overlap=50,
    db_choice="chroma",
    persist_directory=None,
)


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


def create_vector_store(
    conditions_folder: str,
    main_only: bool = True,
    config: VectorStoreConfig = DEFAULT_VECTOR_STORE_CONFIG,
) -> VectorStore:
    """
    Create a vector store using the specified database and conditions.
    This function loads the conditions from the specified folder,
    sets up the embedding model and text splitter, and creates the index.

    Parameters
    ----------
    conditions_folder : str
        The folder containing the conditions to be indexed.
    main_only : bool, optional
        If True, only the main conditions will be loaded. Default is True.
    config : VectorStoreConfig, optional
        The configuration for the vector store which includes the embedding model name,
        chunk overlap size, database choice, and persist directory.
        Default is DEFAULT_VECTOR_STORE_CONFIG.

    Returns
    -------
    VectorStore
        The created vector store instance.
    """
    logging.info(f"Creating vector store with {config.db_choice} database...")
    conditions = load_conditions(conditions_folder, main_only)
    embedding_model = setup_embedding_model(config.embedding_model_name)
    text_splitter = setup_text_splitter(
        config.embedding_model_name, config.chunk_overlap
    )
    index_creator = VectorStoreCreator(
        embedding_model=embedding_model,
        text_splitter=text_splitter,
    )
    index_creator.create_index(
        documents=list(conditions.values()),
        metadatas=[{"source": k} for k in conditions.keys()],
        config=config,
    )

    return index_creator.db


def load_vector_store(
    config: VectorStoreConfig = DEFAULT_VECTOR_STORE_CONFIG,
    trust_source: bool = False,
) -> VectorStore:
    """
    Load the vector store from the specified configuration.

    Parameters
    ----------
    config : VectorStoreConfig, optional
        The configuration for the vector store which includes the embedding model name,
        chunk overlap size, database choice, and persist directory.
        Default is DEFAULT_VECTOR_STORE_CONFIG.
    trust_source : bool, optional
        If True, trust the source of the data index. This is needed for loading in FAISS databases.
        Default is False.

    Returns
    -------
    VectorStore
        The loaded vector store instance.
    """
    logging.info(
        f"Loading vector store with {config.db_choice} database at '{config.persist_directory}'..."
    )
    embedding_model = setup_embedding_model(config.embedding_model_name)
    index_creator = VectorStoreCreator(embedding_model, text_splitter=None)
    index_creator.load_index(config=config, trust_source=trust_source)

    return index_creator.db


def get_vector_store(
    conditions_folder: str,
    main_only: bool = True,
    config: VectorStoreConfig = DEFAULT_VECTOR_STORE_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
) -> VectorStore:
    """
    Get the vector store from the specified conditions folder and configuration.
    This function checks if the vector store already exists in the specified
    persist directory. If it does, it loads the vector store from there.
    If it doesn't exist or if force_create is True, it creates a new vector store.

    Parameters
    ----------
    conditions_folder : str
        The folder containing the conditions to be indexed.
    main_only : bool, optional
        If True, only the main conditions will be loaded. Default is True.
    config : VectorStoreConfig, optional
        The configuration for the vector store which includes the embedding model name,
        chunk overlap size, database choice, and persist directory.
        Default is DEFAULT_VECTOR_STORE_CONFIG.
    force_create : bool, optional
        If True, force the creation of a new vector store even if it already exists.
        Default is False.
    trust_source : bool, optional
        If True, trust the source of the data index. This is needed for loading in FAISS databases.
        Default is False.

    Returns
    -------
    VectorStore | VectorStoreRetriever
        The vector store instance or the vector store retriever instance.
        If as_retriever is True, a VectorStoreRetriever instance will be returned.
        Otherwise, a VectorStore instance will be returned.
        If the vector store already exists, it will be loaded.
        If it doesn't exist or if force_create is True, a new vector store will be created.
    """
    if (
        not force_create
        and config.persist_directory is not None
        and os.path.exists(config.persist_directory)
    ):
        # only load if force_create=True, persist_directory is passed and the directory exists
        db = load_vector_store(
            config=config,
            trust_source=trust_source,
        )
    else:
        remove_saved_directory(config.persist_directory, "persist_directory")

        db = create_vector_store(
            conditions_folder=conditions_folder,
            main_only=main_only,
            config=config,
        )

    return db


class VectorStoreCreator:
    def __init__(
        self,
        embedding_model: Embeddings,
        text_splitter: TextSplitter | None,
    ):
        """
        Initialise the VectorStoreCreator with the specified embedding model and text splitter.

        Parameters
        ----------
        embedding_model : Embeddings
            The embedding model to use for creating the index.
        text_splitter : TextSplitter | None
            The text splitter to use for splitting the documents into chunks.
            If loading an existing index, this can be None.
        """
        self.embedding_model: Embeddings = embedding_model
        self.text_splitter: TextSplitter | None = text_splitter
        self.documents: list[Document] = []
        self.db_choice: str | None = None
        self.db: VectorStore | None = None

    def create_index(
        self,
        documents: list[str],
        metadatas: list[dict[str, str]] = None,
        config: VectorStoreConfig = DEFAULT_VECTOR_STORE_CONFIG,
    ) -> VectorStore:
        """
        Create an index using the specified database and documents.

        Parameters
        ----------
        documents : list[str]
            A list of documents to index.
        metadatas : list[dict[str, str]], optional
            A list of metadata dictionaries corresponding to the documents.
            Each dictionary should contain metadata for a single document.
            If not provided, an empty list will be used.
        config : VectorStoreConfig, optional
            The configuration for the vector store.

        Returns
        -------
        VectorStore
            The created vector store instance.

        Raises
        ------
        ValueError
            If the text splitter is not set.
            If the number of documents and metadata do not match.
            If the specified database type is not supported.
        """
        if self.text_splitter is None:
            raise ValueError("Text splitter is not set. Cannot create index.")
        if metadatas is None:
            metadatas = [{}] * len(documents)
        if len(documents) != len(metadatas):
            raise ValueError("The number of documents and metadata must be the same.")
        if config.db_choice not in ("chroma", "faiss"):
            raise ValueError(
                f"Unsupported database type: {config.db_choice}. Supported options are 'chroma' and 'faiss'."
            )

        logging.info(f"Creating index with {config.db_choice} database...")
        if config.persist_directory is not None:
            logging.info(
                f"After creation, the index will be persisted to '{config.persist_directory}'"
            )
        logging.info(f"Number of documents: {len(documents)}")
        logging.info("Creating documents...")
        self.documents: list[Document] = self.text_splitter.create_documents(
            texts=documents, metadatas=metadatas
        )
        logging.info(
            f"Number of documents created after splitting: {len(self.documents)}"
        )

        logging.info("Creating vector store...")
        self.db_choice: str = config.db_choice
        if self.db_choice == "chroma":
            from langchain_chroma import Chroma

            if config.persist_directory is not None:
                logging.info(
                    f"Persisting Chroma database to '{config.persist_directory}'"
                )

            self.db: VectorStore = Chroma.from_documents(
                self.documents,
                self.embedding_model,
                persist_directory=config.persist_directory,
            )
        elif self.db_choice == "faiss":
            from langchain_community.vectorstores import FAISS

            self.db: VectorStore = FAISS.from_documents(
                self.documents,
                self.embedding_model,
            )

            if config.persist_directory is not None:
                logging.info(
                    f"Persisting FAISS database to '{config.persist_directory}'"
                )
                self.db.save_local(folder_path=config.persist_directory)
        else:
            raise ValueError(f"Unsupported database type: {self.db_choice}")

        logging.info("Index created successfully!")
        return self.db

    def load_index(
        self,
        config: VectorStoreConfig = DEFAULT_VECTOR_STORE_CONFIG,
        trust_source: bool = False,
    ) -> VectorStore:
        """
        Load the index from a specified configuration.

        Parameters
        ----------
        config : VectorStoreConfig, optional
            The configuration for the vector store.
        trust_source : bool
            If True, trust the source of the data index. This is needed for loading in FAISS databases.
            Default is False.

        Raises
        ------
        ValueError
            If the persist directory is not specified in the config.
            If the index has not been created yet.
            If the specified database type is not supported.
        """
        if config.persist_directory is None:
            raise ValueError(
                "Persist directory must be specified in the config to load the vector store."
            )

        self.db_choice: str = config.db_choice
        if self.db_choice == "chroma":
            from langchain_chroma import Chroma

            logging.info(f"Loading Chroma database from '{config.persist_directory}'")
            self.db = Chroma(
                embedding_function=self.embedding_model,
                persist_directory=config.persist_directory,
            )
        elif self.db_choice == "faiss":
            from langchain_community.vectorstores import FAISS

            logging.info(f"Loading FAISS database from '{config.persist_directory}'")
            self.db = FAISS.load_local(
                folder_path=config.persist_directory,
                embeddings=self.embedding_model,
                allow_dangerous_deserialization=trust_source,
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_choice}")

        logging.info("Index loaded successfully!")
        return self.db
