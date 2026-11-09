import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from backend.app.core.config import settings
from backend.app.ai.embeddings.biomedical_embeddings import CloudEmbeddingProvider

logger = logging.getLogger(__name__)

class MedicalRAGPipeline:
    """
    Evidence-Based Medical Retrieval-Augmented Generation Engine.
    Retrieves peer-reviewed and verified clinical knowledge from MedlinePlus,
    PubMed, WHO, and RadiologyInfo.org.
    
    100% Cloud-Architecture Compatible:
    - Zero local GPU or heavy PyTorch downloads.
    - Uses CloudEmbeddingProvider for vectorization.
    - Ready for PostgreSQL pgvector storage.
    """

    def __init__(self, knowledge_dir: str = "./knowledge_base/curated"):
        self.knowledge_dir = knowledge_dir
        self.embedder = CloudEmbeddingProvider(
            provider=settings.EMBEDDING_PROVIDER,
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        self.documents: List[Dict[str, Any]] = []
        self.doc_embeddings: Optional[np.ndarray] = None
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load curated JSON medical knowledge files and compute embeddings."""
        docs = []
        if os.path.exists(self.knowledge_dir):
            for fname in os.listdir(self.knowledge_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.knowledge_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                docs.extend(data)
                    except Exception as e:
                        logger.warning(f"Error loading knowledge file {fname}: {e}")

        self.documents = docs
        if self.documents:
            corpus_texts = [
                f"{d.get('title', '')} {d.get('topic', '')} {d.get('subtopic', '')} {' '.join(d.get('keywords', []))} {d.get('content', '')}"
                for d in self.documents
            ]
            raw_embeddings = self.embedder.embed_documents(corpus_texts)
            self.doc_embeddings = np.array(raw_embeddings, dtype=np.float32)

    def retrieve_evidence(
        self, query: str, top_k: int = 4, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant evidence documents for a given clinical query.
        Returns ranked list of verified sources with relevance scores.
        """
        if not self.documents or self.doc_embeddings is None:
            return []

        query_vec = np.array(self.embedder.embed_query(query), dtype=np.float32)
        norm_q = np.linalg.norm(query_vec)
        if norm_q > 0:
            query_vec = query_vec / norm_q

        # Cosine similarity calculation
        norms_d = np.linalg.norm(self.doc_embeddings, axis=1, keepdims=True)
        norms_d = np.where(norms_d == 0, 1e-10, norms_d)
        normed_docs = self.doc_embeddings / norms_d

        similarities = np.dot(normed_docs, query_vec)

        # Keyword boost for direct test name matches
        query_lower = query.lower()
        scored_docs = []
        for idx, doc in enumerate(self.documents):
            sim = float(similarities[idx])
            
            # Category filter if provided
            if category and doc.get("category", "").lower() != category.lower():
                continue

            # Term overlap boost
            keywords = [k.lower() for k in doc.get("keywords", [])]
            subtopic = doc.get("subtopic", "").lower()
            topic = doc.get("topic", "").lower()
            
            boost = 0.0
            if any(k in query_lower for k in keywords):
                boost += 0.15
            if subtopic in query_lower or topic in query_lower:
                boost += 0.20

            final_score = min(max(sim + boost, 0.0), 1.0)
            if final_score > 0.10:
                scored_docs.append((final_score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "source_org": doc.get("source_org", "Official Medical Reference"),
                "source_title": doc.get("title", "Clinical Reference Document"),
                "source_url": doc.get("source_url", "https://medlineplus.gov/"),
                "excerpt": doc.get("content", "")[:350] + "...",
                "relevance_score": round(score, 3),
                "category": doc.get("category", "General"),
                "clinical_significance": doc.get("clinical_significance", "")
            })

        return results

    def retrieve_for_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Construct multi-faceted clinical queries based on extracted entities
        (especially out-of-range lab values, diseases, or symptoms).
        """
        queries = []
        for ent in entities:
            text = ent.get("text", "")
            flag = ent.get("flag")
            if flag in ["LOW", "HIGH"]:
                queries.append(f"{flag.lower()} {text} reference range cause")
            elif ent.get("entity_type") in ["lab_test", "disease"]:
                queries.append(f"{text} clinical test meaning")

        if not queries:
            queries = ["Complete blood count comprehensive metabolic panel general"]

        evidence_pool = []
        seen_titles = set()

        for q in queries[:5]:
            hits = self.retrieve_evidence(q, top_k=2)
            for hit in hits:
                title = hit["source_title"]
                if title not in seen_titles:
                    seen_titles.add(title)
                    evidence_pool.append(hit)

        evidence_pool.sort(key=lambda x: x["relevance_score"], reverse=True)
        return evidence_pool[:6]
