import logging
from collections import defaultdict
from typing import Any, List, Optional

from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers.multi_vector import SearchType
from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from tqdm import tqdm


class CustomParentDocumentRetriever(ParentDocumentRetriever):
    """
    Custom Retriever class to propagate similarity scores through the
    MultiVectorRetriever (as described in
    https://python.langchain.com/v0.3/docs/how_to/add_scores_retriever/).
    """

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """
        Get documents relevant to a query.
        """
        if self.search_type == SearchType.mmr:
            sub_docs = self.vectorstore.max_marginal_relevance_search(
                query, **self.search_kwargs
            )

            # We do this to maintain the order of the ids that are returned
            ids = []
            for d in sub_docs:
                if self.id_key in d.metadata and d.metadata[self.id_key] not in ids:
                    ids.append(d.metadata[self.id_key])
            docs = self.docstore.mget(ids)

            return [d for d in docs if d is not None]
        elif self.search_type == SearchType.similarity_score_threshold:
            sub_docs = self.vectorstore.similarity_search_with_relevance_scores(
                query, **self.search_kwargs
            )
        else:
            sub_docs = self.vectorstore.similarity_search_with_score(
                query, **self.search_kwargs
            )

        # Map doc_ids to list of sub-documents, adding scores to metadata
        id_to_doc = defaultdict(list)
        for doc, score in sub_docs:
            doc_id = doc.metadata.get("doc_id")
            if doc_id:
                doc.metadata["score"] = float(score)
                id_to_doc[doc_id].append(doc)

        # Fetch documents corresponding to doc_ids, retaining sub_docs in metadata
        docs = []
        for _id, sub_docs in id_to_doc.items():
            docstore_docs = self.docstore.mget([_id])
            if docstore_docs:
                if doc := docstore_docs[0]:
                    doc.metadata["sub_docs"] = sub_docs
                    docs.append(doc)

        return docs

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Asynchronously get documents relevant to a query.
        """
        if self.search_type == SearchType.mmr:
            sub_docs = await self.vectorstore.amax_marginal_relevance_search(
                query, **self.search_kwargs
            )

            # We do this to maintain the order of the ids that are returned
            ids = []
            for d in sub_docs:
                if self.id_key in d.metadata and d.metadata[self.id_key] not in ids:
                    ids.append(d.metadata[self.id_key])
            docs = await self.docstore.amget(ids)

            return [d for d in docs if d is not None]
        elif self.search_type == SearchType.similarity_score_threshold:
            sub_docs = await self.vectorstore.asimilarity_search_with_relevance_scores(
                query, **self.search_kwargs
            )
        else:
            sub_docs = await self.vectorstore.asimilarity_search_with_score(
                query, **self.search_kwargs
            )

        # Map doc_ids to list of sub-documents, adding scores to metadata
        id_to_doc = defaultdict(list)
        for doc, score in sub_docs:
            doc_id = doc.metadata.get("doc_id")
            if doc_id:
                doc.metadata["score"] = float(score)
                id_to_doc[doc_id].append(doc)

        # Fetch documents corresponding to doc_ids, retaining sub_docs in metadata
        docs = []
        for _id, sub_docs in id_to_doc.items():
            docstore_docs = await self.docstore.amget([_id])
            if docstore_docs:
                if doc := docstore_docs[0]:
                    doc.metadata["sub_docs"] = sub_docs
                    docs.append(doc)

        return docs

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
        add_to_docstore: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Adds documents to the docstore and vectorstores in batches of 2048.
        """
        logging.info("Adding documents to vectorstore and docstore...")
        logging.info("Splitting documents for adding...")

        docs, full_docs = self._split_docs_for_adding(documents, ids, add_to_docstore)

        logging.info(f"Number of documents created after splitting: {len(docs)}")
        logging.info(f"Number of full documents: {len(full_docs)}")

        def split_list(input_list, batch_size):
            for i in range(0, len(input_list), batch_size):
                yield input_list[i : i + batch_size]

        split_docs_chunked = split_list(docs, batch_size=2048)
        for docs_chunk in tqdm(
            split_docs_chunked,
            desc="Adding documents in batches of 2048",
            total=len(docs) // 2048,
        ):
            self.vectorstore.add_documents(docs_chunk, **kwargs)

        logging.info("Adding full documents to docstore...")

        if add_to_docstore:
            self.docstore.mset(full_docs)
