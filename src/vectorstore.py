import os
from langchain.vectorstores import FAISS
from embed import get_embeddings
from chunking import chunk_text

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def create_faiss_index(text_path, save_path="faiss_index"):
    print(f"Loading and chunking {text_path}...")
    text = load_file(text_path)
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")

    embeddings = get_embeddings()
    print("Generating embeddings and building index...")
    faiss_index = FAISS.from_texts(chunks, embeddings)

    print(f"Saving FAISS index to {save_path}...")
    faiss_index.save_local(save_path)

def create_faiss_index_from_many(files, save_path="faiss_index_all"):
    print(f"Loading and chunking {len(files)} files...")
    all_chunks = []

    for file_path in files:
        text = load_file(file_path)
        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    print(f"Total chunks across files: {len(all_chunks)}")
    embeddings = get_embeddings()
    faiss_index = FAISS.from_texts(all_chunks, embeddings)
    faiss_index.save_local(save_path)
    print(f"Saved combined index to {save_path}")

# if __name__ == "__main__":
#     create_faiss_index("data/edgar_sec_filings/apple_10K.txt")

if __name__ == "__main__":
    files = [
        "data/edgar_sec_filings/apple_10K.txt",
        "data/edgar_sec_filings/amazon_10K.txt"
    ]
    create_faiss_index_from_many(files)

