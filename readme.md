 Introduction

This project implements a structured Retrieval-Augmented Generation (RAG) system designed for multi-year analysis of corporate annual reports, with a focus on analytical correctness rather than conversational breadth. Instead of querying raw PDFs at runtime, the system ingests annual reports offline, distills them into semantically coherent idea units, and enforces strict metadata constraints—such as financial year, MD&A section, and business segment—during retrieval. This design prevents cross-year and cross-section contamination, a common failure mode in naïve document Q&A systems, and makes the system suitable for fundamental financial analysis across reporting periods. The current implementation demonstrates year-isolated retrieval across multiple annual reports and provides a foundation for scalable, audit-friendly analysis of corporate disclosures.

┌──────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                            │
│                                                              │
│   • Annual Report PDFs (FY2021–FY2025)                        │
│   • Source: BSE / NSE / Company Website                      │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                  OFFLINE INGESTION PIPELINE                  │
│        (Executed once per report, not at query time)         │
│                                                              │
│  1. PDF Text Extraction                                      │
│     • Page-range based extraction (MD&A only)                │
│     • Deterministic, reproducible                             │
│                                                              │
│  2. Section Segmentation                                     │
│     • SOCIO-ECONOMIC ENVIRONMENT                              │
│     • FINANCIAL PERFORMANCE                                  │
│     • COST, MARGIN & INFLATION MANAGEMENT                     │
│     • SEGMENT-WISE STRATEGIC FOCUS                            │
│     • etc.                                                    │
│                                                              │
│  3. Paragraph Normalisation                                  │
│     • Clean text                                              │
│     • Remove boilerplate                                      │
│     • Preserve semantic boundaries                            │
│                                                              │
│  4. Idea Unit Generation (AI-assisted, constrained)           │
│     • Paragraph → 1–N idea units                              │
│     • No interpretation or forecasting                        │
│     • Explicit bucket & year tagging                          │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                  STRUCTURED KNOWLEDGE STORE                  │
│                                                              │
│   Idea Units (JSON / CSV / DB)                                │
│                                                              │
│   Each record contains:                                      │
│     • Text (idea unit)                                        │
│     • Company                                                 │
│     • Financial Year                                          │
│     • MD&A Section / Bucket                                   │
│     • Business Segment                                        │
│     • Source Page Range                                       │
│                                                              │
│   (No embeddings yet)                                         │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                   EMBEDDING LAYER (OFFLINE)                  │
│                                                              │
│   • Model: text-embedding-3-large (LOCKED)                   │
│   • One embedding per idea unit                               │
│   • Same model used for queries                               │
│                                                              │
│   Output:                                                     │
│     Idea Unit → Vector                                        │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                    VECTOR STORE                              │
│                                                              │
│   • Stores:                                                   │
│       - Embedding vector                                      │
│       - Metadata (year, bucket, segment, etc.)                │
│                                                              │
│   • Enforces:                                                 │
│       - No cross-year mixing                                  │
│       - No cross-bucket leakage                               │
│                                                              │
│   (Current: SimpleVectorStore                                 │
│    Later: FAISS / persistent store)                           │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                   QUERY-TIME RETRIEVAL                        │
│                                                              │
│   User Question                                               │
│        ↓                                                     │
│   Query Embedding (same embedding model)                      │
│        ↓                                                     │
│   Metadata Filtering (year, bucket, segment)                  │
│        ↓                                                     │
│   Similarity Ranking (cosine / equivalent)                    │
│        ↓                                                     │
│   Top-K Idea Units                                            │
└───────────────┬──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                ANSWER SYNTHESIS (OPTIONAL)                   │
│                                                              │
│   • LLM receives ONLY retrieved idea units                    │
│   • Generates structured, year-aware answers                  │
│   • No access to raw PDFs                                     │
│                                                              │
│   (This layer is intentionally decoupled)                     │
└──────────────────────────────────────────────────────────────┘