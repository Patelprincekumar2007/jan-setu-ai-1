import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np

logger = logging.getLogger("nagriklens.knowledge.embedding")

_SERVICE_CACHE = {}


class BaseEmbeddingService(ABC):
    """Abstract interface for document and query embedding services."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def encode_documents(self, documents: List[str]) -> np.ndarray:
        """Encodes a list of text documents into L2-normalized float32 vectors."""
        pass

    @abstractmethod
    def encode_query(self, query: str) -> np.ndarray:
        """Encodes a single query string into a 1D L2-normalized float32 vector."""
        pass


class SentenceTransformerEmbeddingService(BaseEmbeddingService):
    """
    Lazy-loaded SentenceTransformer embedding service.
    Loads the underlying neural model only when an encoding request is actually made.
    """

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self._model_name = model_name
        self._model = None
        self._dimension = None

    @property
    def model_name(self) -> str:
        return self._model_name

    def _ensure_loaded(self):
        if self._model is None:
            logger.info(f"Loading SentenceTransformer model '{self._model_name}'...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Model '{self._model_name}' loaded successfully (dimension: {self._dimension}).")

    @property
    def dimension(self) -> int:
        self._ensure_loaded()
        return self._dimension

    def encode_documents(self, documents: List[str]) -> np.ndarray:
        if not documents:
            dim = self.dimension
            return np.empty((0, dim), dtype=np.float32)

        self._ensure_loaded()
        # SentenceTransformers encode with normalize_embeddings=True gives unit L2 vectors
        embeddings = self._model.encode(
            documents,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        self._ensure_loaded()
        vec = self._model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )[0]
        return vec.astype(np.float32)


class MockEmbeddingService(BaseEmbeddingService):
    """
    Deterministic pseudo-embedding generator for fast, offline, zero-network automated unit testing.
    Generates deterministic normalized unit vectors based on text hashing.
    """

    def __init__(self, model_name: str = "mock-embedding-model", dimension: int = 64):
        self._model_name = model_name
        self._dimension = dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def _hash_to_vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self._dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec

        for word in words:
            # Deterministic word hash
            digest = hashlib.md5(word.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:2], byteorder="big") % self._dimension
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec.astype(np.float32)

    def encode_documents(self, documents: List[str]) -> np.ndarray:
        if not documents:
            return np.empty((0, self._dimension), dtype=np.float32)
        vectors = [self._hash_to_vector(doc) for doc in documents]
        return np.vstack(vectors).astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        return self._hash_to_vector(query)


def get_embedding_service(model_name: Optional[str] = None) -> BaseEmbeddingService:
    """Returns a singleton cached instance of SentenceTransformerEmbeddingService."""
    from backend.config import settings
    name = model_name or settings.embedding_model
    if name not in _SERVICE_CACHE:
        _SERVICE_CACHE[name] = SentenceTransformerEmbeddingService(model_name=name)
    return _SERVICE_CACHE[name]
