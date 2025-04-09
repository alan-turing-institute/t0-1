from collections import defaultdict

from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers.multi_vector import SearchType
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document


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
