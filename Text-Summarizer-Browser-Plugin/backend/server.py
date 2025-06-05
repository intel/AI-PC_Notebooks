import tempfile
import warnings
from typing import Literal
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException

from llm_engine import TextSummarizerEngine

# Suppress warnings
warnings.filterwarnings("ignore")

class ModelSelectionRequest(BaseModel):
    model_id: Literal["Meta LLama 2", "Qwen 7B Instruct"]

class UrlRequest(BaseModel):
    url: HttpUrl

# Create FastAPI app instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

engine_instance = None

# Startup event to initialize the engine
@app.on_event("startup")
async def startup_event():
    """Initialize the TextSummarizerEngine when the application starts"""
    global engine_instance
    engine_instance = TextSummarizerEngine()
    print("TextSummarizerEngine initialized on startup")

# Dependency to get the engine
async def get_engine():
    """Dependency to provide the engine to routes that need it"""
    if engine_instance is None:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    return engine_instance

@app.get("/")
async def root():
    return {"message": "The backend server is running. Please use the browser plugin to interact with it."}


@app.post("/select-model")
async def select_model(
    req: ModelSelectionRequest, 
    engine: TextSummarizerEngine = Depends(get_engine)
):
    """
    Model selection function to initialize the model.
    """
    # Load the selected model
    engine.load_model(req.model_id)
    return {"message": f"Model {req.model_id} loaded successfully."}



# Add a cleanup event to free resources when the server shuts down
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources when shutting down."""
    global engine_instance
    if engine_instance:
        engine_instance.cleanup()


@app.post("/process-url")
async def process_url(
    url_req: UrlRequest,
    engine: TextSummarizerEngine = Depends(get_engine)
):
    """
    Fetches URL from the plugin & triggers the URL summarization function.
    """
    try:
        url = str(url_req.url)
        if not url:
            return JSONResponse(content={"message": "No URL provided"}, status_code=400)
        
        # Make sure the model is loaded
        if engine.llm is None:
            return JSONResponse(content={"message": "Model not loaded. Please select a model first."}, status_code=400)
            
        # Process the URL and return summary
        summary = await engine.process_document(url, is_url=True)
        return JSONResponse(content={"message": summary}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": f"Error while processing URL: {str(e)}"}, status_code=400)


@app.post("/upload-pdf")
async def upload_pdf(
    pdf_file: UploadFile = File(...), 
    engine: TextSummarizerEngine = Depends(get_engine)
):
    """
    Once the PDF's uploaded, the PDF Summarization function's triggered.
    """
    if pdf_file.content_type == "application/pdf":
        try:
            # Save uploaded PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                content = await pdf_file.read()
                temp_pdf.write(content)
                temp_pdf_path = temp_pdf.name
                print(f"PDF saved temporarily at: {temp_pdf_path}")

            # Make sure the model is loaded
            if engine.llm is None:
                return JSONResponse(content={"message": "Model not loaded. Please select a model first."}, status_code=400)
                
            # Process the PDF and return summary
            summary = await engine.process_document(temp_pdf_path, is_url=False)
            return JSONResponse(content={"message": summary}, status_code=200) 

        except Exception as e:
            return JSONResponse(content={"message": f"Error processing PDF: {str(e)}"}, status_code=500)

    else:
        return JSONResponse(content={"message": "Invalid file type. Please upload a PDF."}, status_code=400)

@app.post("/query")
async def query(
    query: str,
    engine: TextSummarizerEngine = Depends(get_engine)
):
    try:
        if not query:
            return JSONResponse(content={"message": "No query provided"}, status_code=400)
            
        # Make sure the model and vectorstore are ready
        if engine.llm is None or engine.vectorstore is None:
            return JSONResponse(
                content={"message": "No document processed yet or model not loaded"}, 
                status_code=400
            )
            
        # Get answer to the query
        response_message = await engine.answer_question(query)
        return {"message": response_message}
    except Exception as e:
        return JSONResponse(content={"message": f"Error in Question Answering: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("""
    🎉 FastAPI server is Ready! 🎉
    Your application is now live and waiting for interaction!
    
    **🚀 Essential Step: Activate Your Browser Plugin!**
    
    - This application operates through its dedicated browser extension.
    - To begin, please open your web browser and locate the plugin's icon, which looks like `T`, in your toolbar (it's often in the top-right corner).
    - Click on the `T` icon to access the browser extension
    
    **Having trouble?**
    - Is the plugin loaded? If you haven't already, please load it by following the Readme.md file.
    - Is it enabled? Double-check your browser's extension settings to ensure the plugin isn't disabled.
    - Have you pinned the extension? Pin the extension.
    """)
    uvicorn.run(app, host="0.0.0.0", port=5000)
