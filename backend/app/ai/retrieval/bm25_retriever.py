import math
import re
from typing import Any, Dict, List


class BM25Retriever:
    """Okapi BM25 Sparse Keyword Ranker for Memory Text Retrieval.
    
    Provides exact keyword and proper-noun token matching to complement dense vector embeddings.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def _tokenize(self, text: str) -> List[str]:
        return [word.lower() for word in re.findall(r"\w+", text)]

    def rank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks candidate memory documents against the query using Okapi BM25 scoring."""
        if not documents or not query:
            return documents

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return documents

        doc_tokens_list = [
            self._tokenize(doc["memory"].summary if hasattr(doc.get("memory"), "summary") else str(doc.get("memory", "")))
            for doc in documents
        ]

        num_docs = len(documents)
        if num_docs == 0:
            return documents

        doc_lengths = [len(tokens) for tokens in doc_tokens_list]
        avg_doc_len = sum(doc_lengths) / num_docs if num_docs > 0 else 1.0

        # Calculate Inverse Document Frequency (IDF) for query terms
        idf = {}
        for token in set(query_tokens):
            n_q = sum(1 for doc_tokens in doc_tokens_list if token in doc_tokens)
            # Standard BM25 IDF formula with smoothing
            idf[token] = math.log((num_docs - n_q + 0.5) / (n_q + 0.5) + 1.0)

        # Compute BM25 scores
        scored_documents = []
        for doc, doc_tokens, doc_len in zip(documents, doc_tokens_list, doc_lengths):
            score = 0.0
            term_freqs = {}
            for t in doc_tokens:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            for q_term in query_tokens:
                if q_term in term_freqs:
                    f_q = term_freqs[q_term]
                    numerator = idf.get(q_term, 0.0) * f_q * (self.k1 + 1)
                    denominator = f_q + self.k1 * (1 - self.b + self.b * (doc_len / (avg_doc_len or 1.0)))
                    score += numerator / (denominator or 1.0)

            doc_copy = dict(doc)
            doc_copy["bm25_score"] = round(score, 4)
            scored_documents.append(doc_copy)

        # Sort documents descending by BM25 score
        scored_documents.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_documents
