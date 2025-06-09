from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from optimum.intel import OVModelForCausalLM
from transformers import AutoTokenizer, pipeline
import openvino as ov
import os
os.environ['USER_AGENT'] = "SummarizeBot"


def get_device():
    core = ov.Core()
    available_devices = core.available_devices
    for device in available_devices:
        if device.startswith("GPU"):
            return device
    return "CPU"  # Fallback to CPU if no GPU is available


class TextSummarizerEngine:
    """
    A class for managing text summarization and Q&A operations using LLMs and vector stores.

    This class encapsulates the functionality for loading LLMs, processing documents,
    and generating summaries and answers for both web content and PDFs.
    """

    # Prompt Templates for Summarization & QA Bot
    SUMMARY_TEMPLATE = """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
    QUERY_TEMPLATE = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use 10 words maximum and keep the answer as concise as possible in one sentence.
    Always say "thanks for asking!" at the end of the answer.
    {context}
    Question: {question}
    Helpful Answer:"""

    # Embedding model name
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self):
        """Initialize the TextSummarizerEngine with empty attributes."""
        self.model_id = None
        self.model_path = None
        self.llm = None
        self.tokenizer = None

        # Vector store for document processing
        self.vectorstore = None

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=self.EMBEDDING_MODEL)

    def load_model(self, model_id):
        """
        Load and initialize the specified LLM model using OpenVINO optimization.
        """
        self.model_id = model_id

        if model_id == "Meta LLama 2":
            self.model_path = "../models/ov_llama_2"
        elif model_id == "Qwen 7B Instruct":
            self.model_path = "../models/ov_qwen7b"
        else:
            raise ValueError(f"Unsupported model ID: {model_id}")

        # Load the model with OpenVINO optimization
        device = get_device()
        model = OVModelForCausalLM.from_pretrained(self.model_path, device=device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

        # Create a text generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            max_new_tokens=4096,
            device=model.device,
        )

        # Create a LangChain compatible model
        self.llm = HuggingFacePipeline(pipeline=pipe)

    def _process_document(self, loader):
        """
        Process document content from a loader and create a vector store.
        """
        # Load and split the document into chunks
        page_data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=20
        )
        all_splits = text_splitter.split_documents(page_data)

        # Create and return a vector store from the document chunks
        vectorstore = Chroma.from_documents(
            documents=all_splits,
            embedding=self.embeddings
        )
        return vectorstore

    async def process_document(self, source, is_url=True):
        """
        Process a document (URL or PDF) to generate a summary of its content.
        """
        if not self.llm:
            raise ValueError("Model not loaded. Call load_model first.")

        # Create the appropriate loader based on the document type
        if is_url:
            loader = WebBaseLoader(source)
        else:
            loader = PyPDFLoader(source, extract_images=False)

        # Process the document content
        self.vectorstore = self._process_document(loader)

        # Create a prompt for summarization
        prompt = PromptTemplate(
            template=self.SUMMARY_TEMPLATE,
            input_variables=["context"]
        )

        # Create a retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )

        # Generate a summary
        question = "Please summarize the entire content in one paragraph of 100 words"
        summary = qa_chain.invoke(question)["result"]
        start_idx = summary.find("CONCISE SUMMARY:")
        if start_idx != -1:
            summary = summary[start_idx + len("CONCISE SUMMARY:"):].strip()
        else:
            summary = "No summary found."
        return summary

    async def answer_question(self, query):
        """
        Answer a question about previously processed document content.
        """
        if not self.llm or not self.vectorstore:
            raise ValueError("Document content not processed or model not loaded.")

        # Create a prompt for Q&A
        prompt = PromptTemplate(
            template=self.QUERY_TEMPLATE,
            input_variables=["context", "question"]
        )

        # Create a retrieval QA chain
        reduce_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )

        # Generate an answer
        response = reduce_chain.invoke({"query": query})['result']
        start_idx = response.find("Helpful Answer:")
        if start_idx != -1:
            response = response[start_idx + len("Helpful Answer:"):].strip()
        else:
            response = "No answer found."
        return response

    def cleanup(self):
        """Clean up resources when done."""
        if self.vectorstore:
            try:
                self.vectorstore.delete_collection()
            except Exception:
                print("Failed to delete vector store collection")


if __name__ == "__main__":
    # Example usage
    engine = TextSummarizerEngine()
    engine.load_model("Qwen 7B Instruct")

    # Process a document (URL or PDF)
    engine.process_document("https://example.com/document", is_url=True)
    engine.cleanup()
