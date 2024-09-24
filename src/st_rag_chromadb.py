from langchain import chains, text_splitter, PromptTemplate
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community import document_loaders, embeddings, vectorstores, llms
import streamlit as st
import time
import os
import warnings
import ollama
from typing import List, Dict, Any

warnings.filterwarnings("ignore")

OLLAMA_BASE_URL = "http://localhost:11434"
VECTOR_DB_DIR = "vector_dbs"

st.header("LLM Rag 🐻‍❄️")

# Fetch the list of models from ollama and validate it
try:
    models_response = ollama.list()
    if "models" in models_response and isinstance(models_response["models"], list):
        models = [model["name"] for model in models_response["models"] if "name" in model]
        if not models:
            st.error("No valid models found in the response.")
    else:
        st.error("Invalid response format from ollama.")
        models = []
except Exception as e:
    st.error(f"Error fetching models: {e}")
    models = []

# Ensure models list is not empty before displaying the selectbox
if models:
    model = st.selectbox("Choose a model from the list", models)
else:
    st.error("No models available to choose from.")

# Input text to load the document
url_path = st.text_input("Enter the URL to load for RAG:", key="url_path")

# Select embedding type
embedding_type = st.selectbox(
    "Please select an embedding type",
    ("ollama", "huggingface", "nomic", "fastembed"),
    index=1
)

# Input for RAG
question = st.text_input(
    "Enter the question for RAG:",
    value="What is this about",
    key="question"
)


def load_document(url: str) -> List[Dict[str, Any]]:
    """
    Load the document from the given URL.

    Args:
        url (str): The URL to load the document from.

    Returns:
        List[Dict[str, Any]]: The loaded document.
    """
    try:
        print("Loading document from URL...")
        st.markdown(''' :green[Loading document from URL...] ''')
        loader = document_loaders.WebBaseLoader(url)
        return loader.load()
    except Exception as e:
        st.error(f"Error loading document: {e}")
        return []


def split_document(text: str, chunk_size: int = 3000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split the document into multiple chunks.

    Args:
        text (str): The text to split.
        chunk_size (int): The size of each chunk.
        overlap (int): The overlap between chunks.

    Returns:
        List[Dict[str, Any]]: The split document chunks.
    """
    try:
        print("Splitting document into chunks...")
        st.markdown(''' :green[Splitting document into chunks...] ''')
        text_splitter_instance = text_splitter.RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap)
        return text_splitter_instance.split_documents(text)
    except Exception as e:
        st.error(f"Error splitting document: {e}")
        return []


def initialize_embedding_fn(
        embedding_type: str = "huggingface",
        model_name: str = "sentence-transformers/all-MiniLM-l6-v2") -> Any:
    """
    Initialize the embedding function based on the selected type.

    Args:
        embedding_type (str): The type of embedding to use.
        model_name (str): The name of the model to use.

    Returns:
        Any: The initialized embedding function.
    """
    try:
        print(f"Initializing {embedding_type} model with {model_name}...")
        st.write(f"Initializing {embedding_type} model with {model_name}...")
        if embedding_type == "ollama":
            model_name = model
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
    except Exception as e:
        st.error(f"Error initializing embedding function: {e}")
        return None


def get_or_create_embeddings(
        document_url: str,
        embedding_fn: Any,
        persist_dir: str = VECTOR_DB_DIR) -> Any:
    """
    Create embeddings for the document and store it in ChromaDB.

    Args:
        document_url (str): The URL of the document.
        embedding_fn (Any): The embedding function to use.
        persist_dir (str): The directory to persist the vector store.

    Returns:
        Any: The created vector store.
    """
    try:
        vector_store_path = os.path.join(os.getcwd(), persist_dir)
        start_time = time.time()
        print("No existing vector store found. Creating new one...")
        st.markdown(''' :green[No existing vector store found. Creating new one......] ''')
        document = load_document(document_url)
        documents = split_document(document)
        vector_store = vectorstores.Chroma.from_documents(
            documents=documents,
            embedding=embedding_fn,
            persist_directory=persist_dir
        )
        vector_store.persist()
        print(f"Embedding time: {time.time() - start_time:.2f} seconds")
        st.write(f"Embedding time: {time.time() - start_time:.2f} seconds")
        return vector_store
    except Exception as e:
        st.error(f"Error creating embeddings: {e}")
        return None


def handle_user_interaction(vector_store: Any, chat_model: Any) -> str:
    """
    Handle user interaction to generate a response based on the query.

    Args:
        vector_store (Any): The vector store to use for retrieval.
        chat_model (Any): The chat model to use for generating responses.

    Returns:
        str: The generated response.
    """
    try:
        prompt_template = """
        Use the following pieces of context to answer the question at the end.
        If you do not know the answer, answer 'I don't know', limit your response to the answer and nothing more.

        {context}

        Question: {question}
        """
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": prompt}
        st.markdown(''' :green[Using retrievers to retrieve the data from the database...] ''')
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        st.markdown(''' :green[Answering the query...] ''')
        qachain = chains.RetrievalQA.from_chain_type(
            llm=chat_model,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs=chain_type_kwargs
        )
        qachain.invoke({"query": "what is this about?"})
        print(f"Model warmup complete...")
        st.markdown(''' :green[Model warmup complete...] ''')

        start_time = time.time()
        answer = qachain.invoke({"query": question})
        print(f"Answer: {answer['result']}")
        print(f"Response time: {time.time() - start_time:.2f} seconds")
        st.write(f"Response time: {time.time() - start_time:.2f} seconds")

        return answer['result']
    except Exception as e:
        st.error(f"Error handling user interaction: {e}")
        return "Error generating response."


def getfinalresponse(document_url: str, embedding_type: str, chat_model: str) -> str:
    """
    Main function to load the document, initialize the embeddings, create the vector database, and invoke the model.

    Args:
        document_url (str): The URL of the document.
        embedding_type (str): The type of embedding to use.
        chat_model (str): The chat model to use.

    Returns:
        str: The final response generated by the model.
    """
    try:
        embedding_fn = initialize_embedding_fn(embedding_type)
        if embedding_fn is None:
            return "Error initializing embedding function."

        vector_store = get_or_create_embeddings(document_url, embedding_fn)
        if vector_store is None:
            return "Error creating vector store."

        chat_model_instance = llms.Ollama(base_url=OLLAMA_BASE_URL, model=chat_model)
        return handle_user_interaction(vector_store, chat_model_instance)
    except Exception as e:
        st.error(f"Error in getfinalresponse: {e}")
        return "Error generating final response."


submit = st.button("Generate")

# Generate response
if submit:
    document_url = url_path
    chat_model = model

    with st.spinner("Loading document....🐎"):
        st.write(getfinalresponse(document_url, embedding_type, chat_model))
