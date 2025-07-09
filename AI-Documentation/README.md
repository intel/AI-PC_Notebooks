# AI documentation

Repository that provides code sample for automatic documentation generation using AI (LLM local model) with LammaCpp and tree-sitter

## Installation

Project is written in a python language. Before running please make sure you have python installed.
List of all necessary packages is in a `requirements.txt` file. To install them please follow command below:

```bash
pip install -r requirements.txt
```

You also need to install LLaMa Cpp with SYCL backend. To compile LLama Cpp with SYCL backend follow the commend below:

* Linux 
  ```
  CMAKE_ARGS="-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx" pip install llama-cpp-python
  ```
* Windows
  ```
  set CMAKE_GENERATOR=Ninja
  set CMAKE_C_COMPILER=cl
  set CMAKE_CXX_COMPILER=icx
  set CXX=icx
  set CC=cl
  set CMAKE_ARGS="-DGGML_SYCL=ON -DGGML_SYCL_F16=ON -DCMAKE_CXX_COMPILER=icx -DCMAKE_C_COMPILER=cl"
  pip install llama-cpp-python --force --no-cache-dir --verbose
  ```

To run this application you also need to download LLM model manually. To do that you can use Hugging Face hub download methods:

1. With CLI using `download` method providing repository and file you want to download, then local path where file should be located:
  ```bash
  huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF Meta-Llama-3.1-8B-Instruct-Q6_K.gguf ./models/Meta-Llama-3.1-8B-Instruct-Q6_K.gguf
  ```

2. Directly in Python code:
  ```python
  from huggingface_hub import hf_hub_download

  hf_hub_download(
    repo_id="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
    filename="Meta-Llama-3.1-8B-Instruct-Q6_K.gguf",
      local_dir="./models"
  )
  ```

## Run application

To run application you can use the following command:

```bash
python3 -m aidocapp PATH_TO_DIR_OR_FILE --local_model ./models/Meta-Llama-3.1-8B-Instruct-Q6_K.gguf
```
