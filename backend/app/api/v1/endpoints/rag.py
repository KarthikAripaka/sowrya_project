from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from backend.app.schemas.schemas import RAGQueryRequest, RAGQueryResponse, EvidenceSourceOut
from backend.app.ai.rag.rag_pipeline import MedicalRAGPipeline

router = APIRouter()
rag_pipeline = MedicalRAGPipeline()

@router.post("/query", response_model=RAGQueryResponse)
def query_medical_rag(req: RAGQueryRequest):
    """
    Query the verified medical knowledge base (PubMed, MedlinePlus, WHO, RadiologyInfo).
    Returns ranked evidence excerpts with source URLs and relevance scores.
    """
    results = rag_pipeline.retrieve_evidence(
        query=req.query,
        top_k=req.top_k,
        category=req.category
    )
    sources = [EvidenceSourceOut(**r) for r in results]
    return RAGQueryResponse(
        query=req.query,
        sources=sources,
        retrieved_count=len(sources)
    )

@router.get("/sources")
def get_curated_sources():
    """List all trusted medical knowledge sources and categories."""
    categories = set()
    sources = set()
    for doc in rag_pipeline.documents:
        categories.add(doc.get("category", "General"))
        sources.add(doc.get("source_org", "Medical Organization"))

    return {
        "total_documents": len(rag_pipeline.documents),
        "source_organizations": sorted(list(sources)),
        "categories": sorted(list(categories)),
        "verification_statement": "All documents sourced from MedlinePlus (NIH), World Health Organization (WHO), and RadiologyInfo.org (RSNA/ACR)."
    }
