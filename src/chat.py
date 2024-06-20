import os

os.environ["SYCL_CACHE_PERSISTENT"]="1"
os.environ["BIGDL_LLM_XMX_DISABLED"]="1"

import threading

import streamlit as st

from ipex_llm.transformers import AutoModelForCausalLM
from transformers import AutoTokenizer, GenerationConfig, TextIteratorStreamer
import torch


MODEL_CACHE = {}


def save_model_thread(model, model_path):
    model.save_low_bit(model_path)
    print(f"Model saved to {model_path}")


def warmup_model(model, tokenizer):
    question = "Hello, how are you?"
    tokenizer.pad_token = tokenizer.eos_token
    if model.name_or_path.startswith("microsoft"):
        prompt = f"<|user|>\n{question}<|end|>\n<|assistant|>"
    else:
        prompt = "user: {prompt}\n\nassistant:".format(prompt=question)
    dummy_input = tokenizer(prompt, return_tensors="pt").to("xpu")
    generation_config = GenerationConfig(use_cache=True,
                                        top_k=50,
                                        top_p=0.95,
                                        temperature=0.7, do_sample=True,
                                        )
    _ = model.generate(**dummy_input, generation_config=generation_config)
    print("Model warmed up successfully!")


def load_model(model_name: str = "Qwen/Qwen-1_8B-Chat"):
    if model_name in MODEL_CACHE:
        return MODEL_CACHE[model_name]

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model_path = f"./model_local_cache/{model_name}"

    if os.path.exists(model_path):
        print(f"Loading model from {model_path}")
        model = AutoModelForCausalLM.load_low_bit(
            model_path, cpu_embedding=True, trust_remote_code=True
        )
    else:
        print(f"Loading model from {model_name}")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            load_in_4bit=True,
            cpu_embedding=True,
            trust_remote_code=True
        )
        save_model_thread(model, model_path)

    model = model.to("xpu")

    MODEL_CACHE[model_name] = (model, tokenizer)
    print("Model loaded successfully!")
    return model, tokenizer


def get_response(model, tokenizer, input_text: str):
    question = input_text
    tokenizer.pad_token = tokenizer.eos_token
    if model.name_or_path.startswith("microsoft"):
        prompt = f"<|user|>\n{question}<|end|>\n<|assistant|>"
    else:
        prompt = "user: {prompt}\n\nassistant:".format(prompt=question)

    with torch.inference_mode():
        input_ids = tokenizer(prompt, return_tensors="pt").to("xpu")
        streamer = TextIteratorStreamer(
            tokenizer, skip_prompt=False, skip_special_tokens=True
        )

        generation_config = GenerationConfig(
            use_cache=True, top_k=50, top_p=0.95,
            temperature=0.7, do_sample=True,
        )

        kwargs = dict(
            input_ids,
            streamer=streamer,
            max_new_tokens=256,
            generation_config=generation_config,
        )
        thread = threading.Thread(target=model.generate, kwargs=kwargs)
        thread.start()
    return streamer


def main():
    if "model" not in st.session_state:
        st.session_state.model = None
    if "tokenizer" not in st.session_state:
        st.session_state.tokenizer = None

    st.header("Lets chat... 🐻‍❄️")
    selected_model = st.selectbox(
        "Please select a model", ("Qwen/Qwen-1_8B-Chat", "microsoft/Phi-3-mini-4k-instruct")
    )

    if st.button("Load Model"):
        with st.spinner("Loading..."):
            st.session_state.model, st.session_state.tokenizer = load_model(
                model_name=selected_model
            )
            if (
                st.session_state.model is not None
                and st.session_state.tokenizer is not None
            ):
                st.success("Model loaded successfully!")
                st.info("Warming up the model...")
                warmup_model(st.session_state.model, st.session_state.tokenizer)
                st.success("Model warmed up and ready to use!")
            else:
                st.error("Failed to load the model.")

    chat_container = st.container()
    with chat_container:
        st.subheader("Chat")
        input_text = st.text_input("Enter your input here...")
        if st.button("Generate"):
            if st.session_state.model is None or st.session_state.tokenizer is None:
                st.warning("Please load the model first.")
            else:
                with st.spinner("Running....🐎"):
                    streamer = get_response(
                        st.session_state.model, st.session_state.tokenizer, input_text
                    )
                    st.write_stream(streamer)


if __name__ == "__main__":
   main()
