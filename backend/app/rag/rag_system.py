"""
RAG (Retrieval-Augmented Generation) system for GreenForge AI.
Uses TF-IDF based retrieval with a local curated knowledge base.
Falls back gracefully when heavy ML dependencies are unavailable.
"""
import json
import math
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# ---- Knowledge Base Documents ----
KNOWLEDGE_BASE = [
    {
        "title": "Green Software Engineering Fundamentals",
        "source": "https://principles.green/",
        "category": "green_software",
        "content": (
            "Green Software Engineering is a discipline focused on building software applications that are "
            "carbon-efficient, energy-efficient, and hardware-efficient. The three core pillars are: "
            "(1) Carbon Efficiency — emit as little carbon as possible for a given unit of work; "
            "(2) Energy Efficiency — use as little energy as possible for the work performed; "
            "(3) Hardware Efficiency — use the least amount of embodied carbon (manufacturing) by maximizing "
            "hardware utilization and longevity. Green software practitioners also practice carbon awareness "
            "by shifting compute workloads to times or regions with cleaner grid electricity."
        )
    },
    {
        "title": "Software Carbon Intensity (SCI) Specification",
        "source": "https://sci-data.greensoftware.foundation/",
        "category": "carbon_intensity",
        "content": (
            "The Software Carbon Intensity (SCI) specification defines a methodology to calculate the carbon "
            "intensity of a software application. The formula is: SCI = ((E * I) + M) / R, where "
            "E = energy consumed by the software, I = marginal carbon intensity of electricity (gCO2e/kWh), "
            "M = embodied emissions (hardware manufacturing), R = a functional unit of the software. "
            "The SCI score cannot be gamed by purchasing carbon offsets — it measures operational and "
            "embodied emissions per unit of work. Lower SCI scores indicate greener software."
        )
    },
    {
        "title": "Energy-Aware Algorithm Design",
        "source": "https://greensoftware.foundation/",
        "category": "algorithms",
        "content": (
            "Algorithmic complexity directly impacts energy consumption. An O(n²) algorithm executing on "
            "1 million items performs 10^12 operations, while an O(n log n) alternative performs only ~20 million. "
            "This difference translates directly to CPU cycles, execution time, and energy consumption. "
            "Choosing efficient algorithms is one of the highest-leverage sustainability interventions. "
            "Key patterns to improve: replace nested loops with hash-based lookups (O(1) vs O(n)), "
            "use sorting + binary search instead of linear scans, cache expensive computations, "
            "and prefer lazy evaluation (generators) over eager list construction."
        )
    },
    {
        "title": "Green AI and ML Efficiency",
        "source": "https://arxiv.org/abs/1906.02629",
        "category": "green_ai",
        "content": (
            "Training and running large AI models can be energy-intensive. The paper 'Energy and Policy "
            "Considerations for Deep Learning in NLP' (Strubell et al., 2019) highlighted that training large "
            "NLP models can emit significant carbon. Practitioners can reduce ML energy impact by: "
            "(1) Using pre-trained models rather than training from scratch; "
            "(2) Applying model compression techniques (quantization, pruning, distillation); "
            "(3) Choosing smaller, task-appropriate model architectures; "
            "(4) Batching inference requests to maximize hardware utilization; "
            "(5) Caching model instances to avoid repeated loading; "
            "(6) Scheduling training during low-carbon grid periods."
        )
    },
    {
        "title": "SDG 12: Responsible Consumption and Production",
        "source": "https://sdgs.un.org/goals/goal12",
        "category": "sdg",
        "content": (
            "UN Sustainable Development Goal 12 aims to ensure sustainable consumption and production patterns. "
            "In the context of software and AI, this means: reducing computational waste, optimizing resource "
            "usage, extending hardware lifetimes through efficient software, and being transparent about "
            "resource consumption. Software efficiency aligns with SDG 12 targets on sustainable management "
            "of natural resources, reduction of waste, and encouraging companies to adopt sustainable practices. "
            "Developers can contribute by writing efficient code that consumes fewer computational resources."
        )
    },
    {
        "title": "SDG 13: Climate Action through Technology",
        "source": "https://sdgs.un.org/goals/goal13",
        "category": "sdg",
        "content": (
            "SDG 13 calls for urgent action to combat climate change. The ICT sector accounts for approximately "
            "2-4% of global greenhouse gas emissions. Software efficiency improvements, while not a silver bullet, "
            "can contribute to lower emissions by reducing energy demand from data centers and end-user devices. "
            "Climate-aware software practices include: using renewable energy-powered infrastructure, "
            "optimizing for carbon intensity of electricity grids, reducing unnecessary compute, "
            "and implementing sustainability metrics in software development lifecycles."
        )
    },
    {
        "title": "SDG 9: Industry, Innovation and Infrastructure",
        "source": "https://sdgs.un.org/goals/goal9",
        "category": "sdg",
        "content": (
            "SDG 9 promotes building resilient infrastructure and fostering innovation. "
            "In software engineering, this includes developing more efficient computing infrastructure, "
            "creating developer tools that surface sustainability insights, and innovating in areas "
            "like efficient hardware utilization, serverless computing, and edge computing that can "
            "reduce overall infrastructure energy demand. Green software tools and practices represent "
            "sustainable innovation in the software industry."
        )
    },
    {
        "title": "Responsible AI Principles",
        "source": "https://www.ibm.com/topics/responsible-ai",
        "category": "responsible_ai",
        "content": (
            "Responsible AI encompasses transparency, fairness, explainability, robustness, privacy, and "
            "environmental responsibility. For sustainability tools: (1) Transparency — clearly explain "
            "how sustainability estimates are calculated and their assumptions; (2) Accuracy — distinguish "
            "between measured and modeled data; (3) Fairness — assess workloads and code, not individuals; "
            "(4) Human oversight — AI suggestions should be reviewed and validated by engineers; "
            "(5) Privacy — do not expose user code to third parties without consent; "
            "(6) Environmental responsibility — be honest about the uncertainty in sustainability claims."
        )
    },
    {
        "title": "Memory Efficiency in Software",
        "source": "https://greensoftware.foundation/",
        "category": "memory_efficiency",
        "content": (
            "Memory efficiency is a key dimension of green software. Excessive memory allocation increases "
            "garbage collection pressure, cache misses, and overall energy consumption. Best practices: "
            "(1) Use generators instead of lists for large sequences; "
            "(2) Avoid unnecessary object copies (use views/references where possible); "
            "(3) Release resources explicitly rather than relying solely on GC; "
            "(4) Use appropriate data types (e.g., numpy arrays instead of Python lists for numerical data); "
            "(5) Stream large files rather than loading entirely into memory; "
            "(6) Use connection pools for database/network resources."
        )
    },
    {
        "title": "I/O Optimization for Energy Efficiency",
        "source": "https://principles.green/",
        "category": "io_efficiency",
        "content": (
            "I/O operations (disk, network, database) are often the most energy-intensive parts of an "
            "application. Each I/O operation involves system calls, context switches, and hardware activation. "
            "Reducing I/O improves energy efficiency: (1) Batch database queries rather than N+1 patterns; "
            "(2) Cache API responses to avoid redundant network calls; "
            "(3) Buffer file writes rather than writing byte-by-byte; "
            "(4) Use connection pooling for databases; "
            "(5) Compress data to reduce network transfer volume; "
            "(6) Read files once and cache in memory if accessed repeatedly."
        )
    },
    {
        "title": "Model Quantization and Compression",
        "source": "https://pytorch.org/docs/stable/quantization.html",
        "category": "ml_optimization",
        "content": (
            "Model quantization reduces the precision of model weights (e.g., from float32 to int8), "
            "reducing model size by ~4x and often improving inference speed by 2-4x with minimal accuracy loss. "
            "Post-training quantization can be applied without retraining. Dynamic quantization works well "
            "for RNN/LSTM models. Static quantization requires calibration data. Quantization-aware training "
            "achieves the best accuracy. Other compression techniques: pruning (removing low-importance weights), "
            "knowledge distillation (training a smaller student model from a larger teacher), and "
            "low-rank approximation. These techniques reduce energy consumption during inference."
        )
    },
    {
        "title": "Batching for ML Inference Efficiency",
        "source": "https://www.tensorflow.org/guide/performance/overview",
        "category": "ml_optimization",
        "content": (
            "Batching is one of the most effective ways to improve ML inference efficiency. "
            "Modern hardware (CPUs and GPUs) is optimized for matrix operations on batches of data. "
            "Running n individual inference calls is far less efficient than one batched call for n samples. "
            "GPU speedups from batching can be 10-100x for appropriate workloads. "
            "For serving scenarios, implement dynamic batching to group incoming requests. "
            "Choose batch sizes that maximize hardware utilization without exceeding memory limits. "
            "For CPU-bound workloads, batching reduces Python overhead per sample."
        )
    },
    {
        "title": "Carbon-Aware Computing",
        "source": "https://carbon-aware-sdk.greensoftware.foundation/",
        "category": "carbon_awareness",
        "content": (
            "Carbon-aware computing shifts workloads to times or locations with lower grid carbon intensity. "
            "Grid carbon intensity (gCO2e/kWh) varies by region and time of day based on the energy mix "
            "(renewable vs. fossil fuel). The Carbon-Aware SDK (Green Software Foundation) provides tools "
            "to schedule compute workloads during low-carbon periods. Strategies: temporal shifting "
            "(schedule batch jobs at night when wind energy is higher), spatial shifting (use data centers "
            "in regions with cleaner grids), and demand shaping (reduce quality/precision during high-carbon periods). "
            "This is most applicable to batch ML training and large-scale data processing."
        )
    },
    {
        "title": "Python Performance Optimization Techniques",
        "source": "https://docs.python.org/3/howto/perf_profiling.html",
        "category": "python_optimization",
        "content": (
            "Python performance optimization techniques for energy efficiency: "
            "(1) Use list comprehensions over for-loops with append (2-3x faster); "
            "(2) Use map/filter for simple transformations; "
            "(3) Prefer NumPy vectorized operations over loops for numerical data (10-100x faster); "
            "(4) Use sets for membership testing (O(1) vs O(n) for lists); "
            "(5) Cache function results with functools.lru_cache for pure functions; "
            "(6) Use __slots__ in classes to reduce memory overhead; "
            "(7) Profile before optimizing — avoid premature optimization; "
            "(8) Use generators to process large datasets without materializing in memory."
        )
    },
    {
        "title": "Data Center Power Usage Effectiveness (PUE)",
        "source": "https://www.thegreengrid.org/",
        "category": "infrastructure",
        "content": (
            "Power Usage Effectiveness (PUE) measures data center energy efficiency: "
            "PUE = Total Facility Energy / IT Equipment Energy. "
            "A PUE of 1.0 means 100% of energy goes to IT equipment (ideal). "
            "World average is ~1.5; hyperscale cloud providers achieve ~1.1-1.2. "
            "When estimating software carbon impact, PUE must be factored in: "
            "the IT energy consumption is multiplied by PUE to get total facility energy. "
            "Choosing cloud providers with low PUE and renewable energy commitments can "
            "significantly reduce software's environmental footprint."
        )
    },
    {
        "title": "Measuring Software Energy Consumption",
        "source": "https://greensoftware.foundation/",
        "category": "measurement",
        "content": (
            "Accurately measuring software energy consumption requires hardware instrumentation: "
            "RAPL (Running Average Power Limit) on Intel processors, NVML for NVIDIA GPUs, "
            "or external power meters. Without hardware instrumentation, energy must be estimated "
            "from proxy metrics (CPU time, TDP, utilization). "
            "Tools like CodeCarbon, Carbonara, and Scaphandre enable energy measurement in CI/CD pipelines. "
            "Key metrics to collect: wall time, CPU time, peak memory, GPU utilization, I/O bytes. "
            "Sustainability estimates from static analysis alone are indicative only — "
            "actual energy depends on hardware, OS, runtime conditions, and workload characteristics."
        )
    }
]


