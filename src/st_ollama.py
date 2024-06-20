import ollama
import streamlit as st

st.title("Let's Chat....🐼")

# Load ollama models

model_list = [model["name"] for model in ollama.list()["models"]]
model = st.selectbox("Choose a model from the list", model_list)

if chat_input := st.chat_input("Hi, How are you?"):
    with st.spinner("Running....🐎"):
        with st.chat_message("user"):
            st.markdown(chat_input)

        def generate_response(user_input):
            response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': chat_input,
            },
            ],
            stream=True,
            )    
            for res in response:
                yield res["message"]["content"]            
        st.write_stream(generate_response(chat_input))
        del model
