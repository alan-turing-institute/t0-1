import logging
import os
from dataclasses import dataclass
from pathlib import Path

from langchain.storage import InMemoryStore, LocalFileStore, create_kv_docstore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters.base import TextSplitter
from t0_001.query_vector_store.build_index import (
    VectorStoreConfig,
    load_conditions_jsonl,
    setup_embedding_model,
    setup_text_splitter,
)
from t0_001.query_vector_store.custom_parent_document_retriever import (
    CustomParentDocumentRetriever,
)
from t0_001.query_vector_store.utils import remove_saved_directory


@dataclass
class RetrieverConfig(VectorStoreConfig):
    local_file_store: str | Path | None
    search_type: str
    k: int
    search_kwargs: dict


DEFAULT_RETRIEVER_CONFIG = RetrieverConfig(
    embedding_model_name="sentence-transformers/all-mpnet-base-v2",
    chunk_overlap=50,
    db_choice="chroma",
    persist_directory=None,
    local_file_store=None,
    search_type="similarity",
    k=4,
    search_kwargs={},
)


def create_parent_doc_retriever(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
) -> CustomParentDocumentRetriever:
    """
    Create a retriever with the specified conditions folder and configuration.
    This function loads the conditions from the specified folder,
    sets up the embedding model and text splitter, and creates a retriever
    using a custom ParentDocumentRetrieverCreator class that can allow
    for returning the scores.

    Parameters
    ----------
    conditions_file : str
        The file containing the conditions to be indexed.
    config : RetrieverConfig, optional
        Configuration object containing parameters for the retriever which
        includes the embedding model name, chunk overlap, database choice,
        persistence directory, local file store, search type, number of
        results to return, and search keyword arguments. Default is
        DEFAULT_RETRIEVER_CONFIG.

    Returns
    -------
    CustomParentDocumentRetriever
        The created retriever instance.
    """
    logging.info(f"Creating retriever with {config.db_choice} database...")
    conditions = load_conditions_jsonl(conditions_file)
    embedding_model = setup_embedding_model(config.embedding_model_name)
    text_splitter = setup_text_splitter(
        config.embedding_model_name, config.chunk_overlap
    )
    retriever_creator = ParentDocumentRetrieverCreator(
        embedding_model=embedding_model,
        text_splitter=text_splitter,
    )
    retriever = retriever_creator.create_retriever(
        documents=list(conditions.values()),
        metadatas=[{"source": k} for k in conditions.keys()],
        config=config,
    )

    return retriever


def load_parent_doc_retriever(
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    trust_source: bool = False,
) -> CustomParentDocumentRetriever:
    """
    Load the retriever with the specified configuration.

    Parameters
    ----------
    config : RetrieverConfig, optional
        Configuration object containing parameters for the retriever which
        includes the embedding model name, chunk overlap, database choice,
        persistence directory, local file store, search type, number of
        results to return, and search keyword arguments. Default is
        DEFAULT_RETRIEVER_CONFIG.
    trust_source : bool, optional
        If True, trust the source of the data index. This is needed for loading in FAISS databases.
        Default is False.

    Returns
    -------
    CustomParentDocumentRetriever
        The loaded retriever instance.
    """
    logging.info(
        f"Loading retriever with {config.db_choice} database at {config.persist_directory} and {config.local_file_store}..."
    )
    embedding_model = setup_embedding_model(config.embedding_model_name)
    text_splitter = setup_text_splitter(
        config.embedding_model_name, config.chunk_overlap
    )
    retriever_creator = ParentDocumentRetrieverCreator(
        embedding_model=embedding_model,
        text_splitter=text_splitter,
    )
    retriever = retriever_creator.load_retriever(
        config=config,
        trust_source=trust_source,
    )

    return retriever


def get_parent_doc_retriever(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
) -> CustomParentDocumentRetriever:
    """
    Get the retriever with the specified conditions folder and configuration.
    This function checks if the retriever already exists in the specified
    persist directory. If it does, it loads the retriever from there.
    If it doesn't exist or if force_create is True, it creates a new retriever.

    Parameters
    ----------
    conditions_file : str
        The file containing the conditions to be indexed.
    config : RetrieverConfig, optional
        Configuration object containing parameters for the retriever which
        includes the embedding model name, chunk overlap, database choice,
        persistence directory, local file store, search type, number of
        results to return, and search keyword arguments. Default is
        DEFAULT_RETRIEVER_CONFIG.
    force_create : bool, optional
        If True, force the creation of a new retriever even if one already exists.
        Default is False.
    trust_source : bool, optional
        If True, trust the source of the data index. This is needed for loading in FAISS databases.
        Default is False.
    """
    if (
        not force_create
        and config.persist_directory is not None
        and config.local_file_store is not None
        and os.path.exists(config.persist_directory)
        and os.path.exists(config.local_file_store)
    ):
        # only load if force_create=True, persist_directory and local_file_store
        # are passed and the directories exist
        retriever = load_parent_doc_retriever(
            config=config,
            trust_source=trust_source,
        )
    else:
        remove_saved_directory(config.persist_directory, "persist_directory")
        remove_saved_directory(config.local_file_store, "local_file_store")

        retriever = create_parent_doc_retriever(
            conditions_file=conditions_file,
            config=config,
        )

    return retriever


