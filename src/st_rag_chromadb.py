from langchain import chains, text_splitter, PromptTemplate
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community import document_loaders, embeddings, vectorstores, llms
import streamlit as st
import time
import os
import warnings
import ollama

warnings.filterwarnings("ignore")

OLLAMA_BASE_URL = "http://localhost:11434"
VECTOR_DB_DIR = "vector_dbs"

st.header("LLM Rag 🐻‍❄️")

models = [model["name"] for model in ollama.list()["models"]]
model = st.selectbox("Choose a model from the list", models)

# Input text to load the document
url_path = st.text_input("Enter the URL to load for RAG:", key="url_path")

# Select embedding type
embedding_type = st.selectbox(
    "Please select an embedding type",
    ("ollama",
     "huggingface",
     "nomic",
     "fastembed"),
    index=1)

# Input for RAG
question = st.text_input(
    "Enter the question for RAG:",
    value="What is this about",
    key="question")

def load_document(url):
    """
    Load the document from the specified URL.

    Args:
        url (str): The URL of the document to load.

    Returns:
        Document: The loaded document.
    """
    print("Loading document from URL...")
    st.markdown(''' :green[Loading document from URL...] ''')
    loader = document_loaders.WebBaseLoader(url)
    return loader.load()

def split_document(text, chunk_size=3000, overlap=200):
    """
    Split the document into multiple chunks.

    Args:
        text (str): The text of the document to split.
        chunk_size (int): The size of each chunk.
        overlap (int): The overlap between chunks.

    Returns:
        list: A list of document chunks.
    """
    print("Splitting document into chunks...")
    st.markdown(''' :green[Splitting document into chunks...] ''')
    text_splitter_instance = text_splitter.RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap)
    return text_splitter_instance.split_documents(text)

def initialize_embedding_fn(
        embedding_type="huggingface",
        model_name="sentence-transformers/all-MiniLM-l6-v2"):
    """
    Initialize the embedding function based on the specified type.

    Args:
        embedding_type (str): The type of embedding to use.
        model_name (str): The name of the model to use for embeddings.

    Returns:
        Embeddings: The initialized embedding function.
    """
    print(f"Initializing {embedding_type} model with {model_name}...")
    st.write(f"Initializing {embedding_type} model with {model_name}...")
    if embedding_type == "ollama":
        model_name = chat_model
        return embeddings.OllamaEmbeddings(
            model=model_name, base_url=OLLAMA_BASE_URL)
    elif embedding_type == "huggingface":
        model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
        return embeddings.HuggingFaceEmbeddings(model_name=model_name)
    elif embedding_type == "nomic":
        return embeddings.NomicEmbeddings(model_name=model_name)
    elif embedding_type == "fastembed":
        return FastEmbedEmbeddings(threads=16)
    else:
        raise ValueError(f"Unsupported embedding type: {embedding_type}")

def get_or_create_embeddings(
        document_url,
        embedding_fn,
        persist_dir=VECTOR_DB_DIR):
    """
    Create embeddings for the document chunks and store them in a vector database.

    Args:
        document_url (str): The URL of the document.
        embedding_fn (Embeddings): The embedding function to use.
        persist_dir (str): The directory to persist the vector database.

    Returns:
        VectorStore: The created vector store.
    """
    vector_store_path = os.path.join(os.getcwd(), persist_dir)
    start_time = time.time()
    print("No existing vector store found. Creating new one...")
    st.markdown(
        ''' :green[No existing vector store found. Creating new one......] ''')
    document = load_document(document_url)
    documents = split_document(document)
    vector_store = vectorstores.Chroma.from_documents(
        documents=documents,
        embedding=embedding_fn,
        persist_directory=persist_dir
    )
    vector_store.persist()
    print(f"Embedding time: {time.time() - start_time:.2f} seconds")
    st.write(f"Embedding time: {time.time() - start_time:.2f seconds")
    return vector_store

def handle_user_interaction(vector_store, chat_model):
    """
    Handle user interaction by generating a response based on the user's question.

    Args:
        vector_store (VectorStore): The vector store containing document embeddings.
        chat_model (LLM): The language model to generate responses.

    Returns:
        str: The generated response.
    """
    prompt_template = """
    Use the following pieces of context to answer the question at the end.
    If you do not know the answer, answer 'I don't know', limit your response to the answer and nothing more.

    {context}

    Question: {question}
    """
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=[
            "context",
            "question"])
    chain_type_kwargs = {"prompt": prompt}
    st.markdown(
        ''' :green[Using retrievers to retrieve the data from the database...] ''')
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    st.markdown(''' :green[Answering the query...] ''')
    qachain = chains.RetrievalQA.from_chain_type(
        llm=chat_model,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs=chain_type_kwargs)
    qachain.invoke({"query": "what is this about?"})
    print(f"Model warmup complete...")
    st.markdown(''' :green[Model warmup complete...] ''')

    start_time = time.time()
    answer = qachain.invoke({"query": question})
    print(f"Answer: {answer['result']}")
    print(f"Response time: {time.time() - start_time:.2f} seconds")
    st.write(f"Response time: {time.time() - start_time:.2f} seconds")

    return answer['result']

def getfinalresponse(document_url, embedding_type, chat_model):
    """
    Main function to load the document, initialize the embeddings, create the vector database, and invoke the model.

    Args:
        document_url (str): The URL of the document.
        embedding_type (str): The type of embedding to use.
        chat_model (str): The name of the chat model to use.

    Returns:
        str: The final response generated by the model.
    """
    try:
        document_url = url_path
        chat_model = model

        embedding_fn = initialize_embedding_fn(embedding_type)
        vector_store = get_or_create_embeddings(document_url, embedding_fn)
        chat_model_instance = llms.Ollama(
            base_url=OLLAMA_BASE_URL, model=chat_model)
        return handle_user_interaction(vector_store, chat_model_instance)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

submit = st.button("Generate")

if submit:
    if not url_path.strip():
        st.error("Please enter a valid URL.")
    elif not question.strip():
        st.error("Please enter a valid question.")
    else:
        with st.spinner("Loading document....🐎"):
            st.write(getfinalresponse(url_path, embedding_type, model))
