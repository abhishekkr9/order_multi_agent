from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from config import embeddings # Import embeddings from config.py

# Define the URL for document loading
# Note: This URL might be temporary or require specific access.
# Consider replacing with a more permanent or locally hosted document source if needed.
url = "https://jmp.sh/s/xytMC8GRMqFt3qmbIRL7"
try:
    loader = WebBaseLoader([url])
    docs = loader.load()

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )

    # Split documents
    doc_splits = text_splitter.split_documents(docs)

    # Create Chroma vector store
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embeddings,
    )

    # Create retriever
    retriever = vectorstore.as_retriever()

except Exception as e:
    print(f"Error setting up vector store from {url}: {e}")
    print("Vector store and retriever setup failed. Support agent functionality might be limited.")
    vectorstore = None
    retriever = None