class ParentDocumentRetrieverCreator:
    def __init__(
        self,
        embedding_model: Embeddings,
        text_splitter: TextSplitter | None,
    ):
        """
        Initialise the ParentDocumentRetrieverCreator with the specified embedding model and text splitter.

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

    def create_retriever(
        self,
        documents: list[str],
        metadatas: list[dict[str, str]] = None,
        config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    ) -> CustomParentDocumentRetriever:
        """
        Create a retriever with the specified documents and metadata.

        Parameters
        ----------
        documents : list[str]
            A list of documents to index.
        metadatas : list[dict[str, str]], optional
            A list of metadata dictionaries corresponding to the documents.
            Each dictionary should contain metadata for a single document.
            If not provided, an empty list will be used.
        config : RetrieverConfig, optional
            Configuration object containing parameters for the retriever.
            If not provided, default values will be used.

        Returns
        -------
        CustomParentDocumentRetriever
            The created retriever instance.

        Raises
        -------
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

        logging.info(f"Creating retriever with {config.db_choice} database...")
        if config.persist_directory is not None:
            logging.info(
                f"After creation, the index will be persisted to '{config.persist_directory}'"
            )
        logging.info(f"Number of documents: {len(documents)}")
        logging.info("Creating documents...")
        self.documents: list[Document] = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(documents, metadatas)
        ]

        if config.local_file_store is None:
            store = InMemoryStore()
        else:
            fs = LocalFileStore(config.local_file_store)
            store = create_kv_docstore(fs)

        self.db_choice: str = config.db_choice
        if self.db_choice == "chroma":
            from langchain_chroma import Chroma

            if config.persist_directory is not None:
                logging.info(
                    f"Persisting Chroma database to '{config.persist_directory}'"
                )

            vectorstore = Chroma(
                collection_name="full_documents",
                embedding_function=self.embedding_model,
                persist_directory=config.persist_directory,
            )
        elif self.db_choice == "faiss":
            from faiss import IndexFlatL2
            from langchain_community.docstore.in_memory import InMemoryDocstore
            from langchain_community.vectorstores import FAISS

            vectorstore = FAISS(
                embedding_function=self.embedding_model,
                index=IndexFlatL2(len(self.embedding_model.embed_query("d"))),
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_choice}")

        retriever = CustomParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=self.text_splitter,
            search_type=config.search_type,
            search_kwargs=config.search_kwargs | {"k": config.k},
        )

        retriever.add_documents(self.documents)

        if self.db_choice == "faiss" and config.persist_directory is not None:
            logging.info(f"Persisting FAISS database to '{config.persist_directory}'")
            retriever.vectorstore.save_local(folder_path=config.persist_directory)

        return retriever

    def load_retriever(
        self,
        config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
        trust_source: bool = False,
    ) -> CustomParentDocumentRetriever:
        """
        Load a retriever from the specified configuration.

        Parameters
        ----------
        config : RetrieverConfig, optional
            Configuration object containing parameters for the retriever.
        trust_source : bool
            If True, trust the source of the data index. This is needed for loading in FAISS databases.
            Default is False.

        Returns
        -------
        CustomParentDocumentRetriever
            The loaded retriever instance.

        Raises
        ------
        ValueError
            If the persist directory is not specified in the config.
            If the local file store is not specified in the config.
            If the index has not been created yet.
            If the specified database type is not supported.
        """
        if config.persist_directory is None:
            raise ValueError(
                "Persist directory must be specified in the config to load the vector store."
            )
        if config.local_file_store is None:
            raise ValueError(
                "Local file store must be specified in the config to load the retriever."
            )

        self.db_choice: str = config.db_choice
        if self.db_choice == "chroma":
            from langchain_chroma import Chroma

            logging.info(f"Loading Chroma database from '{config.persist_directory}'")
            vectorstore = Chroma(
                collection_name="full_documents",
                embedding_function=self.embedding_model,
                persist_directory=config.persist_directory,
            )
        elif self.db_choice == "faiss":
            from langchain_community.vectorstores import FAISS

            logging.info(f"Loading FAISS database from '{config.persist_directory}'")
            vectorstore = FAISS.load_local(
                folder_path=config.persist_directory,
                embeddings=self.embedding_model,
                allow_dangerous_deserialization=trust_source,
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_choice}")

        fs = LocalFileStore(config.local_file_store)
        store = create_kv_docstore(fs)

        retriever = CustomParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=self.text_splitter,
            search_type=config.search_type,
            search_kwargs=config.search_kwargs | {"k": config.k},
        )

        return retriever
