# %%

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)

encoder = SentenceTransformer('all-MiniLM-L6-v2')

user_query = "Can you recommend me a terror book?"

query_vector = encoder.encode(user_query).tolist()

hits = client.search(
        collection_name="books",
        query_vector=query_vector,
        limit=10,
    )

h = [f"- {hit.payload.get('combined_column')}" for hit in hits]

for x in h:
    print(x)



# %%