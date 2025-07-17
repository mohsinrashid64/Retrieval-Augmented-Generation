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
OLLAMA_MODEL = "llama3.2:latest"
EMBED_MODEL = "llama3.2:latest"
CHROMA_DB_DIR = "./chroma_db"

# -------- Initialize --------
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

# -------- Streamlit UI --------
st.set_page_config(page_title="RAG App with ChromaDB", layout="wide")
st.title("📄 RAG App")

uploaded_file = st.file_uploader("Upload a PDF file to build knowledge base", type=["pdf"])

# Load or create vectorstore
vectorstore = load_vectorstore()

if uploaded_file is not None:
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.read())
    
    # Load documents
    loader = PyPDFLoader("uploaded_file.pdf")
    documents = loader.load()

    # Split text
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
    docs = splitter.split_documents(documents)

    # Create and persist vectorstore
    vectorstore = create_vectorstore(docs)
    st.success("Knowledge base updated!")

if vectorstore is None:
    st.warning("⚠️ Upload a PDF first to start asking questions.")
else:
    query = st.text_input("Ask something about your uploaded PDF:")

    if query:
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
