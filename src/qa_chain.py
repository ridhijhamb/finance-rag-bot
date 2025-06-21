import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load API keys
load_dotenv()

# Load FAISS index
def load_faiss_index(path="faiss_index_all"):
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

def build_qa_chain(index, company, level):
    retriever = index.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3, "filter": {"company": company}}
    )
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    prompt_template = """
You are an AI investment assistant helping users understand financial documents like 10-K filings.

Context:
{context}

User level: {level}
Question: {question}

Instructions:
- If the user is a beginner, explain in a simple, friendly, and non-technical way.
- If the user is intermediate, use some financial terms but keep it approachable.
- If the user is an expert, use technical financial language, ratios, and precise analysis.

Answer:
"""
    prompt = PromptTemplate(
        input_variables=["context", "question", "level"],
        template=prompt_template,
    )

    return create_stuff_documents_chain(llm=llm, prompt=prompt), retriever

if __name__ == "__main__":
    index = load_faiss_index()

    company = input("Choose a company (Apple / Amazon / Alphabet): ").strip().capitalize()
    if company not in {"Apple", "Amazon", "Alphabet"}:
        print("Invalid company. Defaulting to Apple.")
        company = "Apple"

    level = input("Choose your level (Beginner / Intermediate / Expert): ").strip().capitalize()
    if level not in {"Beginner", "Intermediate", "Expert"}:
        print("Invalid input. Defaulting to Intermediate.")
        level = "Intermediate"

    qa_chain, retriever = build_qa_chain(index, company, level)

    print(f"\nYou are in {level} mode. Ask a question about {company} (type 'exit' to quit):\n")

    while True:
        query = input("Q: ")
        if query.lower() in {"exit", "quit"}:
            break
        docs = retriever.invoke(query)
        result = qa_chain.invoke({"context": docs, "question": query, "level": level})
        print(f"\nA: {result}\n")