class TFIDFRetriever:
    """
    TF-IDF based document retriever.
    Does not require heavy ML dependencies.
    """

    def __init__(self):
        self.chunks: List[Dict] = []
        self.tfidf_matrix: Optional[List[List[float]]] = None
        self.vocab: Dict[str, int] = {}
        self._built = False

    def build_index(self, documents: List[Dict]):
        """Chunk documents and build TF-IDF index."""
        self.chunks = []
        for doc_idx, doc in enumerate(documents):
            text = doc["content"]
            # Simple chunking: split by sentence groups
            sentences = re.split(r'(?<=[.!?])\s+', text)
            chunk_size = 3
            for i in range(0, len(sentences), chunk_size):
                chunk = " ".join(sentences[i:i + chunk_size])
                if len(chunk.strip()) < 20:
                    continue
                self.chunks.append({
                    "chunk_text": chunk,
                    "chunk_index": i // chunk_size,
                    "document_title": doc["title"],
                    "document_source": doc.get("source"),
                    "category": doc.get("category"),
                    "doc_idx": doc_idx
                })

        # Build vocabulary
        all_terms = set()
        for chunk in self.chunks:
            for term in self._tokenize(chunk["chunk_text"]):
                all_terms.add(term)
        self.vocab = {term: idx for idx, term in enumerate(sorted(all_terms))}

        # Compute TF-IDF
        self.tfidf_matrix = []
        doc_freq = [0] * len(self.vocab)
        # Count document frequencies
        tf_vectors = []
        for chunk in self.chunks:
            terms = self._tokenize(chunk["chunk_text"])
            tf = [0.0] * len(self.vocab)
            term_counts: Dict[str, int] = {}
            for t in terms:
                term_counts[t] = term_counts.get(t, 0) + 1
            total = len(terms) or 1
            for term, count in term_counts.items():
                if term in self.vocab:
                    idx = self.vocab[term]
                    tf[idx] = count / total
                    doc_freq[idx] += 1
            tf_vectors.append(tf)

        N = len(self.chunks)
        for tf in tf_vectors:
            tfidf = []
            for i, val in enumerate(tf):
                idf = math.log((N + 1) / (doc_freq[i] + 1)) + 1
                tfidf.append(val * idf)
            self.tfidf_matrix.append(tfidf)

        self._built = True

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-z]{2,}\b', text.lower())

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self._built:
            return []
        query_terms = self._tokenize(query)
        query_tf: Dict[str, float] = {}
        for t in query_terms:
            query_tf[t] = query_tf.get(t, 0) + 1
        total = len(query_terms) or 1
        query_vec = [0.0] * len(self.vocab)
        for term, count in query_tf.items():
            if term in self.vocab:
                query_vec[self.vocab[term]] = count / total

        scores = []
        for i, doc_vec in enumerate(self.tfidf_matrix):
            sim = self._cosine_similarity(query_vec, doc_vec)
            scores.append((i, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            if score > 0.0:
                chunk = dict(self.chunks[idx])
                chunk["score"] = round(score, 4)
                results.append(chunk)
        return results


class RAGSystem:
    """
    Main RAG system for GreenForge AI.
    Combines TF-IDF retrieval with AI-powered answer generation.
    """

    def __init__(self):
        self.retriever = TFIDFRetriever()
        self.retriever.build_index(KNOWLEDGE_BASE)

    def query(self, query: str, top_k: int = 5, context: Optional[Dict] = None) -> Dict:
        """
        Retrieve relevant chunks and generate an answer.
        """
        chunks = self.retriever.retrieve(query, top_k=top_k)

        if not chunks:
            return {
                "query": query,
                "answer": (
                    "No directly relevant information was found in the local knowledge base for this query. "
                    "Please consult greensoftware.foundation, the SCI specification, or the IBM Granite "
                    "AI provider for more detailed guidance."
                ),
                "source_chunks": [],
                "is_grounded": False,
                "ai_provider": "Local fallback"
            }

        # Build context from retrieved chunks
        context_text = "\n\n".join(
            f"[Source: {c['document_title']}]\n{c['chunk_text']}"
            for c in chunks[:3]
        )

        # Try to generate answer with AI provider
        from app.providers.ai_provider import get_ai_provider
        provider = get_ai_provider()

        prompt = (
            f"You are GreenForge AI's knowledge assistant, specializing in green software engineering, "
            f"sustainable AI, and computational efficiency.\n\n"
            f"Using the following retrieved knowledge base excerpts, answer the user's question accurately.\n\n"
            f"Retrieved context:\n{context_text}\n\n"
            f"Question: {query}\n\n"
            f"Provide a clear, accurate answer based on the retrieved context. "
            f"If the context doesn't fully answer the question, say so."
        )

        try:
            answer = provider.generate(prompt, max_tokens=600)
            is_grounded = True
        except Exception as e:
            # Construct answer from retrieved chunks directly
            answer = (
                f"Based on the GreenForge AI knowledge base:\n\n"
                + "\n\n".join(c["chunk_text"] for c in chunks[:2])
            )
            is_grounded = True

        return {
            "query": query,
            "answer": answer,
            "source_chunks": [
                {
                    "chunk_text": c["chunk_text"],
                    "document_title": c["document_title"],
                    "document_source": c.get("document_source"),
                    "score": c["score"],
                    "chunk_index": c["chunk_index"]
                }
                for c in chunks
            ],
            "is_grounded": is_grounded,
            "ai_provider": provider.name
        }


# Singleton
_rag_instance: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance
