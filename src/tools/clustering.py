from sklearn.cluster import AgglomerativeClustering
import numpy as np 
from ..settings.config import LLMFactory, get_settings
from collections import defaultdict
import logging 

logger = logging.getLogger(__name__)
settings = get_settings()

def cluster_claims(claims: list[str]) -> list[list[str]]:
    max_batch_size = settings.MAX_BATCH_SIZE
    try:
        if len(claims) < settings.CLUSTERING_MIN_CLAIMS:
            return cluster_simple(claims)
        
        embedd_model = LLMFactory.get_cluster_encoder()
        embeddings = embedd_model.encode(claims)
        embeddings_arr = np.array(embeddings)
        
        cluster_model = LLMFactory.get_clustering_model()
        cluster_model.fit(embeddings_arr)
        labels = cluster_model.labels_
        
        grouped_clusters = defaultdict(list)
        for claim, label in zip(claims, labels):
            grouped_clusters[label].append(claim)
        
        final_batches = []
        current_batch = []
        for cluster_id, cluster_items in grouped_clusters.items():
            if len(cluster_items) > max_batch_size:
                if current_batch:
                    final_batches.append(current_batch)
                    current_batch = []
                for i in range(0, len(cluster_items), max_batch_size):
                    chunk = cluster_items[i : i + max_batch_size]
                    if len(chunk) == max_batch_size:
                        final_batches.append(chunk)
                    else:
                        current_batch = list(chunk)
                continue
            if len(current_batch) + len(cluster_items) <= max_batch_size:
                current_batch.extend(cluster_items)
            else:
                if current_batch:
                    final_batches.append(current_batch)
                current_batch = list(cluster_items)
        if current_batch:
            final_batches.append(current_batch)
        
        return final_batches
    except Exception as e:
        logger.error(f"Clustering failed. Error: {e}")
        return cluster_simple(claims)
    
def cluster_simple(claims: list[str]):
    return [claims[i:i+ settings.MAX_BATCH_SIZE] for i in range(0, len(claims), settings.MAX_BATCH_SIZE)]