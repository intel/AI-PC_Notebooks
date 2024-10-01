import time
from threading import Thread
import streamlit as st
from llama_cpp import Llama
from llama_cpp.llama_chat_format import MoondreamChatHandler
import tempfile
from PIL import Image
import base64

# Create a Streamlit app that displays the response word by word
st.header("Visual-language assistant with SYCL 🐻‍❄️")

# Dropdown to select a model
selected_model = st.selectbox(
    "Please select a model", 
    ("vikhyatk/moondream2", "microsoft/Phi-3-vision-128k-instruct", "Intel/llava-gemma-2b"), 
    index=0
)

# File uploader for image
img_file_buffer = st.file_uploader('Upload a PNG image', type=["jpg", "png", "gif"])

# Input for image URL
url = st.text_input("Enter the URL of the Image:", value="Enter the URL of the Image", key="url_path")

# Display the uploaded image or the image from the URL
if img_file_buffer is not None:
    try:
        image = Image.open(img_file_buffer)
        st.image(image, width=600)  # Manually Adjust the width of the image as per requirement
    except Exception as e:
        st.error(f"Error loading image: {e}")
else:
    st.error("Please provide an image URL or upload an image.")

# Input prompt for the question
question = st.text_input("Enter the question:", value="What's the content of the image?", key="question")

def getfinalresponse(input_text):
    """
    Generate a response based on the input text and image.

    Args:
        input_text (str): The input text or question from the user.

    Yields:
        str: The generated response content word by word.
    """
    try:
        # Create a temporary file if an image is uploaded
        if img_file_buffer is not None:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(img_file_buffer.getvalue())
                file_path = tmp_file.name

            def image_to_base64_data_uri():
                """
                Convert the uploaded image to a base64 data URI.

                Returns:
                    str: The base64 data URI of the image.
                """
                with open(file_path, "rb") as img_file:
                    base64_data = base64.b64encode(img_file.read()).decode('utf-8')
                    return f"data:image/jpg;base64,{base64_data}"

        # Initialize the chat handler with a pre-trained model
        chat_handler = MoondreamChatHandler.from_pretrained(
            repo_id="vikhyatk/moondream2",
            filename="*mmproj*",
        )

        # Initialize the Llama model with the pre-trained model and chat handler
        llm = Llama.from_pretrained(
            repo_id=selected_model,
            filename="*text-model*",
            chat_handler=chat_handler,
            n_gpu_layers=-1,  # Uncomment to use GPU acceleration
            seed=1337,  # Uncomment to set a specific seed
            n_ctx=2048,  # Uncomment to increase the context window
            n_threads=16,
        )

        # Create a chat completion request with the appropriate image URL
        if img_file_buffer is not None:
            response = llm.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": image_to_base64_data_uri()}}
                        ]
                    }
                ],
                stream=True
            )
        else:
            response = llm.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": url}}
                        ]
                    }
                ],
                stream=True
            )

        # Stream and yield the response content word by word
        for chunk in response:
            res = chunk['choices'][0]['delta']
            if 'content' in res:
                word = res['content'].split()
                for token in word:
                    yield token + " "
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Generate response when the button is clicked
if st.button("Generate"):
    with st.spinner("Running....🐎"):
        if not question.strip():
            st.error("Please enter a question.")
        elif not url.strip() and img_file_buffer is None:
            st.error("Please provide an image URL or upload an image.")
        else:
            st.write_stream(getfinalresponse(question))
