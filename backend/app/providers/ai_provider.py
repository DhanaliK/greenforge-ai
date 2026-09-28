"""
AI Provider abstraction for GreenForge AI.
Supports IBM Granite via watsonx.ai and a local deterministic fallback.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 800) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass


class LocalFallbackProvider(AIProvider):
    """
    Deterministic local provider for demo/fallback mode.
    Uses template-based reasoning — clearly labeled as local AI mode.
    """

    @property
    def name(self) -> str:
        return "Local fallback (Demo / Local AI mode)"

    @property
    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, max_tokens: int = 800) -> str:
        p = prompt.lower()

        if "explain" in p and ("nested loop" in p or "o(n²)" in p or "o(n^2)" in p):
            return (
                "[Demo / Local AI mode] The nested loop pattern causes the inner body to execute "
                "approximately n² times for an input of size n. As n grows, this quadratic scaling "
                "significantly increases CPU time. For large datasets, replacing the inner loop with "
                "a hash-based lookup (dict/set) can reduce this to O(n) overall complexity. "
                "Whether this matters depends on actual input sizes in your workload."
            )

        if "optimize" in p or "optimization" in p:
            return (
                "[Demo / Local AI mode] Based on the detected inefficiency patterns, the primary "
                "optimization opportunity is to reduce algorithmic complexity by replacing repeated "
                "iteration with more efficient data structures or pre-computation. "
                "The optimized version uses a dictionary/set for O(1) lookups instead of O(n) linear scans. "
                "Please benchmark both versions to confirm improvement in your specific context."
            )

        if "sustainability" in p or "carbon" in p or "energy" in p:
            return (
                "[Demo / Local AI mode] The sustainability impact shown is a modeled estimate based on "
                "benchmark runtime and configurable hardware assumptions (CPU TDP, PUE, grid carbon intensity). "
                "A reduction in runtime translates to less CPU-time consumed, which reduces estimated energy use. "
                "These are estimates — not validated environmental measurements. "
                "The primary benefit is reduced compute resource usage, which aligns with SDG 12 (Responsible Consumption)."
            )

        if "ml" in p or "model" in p or "inference" in p:
            return (
                "[Demo / Local AI mode] The ML efficiency findings indicate opportunities to improve "
                "inference throughput. Key recommendations: (1) Load the model once and reuse it "
                "across all inference calls. (2) Batch inputs together rather than running single-sample "
                "inference in a loop. (3) Consider quantization or a smaller model architecture if "
                "accuracy requirements allow. Benchmark before and after any optimization."
            )

        if "trade" in p or "tradeoff" in p or "trade-off" in p:
            return (
                "[Demo / Local AI mode] Every optimization involves trade-offs. "
                "Faster algorithms may use more memory (space-time trade-off). "
                "Smaller ML models are faster but may sacrifice accuracy. "
                "Batching improves throughput but increases latency for individual requests. "
                "The right choice depends on your application's requirements and constraints. "
                "Use the benchmark comparison to make an evidence-based decision."
            )

        if "score" in p or "greenforge" in p:
            return (
                "[Demo / Local AI mode] The GreenForge Score is a composite indicator (0–100) "
                "computed from weighted sub-scores: algorithmic efficiency, runtime efficiency, "
                "memory efficiency, I/O efficiency, ML efficiency, optimization potential, and "
                "benchmark improvement. It is a prototype decision-support metric, not an "
                "industry certification. A higher score reflects fewer detected efficiency concerns."
            )

        if "rag" in p or "knowledge" in p or "green software" in p:
            return (
                "[Demo / Local AI mode] Green Software Engineering focuses on three pillars: "
                "energy efficiency, carbon awareness, and hardware efficiency. "
                "The Software Carbon Intensity (SCI) specification provides a framework for "
                "measuring software carbon impact. Key principle: reduce unnecessary computation, "
                "use efficient algorithms, choose appropriate hardware, and be aware of grid carbon intensity "
                "when scheduling compute-intensive workloads."
            )

        # Generic fallback
        return (
            "[Demo / Local AI mode] This response is generated by the local deterministic fallback. "
            "Configure IBM Granite credentials in .env to enable AI-powered analysis. "
            "The analysis above was produced by GreenForge AI's static analysis engine and "
            "does not require an external AI service."
        )


class GraniteProvider(AIProvider):
    """
    IBM Granite provider via watsonx.ai API.
    Requires IBM_API_KEY, IBM_PROJECT_ID, IBM_SERVICE_URL in environment.
    """

    def __init__(self):
        self._client = None
        self._model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")
        self._project_id = os.getenv("IBM_PROJECT_ID")
        self._api_key = os.getenv("IBM_API_KEY")
        self._service_url = os.getenv("IBM_SERVICE_URL", "https://us-south.ml.cloud.ibm.com")
        self._initialized = False
        self._init_error = None

    def _init_client(self):
        if self._initialized:
            return
        try:
            from ibm_watsonx_ai import APIClient, Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference

            credentials = Credentials(
                api_key=self._api_key,
                url=self._service_url
            )
            self._client = ModelInference(
                model_id=self._model_id,
                credentials=credentials,
                project_id=self._project_id
            )
            self._initialized = True
            logger.info("IBM Granite provider initialized successfully")
        except ImportError:
            self._init_error = "ibm-watsonx-ai not installed"
            logger.warning("ibm-watsonx-ai package not available")
        except Exception as e:
            self._init_error = str(e)
            logger.warning(f"Failed to initialize Granite provider: {e}")

    @property
    def name(self) -> str:
        return f"IBM Granite ({self._model_id})"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key and self._project_id)

    def generate(self, prompt: str, max_tokens: int = 800) -> str:
        if not self.is_available:
            raise RuntimeError("IBM Granite credentials not configured")
        self._init_client()
        if not self._initialized:
            raise RuntimeError(f"Granite initialization failed: {self._init_error}")
        try:
            response = self._client.generate_text(
                prompt=prompt,
                params={
                    "max_new_tokens": max_tokens,
                    "temperature": 0.3,
                    "top_p": 0.9,
                }
            )
            return response
        except Exception as e:
            logger.error(f"Granite generation error: {e}")
            raise


def get_provider() -> AIProvider:
    """Get the best available AI provider."""
    granite = GraniteProvider()
    if granite.is_available:
        try:
            granite._init_client()
            if granite._initialized:
                return granite
        except Exception:
            pass
    return LocalFallbackProvider()


# Singleton
_provider_instance: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = get_provider()
    return _provider_instance


def reset_provider():
    """Force re-initialization (e.g., after settings change)."""
    global _provider_instance
    _provider_instance = None
