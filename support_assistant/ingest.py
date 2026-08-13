import os
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "zepto_policies"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

documents = []
ids = []
metadatas = []

for filename in sorted(os.listdir(DOCS_DIR)):
    if filename.endswith(".txt"):
        file_path = os.path.join(DOCS_DIR, filename)

        with open(file_path, "r", encoding="utf-8-sig") as file:
            text = file.read().strip()

        documents.append(text)
        ids.append(filename.replace(".txt", ""))
        metadatas.append({
            "source": filename
        })

embeddings = model.encode(
    documents
).tolist()

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)

print("Documents embedded successfully.")
print("Documents stored:", collection.count())