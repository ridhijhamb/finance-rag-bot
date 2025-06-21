import os
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load API keys from .env
load_dotenv()

# Load FAISS index
def load_faiss_index(path="faiss_index"):
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)


# Build LangChain RetrievalQA
def build_qa_chain(index):
    retriever = index.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

if __name__ == "__main__":
    index = load_faiss_index("faiss_index_all")
    qa_chain = build_qa_chain(index)

    print("Ask a question about Apple’s 10-K (type 'exit' to quit):\n")
    while True:
        query = input("Q: ")
        if query.lower() in {"exit", "quit"}:
            break
        result = qa_chain.run(query)
        print(f"\nA: {result}\n")
