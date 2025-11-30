from __future__ import annotations
import os
import json
from typing import List, Optional, Dict


STORY_INDEX_BASE_DIR = "app/story_indexes"


def _load_json(path: str) -> Dict:
    """Utility function to load JSON data from a file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _load_story_context(node_id: str, docstore: Dict) -> str:
    try:
        if node_id in docstore.get("docstore/data", {}):
            node_data = docstore["docstore/data"][node_id]
            if "__data__" in node_data:
                node_content = node_data["__data__"]
                return node_content.get("text", "")
    except Exception as e:
        print(f"Error loading docstore: {e}")

def retrieve_story_context(story_title: str, user_query: str,
                           current_story_state: Optional[str] = None, child_story_states: Optional[List[str]] = None) -> List:
    
    ret = {}
    ret["current_story"] = {}
    ret["child_stories"] = []

    # Load docstore.json
    path = f"{STORY_INDEX_BASE_DIR}/{story_title}/docstore.json"
    if not os.path.exists(path):
        print(f"Retrieval result file not found: {path}")
        return ret
    docstore = _load_json(path)

    # Retrieve current story state
    if current_story_state:
        story = _load_story_context(current_story_state, docstore)
        ret["current_story"] = {
            "state_id": current_story_state,
            "text": story
        }

    # Retrieve child story states
    if child_story_states:
        for state_id in child_story_states:
            story = _load_story_context(state_id, docstore)
            ret["child_stories"].append({
                "state_id": state_id,
                "text": story
            })    

    return ret

__all__ = ["retrieve_story_context"]

# from __future__ import annotations
# from typing import List, Optional, Dict
# from pathlib import Path
# from functools import lru_cache 
# import os
# from llama_index.core import StorageContext, load_index_from_storage, VectorStoreIndex
# from llama_index.core.schema import NodeWithScore
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.core import Settings
# from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

# STORY_INDEX_BASE_DIR = "app/story_indexes"
# EMBED_MODEL_NAME = "jhgan/ko-sbert-nli"
# _EMBED_MODEL = None

# def _get_embed_model():
#     """Lazy load and cache the embedding model."""
#     global _EMBED_MODEL
#     if _EMBED_MODEL is None:
#         try:
#             _EMBED_MODEL = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
#             print(f"[Story RAG] Embedding model loaded: {EMBED_MODEL_NAME}")
#         except Exception as e:
#             print(f"경고: HuggingFace 임베딩 모델 로드 실패. {e}")
#             raise
#     return _EMBED_MODEL


# @lru_cache(maxsize=10)  # Cache up to 10 different story indexes
# def _load_story_index(story_title: str) -> Optional[VectorStoreIndex]:
#     """
#     Load the story index from storage.
#     Args:
#         story_title: Title of the story to load the index for.
#     Returns:
#         Loaded VectorStoreIndex or None if loading fails.
#     """
#     try:
#         # Set embedding model (lazy load on first call)
#         Settings.embed_model = _get_embed_model()
        
#         index_dir = Path(STORY_INDEX_BASE_DIR) / story_title
#         if not index_dir.exists():
#             print(f"Failed to find story index directory: {index_dir}")
#             return None
            
#         storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
#         index = load_index_from_storage(storage_context)
#         print(f"Story index loaded successfully: {story_title}")
#         return index
#     except Exception as e:
#         print(f"Error loading story index '{story_title}': {e}")
#         return None


# def retrieve_story_context(story_title: str, user_query: str, current_depth: Optional[int] = None) -> List:
#     """
#     Main retrieval function for story context.
#     Args:
#         story_title: Title of the story to retrieve context from.
#         user_query: User's input message for retrieval.
#     Returns:
#         List of retrieved story segments as dicts with 'text' and 'score'.
#     """
    
#     all_nodes: List[NodeWithScore] = []
#     results: List[Dict] = []

#     # 1. Load story index and perform retrieval
#     story_index = _load_story_index(story_title)
    
#     if story_index:
#         filters = None
#         if current_depth is not None:
#             filters = MetadataFilters(
#                 filters=[
#                     MetadataFilter(
#                         key="depth",             
#                         value=current_depth,     
#                         operator=FilterOperator.LTE,# LTE = (<=)
#                     )
#                 ]
#             )
    

#         retriever = story_index.as_retriever(filters=filters)
#         retrieved_nodes = retriever.retrieve(user_query)
#         all_nodes.extend(retrieved_nodes)
#     else:
#         print(f"No story index found for title: {story_title}")
#         return results

#     # 2. Convert results (Node -> List[Dict])
#     for i, node_with_score in enumerate(all_nodes):
#         node = node_with_score.node
#         results.append({
#             "text": node.get_content(),
#             "score": node_with_score.score 
#         })
#     return results

# __all__ = ["retrieve_story_context"]