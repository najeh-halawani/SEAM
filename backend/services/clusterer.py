"""Semantic clustering of diagnostic field notes.

Uses sentence-transformers for multilingual embeddings and
scikit-learn agglomerative clustering to group similar statements.
"""

import logging
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances

logger = logging.getLogger(__name__)

# ── Lazy-loaded model ─────────────────────────────────────────────────

_model = None


def _get_model():
    """Lazily load the sentence-transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from backend.config import settings
        logger.info(f"Loading sentence-transformer model: {settings.sentence_transformer_model}")
        _model = SentenceTransformer(settings.sentence_transformer_model)
    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate sentence embeddings for a list of texts.

    Args:
        texts: List of field note texts.

    Returns:
        List of embedding vectors (as lists of floats).
    """
    if not texts:
        return []

    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def cluster_field_notes(
    texts: list[str],
    embeddings: list[list[float]] | None = None,
    distance_threshold: float = 0.5,
) -> dict:
    """Cluster field notes by semantic similarity.

    Args:
        texts: List of field note texts.
        embeddings: Pre-computed embeddings (optional — will generate if None).
        distance_threshold: Cosine distance threshold for clustering.
            Lower = tighter clusters, Higher = more permissive.

    Returns:
        dict with:
            - cluster_labels: list of cluster IDs (same length as texts)
            - n_clusters: number of clusters found
            - clusters: dict mapping cluster_id -> {texts, representative}
    """
    if not texts or len(texts) < 2:
        return {
            "cluster_labels": [0] * len(texts) if texts else [],
            "n_clusters": 1 if texts else 0,
            "clusters": {0: {"texts": texts, "representative": texts[0]}} if texts else {},
        }

    # Generate embeddings if not provided
    if embeddings is None:
        embeddings = generate_embeddings(texts)

    emb_array = np.array(embeddings)

    # Compute cosine distance matrix
    distance_matrix = cosine_distances(emb_array)

    # Agglomerative clustering
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="precomputed",
        linkage="average",
    )
    labels = clustering.fit_predict(distance_matrix)

    # Build cluster summaries
    clusters = {}
    for idx, label in enumerate(labels):
        label_int = int(label)
        if label_int not in clusters:
            clusters[label_int] = {"texts": [], "indices": []}
        clusters[label_int]["texts"].append(texts[idx])
        clusters[label_int]["indices"].append(idx)

    # Find representative statement for each cluster (closest to centroid)
    for label_int, cluster_data in clusters.items():
        indices = cluster_data["indices"]
        if len(indices) == 1:
            cluster_data["representative"] = cluster_data["texts"][0]
        else:
            cluster_embs = emb_array[indices]
            centroid = cluster_embs.mean(axis=0)
            distances_to_centroid = np.linalg.norm(cluster_embs - centroid, axis=1)
            representative_idx = distances_to_centroid.argmin()
            cluster_data["representative"] = cluster_data["texts"][representative_idx]
        del cluster_data["indices"]

    return {
        "cluster_labels": [int(l) for l in labels],
        "n_clusters": len(clusters),
        "clusters": clusters,
    }
