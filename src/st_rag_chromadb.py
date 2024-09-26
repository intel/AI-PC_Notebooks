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

# Load the document using document_loaders


def load_document(url):
    print("Loading document from URL...")
    st.markdown(''' :green[Loading document from URL...] ''')
    loader = document_loaders.WebBaseLoader(url)
    return loader.load()


# Split the document into multiple chunks
def split_document(text, chunk_size=3000, overlap=200):
    print("Splitting document into chunks...")
    st.markdown(''' :green[Splitting document into chunks...] ''')
    text_splitter_instance = text_splitter.RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap)
    return text_splitter_instance.split_documents(text)


# Initialize embeddings for these chunks of data. we can use one of the
# below four embedding types

def initialize_embedding_fn(
        embedding_type="huggingface",
        model_name="sentence-transformers/all-MiniLM-l6-v2"):
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

# Create embeddings for these chunks of data and store it in chromaDB


def get_or_create_embeddings(
        document_url,
        embedding_fn,
        persist_dir=VECTOR_DB_DIR):
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
    st.write(f"Embedding time: {time.time() - start_time:.2f} seconds")
    return vector_store
# Create the user prompt and generate the response


def handle_user_interaction(vector_store, chat_model):
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
    # Use retrievers to retrieve the data from the database
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


# Main Function to load the document, initialize the embeddings , create
# the vector database and invoke the model
def getfinalresponse(document_url, embedding_type, chat_model):

    document_url = url_path
    chat_model = model

    embedding_fn = initialize_embedding_fn(embedding_type)
    vector_store = get_or_create_embeddings(document_url, embedding_fn)
    chat_model_instance = llms.Ollama(
        base_url=OLLAMA_BASE_URL, model=chat_model)
    return handle_user_interaction(vector_store, chat_model_instance)


submit = st.button("Generate")


# generate response
if submit:
    if not url_path.strip():
        st.error("Please enter a valid URL.")
    elif not question.strip():
        st.error("Please enter a valid question.")
    else:
        with st.spinner("Loading document....🐎"):
            st.write(getfinalresponse(url_path, embedding_type, model))
