import streamlit as st
import os
import ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# -------- Settings --------
OLLAMA_MODEL = "llama3"
EMBED_MODEL = "nomic-embed-text"
CHROMA_DB_DIR = "./chroma_db"

# -------- Streamlit UI --------
st.set_page_config(page_title="RAG App with ChromaDB", layout="wide")
st.title("🦙📄 RAG App (Streamlit + Ollama + Chroma)")

# Check if Ollama is running
ollama_available = True
try:
    ollama.list()
except Exception as e:
    ollama_available = False
    st.error("❌ Ollama server not detected! Please make sure Ollama is running.", icon="🚫")

uploaded_file = st.file_uploader("Upload a PDF file to build knowledge base", type=["pdf"], disabled=not ollama_available)

# Load or create vectorstore
def load_vectorstore():
    if os.path.exists(CHROMA_DB_DIR):
        return Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=OllamaEmbeddings(model=EMBED_MODEL))
    return None

def create_vectorstore(docs):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=CHROMA_DB_DIR)
    vectorstore.persist()
    return vectorstore

def load_llm():
    return Ollama(model=OLLAMA_MODEL)

vectorstore = load_vectorstore()

if uploaded_file is not None and ollama_available:
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.read())
    
    # Load documents
    loader = PyPDFLoader("uploaded_file.pdf")
    documents = loader.load()

    # Split text
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    # Create and persist vectorstore
    vectorstore = create_vectorstore(docs)
    st.success("Knowledge base updated!")

if vectorstore is None:
    st.warning("⚠️ Upload a PDF first to start asking questions.")

query = st.text_input("Ask something about your uploaded PDF:", disabled=not ollama_available)

if query and ollama_available:
    llm = load_llm()
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff"
    )

    with st.spinner("Thinking..."):
        result = qa.invoke({"query": query})
        st.write("### Answer:")
        st.write(result["result"])
