import ollama
import streamlit as st

# Set the title of the Streamlit app
st.title("Let's Chat....🐼")

# Function to load Ollama models
def load_models():
    try:
        model_list = [model["name"] for model in ollama.list()["models"]]
        return model_list
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return []

# Function to generate response from Ollama
def generate_response(user_input, model):
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': user_input,
                },
            ],
            stream=True,
        )
        for res in response:
            yield res["message"]["content"]
    except Exception as e:
        st.error(f"Error generating response: {e}")

# Load Ollama models
model_list = load_models()

# Validate if models are loaded
if model_list:
    model = st.selectbox("Choose a model from the list", model_list)
else:
    st.stop()  # Stop execution if models are not loaded

# Get user input from chat
chat_input = st.chat_input("Hi, How are you?")

# Validate user input
if chat_input:
    with st.spinner("Running....🐎"):
        with st.chat_message("user"):
            st.markdown(chat_input)

        # Stream the generated response
        st.write_stream(generate_response(chat_input, model))
