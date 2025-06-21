import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

# Load FAISS index
@st.cache_resource
def load_index():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local("faiss_index_all", embeddings, allow_dangerous_deserialization=True)

# Build QA chain
def get_qa_chain(index):
    retriever = index.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

# App UI
st.title("📊 Finance Q&A RAG Chatbot")

tone = st.selectbox(
    "Choose your experience level:",
    ["Beginner", "Intermediate", "Expert"],
    index=0
)

st.caption("Ask questions grounded in Apple + Amazon 10-K filings.")

query = st.text_input("Ask your question:")

if query:
    index = load_index()
    qa_chain = get_qa_chain(index)
    response = qa_chain(query)

    st.write("### 📎 Answer")
    st.success(response["result"])

    st.write("### 🔍 Top Retrieved Chunks")
    for i, doc in enumerate(response["source_documents"]):
        st.markdown(f"**Chunk {i+1}**")
        st.code(doc.page_content[:300] + "...", language="markdown")
