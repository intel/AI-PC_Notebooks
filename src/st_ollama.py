import ollama
import streamlit as st
from typing import List, Generator

st.title("Let's Chat....🐼")


def fetch_model_list() -> List[str]:
    """
    Fetch the list of models from ollama and validate it.

    Returns:
        List[str]: A list of model names.
    """
    try:
        models_response = ollama.list()
        if "models" in models_response and isinstance(models_response["models"], list):
            return [model["name"] for model in models_response["models"] if "name" in model]
        else:
            st.error("Invalid response format from ollama.")
            return []
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []


def generate_response(user_input: str, model: str) -> Generator[str, None, None]:
    """
    Generate a response from the ollama chat model.

    Args:
        user_input (str): The user's input message.
        model (str): The selected model name.

    Yields:
        str: The response message content.
    """
    try:
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': user_input,
            },
        ], stream=True)
        for res in response:
            yield res["message"]["content"]
    except Exception as e:
        st.error(f"Error generating response: {e}")
        yield "Error generating response."


# Load ollama models
model_list = fetch_model_list()
if model_list:
    model = st.selectbox("Choose a model from the list", model_list)
else:
    model = None

if model and (chat_input := st.chat_input("Hi, How are you?")):
    with st.spinner("Running....🐎"):
        with st.chat_message("user"):
            st.markdown(chat_input)

        st.write_stream(generate_response(chat_input, model))
        del model
