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

# Page config
st.set_page_config(page_title="💸 Multitone Investment Assistant", page_icon="💸")

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/1/11/Finance_icon.png", width=100)
st.sidebar.title("Multitone Investment Assistant")
tone = st.sidebar.radio("Choose your experience level:", ["Beginner", "Intermediate", "Expert"])

st.markdown(
    f"""
    <h1 style='text-align: center;'>💼 Investment Q&A Assistant</h1>
    <p style='text-align: center; font-size: 16px;'>Ask questions grounded in Apple, Amazon, and Alphabet’s 10-K filings.</p>
    <p style='text-align: center; font-size: 14px; color: gray;'>Response tone: <b>{tone}</b></p>
    """,
    unsafe_allow_html=True,
)

# Input area
query = st.text_input("🔎 What would you like to ask?", placeholder="e.g., What is Apple's revenue in 2023?")

if query:
    with st.spinner("Thinking... 🤔"):
        index = load_index()
        qa_chain = get_qa_chain(index)
        response = qa_chain({"query": query})

    st.markdown("### 📎 Answer")
    st.success(response["result"])

    with st.expander("🔍 View Retrieved Chunks"):
        for i, doc in enumerate(response["source_documents"]):
            st.markdown(f"**Chunk {i+1}:**")
            st.code(doc.page_content[:500].strip() + " ...", language="markdown")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 12px; color: gray;'>Built with ❤️ by Ridhi Jhamb</p>",
    unsafe_allow_html=True,
)
