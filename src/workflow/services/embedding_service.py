from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
import os
from typing import Optional, List, Dict, Any

class EmbeddingService:
    def __init__(self, embedding_model: Optional[OpenAIEmbeddings] = None):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        self.embedding_model = embedding_model or OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    async def similarity_search(
        self,
        query: str,
        collection_name: str,
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.embedding_model.aembed_query(query)

        search_results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )

        return [
            {
                "text": item.payload["text"],
                "metadata": item.payload.get("metadata", {}),
                "score": item.score
            }
            for item in search_results
        ]

    async def search_for_context(
        self,
        query: str,
        collection_name: str,
        top_k: int = 4
    ) -> Optional[str]:
        try:
            results = await self.similarity_search(
                query=query,
                collection_name=collection_name,
                limit=top_k
            )
            
            if not results:
                return None
                
            return "\n\n".join([result["text"] for result in results])
            
        except Exception as e:
            print(f"Error searching for context: {e}")
            return None