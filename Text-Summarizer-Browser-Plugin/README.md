# Text summarizer browser Plugin Sample

A plug-and-play Chrome extension seamlessly integrates with Flask and leverages an OpenVINO backend for fast and efficient summarization of webpages (via URL) and PDFs (via upload). Powered by LangChain tools, it handles advanced tasks like text splitting and vectorstore management to deliver accurate and meaningful summaries.

This Chrome extension acts as the immediate user gateway, offering a minimalist interface right in the browser's toolbar that lets users instantly trigger summarization. It's designed to efficiently capture the required input, whether it's a webpage's URL or content from an uploaded PDF, and securely send this data to the Flask server for further processing.

## Contents
- [Sample Workflow](./Readme.md#sample-workflow)
- [Prerequisites](./Readme.md#prerequisites)
- [Sample Structure](./Readme.md#sample-structure)
- [Run the `Text Summarizer Browser Plugin` Sample](./Readme.md#run-the-text-summarizer-browser-plugin-sample)
  - [Setup the environment with uv](./Readme.md#setup-the-environment-with-uv)
  - [Load this `Text Summarizer` extension](./Readme.md#load-this-text=summarizer-extension)
    - [Contens of `extension` directory](./Readme.md#contents-of-extension-directory)
    - [Load an unpacked extension](./Readme.md#load-an-unpacked-extension)
    - [Pin the extension](./Readme.md#pin-the-extension)
  - [Run the sample](./Readme.md#run-the-sample)
    - [Steps to follow via Jupyter Notebook](./Readme.md#steps-to-follow-via-jupyter-notebook)
    - [Steps to follow via Terminal](./Readme.md#steps-to-follow-via-terminal)
    - [Interact with `Text Summarizer Browser Plugin`](./Readme.md#interact-with-text-summarizer-browser-plugin)
  

## Sample Workflow

- This architecture is split into two main components: a lightweight **Chrome extension** and a powerful **Flask server**.
- The **Chrome extension** serves as the user's direct interface, enabling them to simply click a button to initiate summarization of the current webpage or to upload a PDF directly from their browser.
- Once activated, it securely sends the webpage URL or the uploaded PDF content to the Flask server.
- This **Flask server**, acting as the intelligent backend, processes the request, orchestrates the summarization using the OpenVINO backend and LangChain tools, and then sends the concise summary back to the extension for display.
- This clear separation of concerns ensures a responsive user experience within the browser while offloading heavy computational tasks to a dedicated and scalable server.
  
<img width="1000" alt="image" src="./assets/Text-Summarizer-Overview.png">

## Pre-requisites

| Optimized for | Description                                                                                                                                                                                      |
| :------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OS            | Windows 11 64-bit (22H2, 23H2) and newer or Ubuntu* 22.04 64-bit (with Linux kernel 6.6+) and newer                                                                                              |
| Hardware      | 1. [Intel® GPU drivers from Intel® Arc™ & Iris® Xe Graphics for Windows](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html) or [Linux GPU drivers](https://dgpu-docs.intel.com/driver/client/overview.html) <br> 2. NPU(Optional): [Intel® NPU Driver for Windows](https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html) or [Linux NPU Driver](https://github.com/intel/linux-npu-driver/releases)  <br> 3. Intel® Core™ Ultra Processors                                                                                                                                                                             |
| Software      | 1. [Intel® GPU drivers from Intel® Arc™ & Iris® Xe Graphics for Windows](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html), <br> 2. [uv](https://docs.astral.sh/uv/) |
| Browsers      | [Google Chrome](https://www.google.com/chrome/dr/download/?brand=MRUS&ds_kid=43700079286123654&gad_source=1&gclid=EAIaIQobChMI0J3fybvSigMV5dXCBB1TDARCEAAYASAAEgL36_D_BwE&gclsrc=aw.ds) & [Microsoft Edge](https://www.microsoft.com/en-us/edge/download?form=MA13FJ)


## Sample Structure

The directory contains:
- **backend:** Includes `code.py` and `server.py` for processing text from webpages or PDFs and managing Flask-related operations.
- **extension:** Contains `manifest.json` for the Chrome extension along with `popup.html`, `popup.js`, and `style.css` for the user interface. These files are used to load an unapcked extension.
- **`TextSummarizerPlugin.ipynb`:** Notebook which processes text from webpages or PDFs and manages Flask-related operations.


## Run the `Text Summarizer Browser Plugin` Sample:

### Setup Environment with `uv`:
The sample uses [uv](https://docs.astral.sh/uv/) for environment management. 
> Steps to install `uv` are as follows. Refer [this documentation](https://docs.astral.sh/uv/getting-started/installation/) this for more information.
> </br> **Windows:** </br>
> ```bash
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```
> 
> </br> **Linux:** </br>
> </br> Use curl to download the script and execute it with sh:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
>
> </br> If your system doesn't have curl, you can use wget:
> ```bash
> wget -qO- https://astral.sh/uv/install.sh | sh
> ```
   
1. In a terminal, navigate to `Text Summarizer Browser Plugin Sample` folder:
   ```bash
   cd <path/to/folder>
   ```
2. Sync project dependencies:
   ```bash
   uv sync
   ```
> **NOTE:** Run the below command if you face any dependency issues:
> ```bash
>   uv clean
> ```
### Load this `Text Summarizer` extension

1. **Contents of `extension` directory**
   - [`extension` directory](./extension) consists of files, i.e. `manifest.json`, `popup.html`, `popup.js` and `style.css`, used to load an unpacked extension.

2. **Load an unpacked Extension:**
   - To load an unpacked extension in developer mode:
        - Go to the Extensions page by entering **chrome://extensions** in a new tab. (By design chrome:// URLs are not linkable.)
             - Alternatively, **click the Extensions menu puzzle button and select Manage Extensions** at the bottom of the menu.
             - Or, click the Chrome menu, hover over More Tools, then select Extensions.
        - Enable **Developer Mode** by clicking the toggle switch next to Developer mode.
        - Click the **Load unpacked** button and select the `extension directory`.
        - Refer to [Chrome’s development documentation](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked) for further details.
     
    <img width="389" alt="image" src="https://github.com/user-attachments/assets/c276f522-6f03-4aac-91ff-d38faf8c1f67">
     

3. **Pin the Extension:**

   Pin your extension to the toolbar for a quick access to your extension.
   
   <img width="389" alt="image" src="https://github.com/user-attachments/assets/1bcc1571-b2d6-4ece-a3ca-c435733436b5">
 

### Run the Sample
Below are the steps to run the plugin from Jupyter Notebook **OR** Terminal.

#### **Steps to follow via Jupyter Notebook:**
Once the environment is created, we can run the plugin via [TextSummarizerPlugin.ipynb](./TextSummarizerPlugin.ipynb). Please follow the below steps to open the jupyter notebook:
1. Launch Jupyter Notebook:
   ```
   uv run jupyter lab
   ```
2. Select the default **ipykernel** kernel.
3. Run all the cells one by one.
4. The last cell at the end of the notebook launches the flask server.
5. Once the flask server is running, open Chrome Browser & click on the pinned text-summarizer

<div class="alert alert-block alert-warning" align="center">OR</div>

#### **Steps to follow via Terminal:**
1. **Download and Convert the Huggingface Model to OpenVINO IR Format:**
   - Log in to Huggingface:
     ```
     huggingface-cli login
     ```
   - Generate a token from Huggingface. For private or gated models, refer to [Huggingface documentation](https://huggingface.co/docs/hub/en/models-gated).
   - Convert the model using `optimum-cli`by creating a directory named **models** and saving the models inside it:
     ```
     mkdir models
     cd models
     uv run optimum-cli export openvino --model meta-llama/Llama-2-7b-chat-hf --weight-format int4 ov_llama_2
     uv run optimum-cli export openvino --model Qwen/Qwen2-7B-Instruct --weight-format int4 ov_qwen7b
     
     ```
     >**Note**: [Raise access request](https://www.llama.com/llama-downloads) for Llama models as it is a gated repository.
    

2. **Start the Flask Server:**
   - In one terminal, navigate to the backend folder:
     ```
     cd ./backend
     uv run server.py
     ```
     This step would launch a flask server in browser extension

### Interact with `Text Summarizer Browser Plugin`
1. **Open Chrome Extension in Browser:**
   - Click on the pinned extension of this text summarizer plugin.
   - Plugin UI looks as follows:

      <img width="286" alt="image" src="https://github.com/user-attachments/assets/37349acc-ff37-437b-928a-673ca4ad3986">

   
2. **Select an OpenVINO Model:**
   - Choose an OpenVINO IR format model previously converted from Huggingface.

     <img width="286" alt="image" src="https://github.com/user-attachments/assets/953050c9-c64c-4ce6-831d-626a52547d0b">


3. **Interact with the UI:**
   - Choose either **Web Page** or **PDF** post selecting one of the converted OV models:

     <img width="285" alt="image" src="https://github.com/user-attachments/assets/065022e9-c9a2-474c-ae4e-5a2f298a9934">


     - **Web Summarizer:**
       1. Enter the URL of the webpage to summarize.
       2. Click the "Summarize" button.
       3. After summarization, the text appears, and users can ask follow-up questions.

          <img width="287" alt="image" src="https://github.com/user-attachments/assets/5f308ad3-b5bc-4b3e-9d29-b8002dc88e29">



     - **PDF Summarizer:**
       1. Upload a PDF file.
       2. Click "Upload & Summarize."
       3. After summarization, the text appears, and users can ask additional questions.

          <img width="290" alt="image" src="https://github.com/user-attachments/assets/4d6e3ce0-1650-4cd0-a073-0e84891518a3">
      
       4. Sample output post summarization.
          
          <img width="300" alt="image" src="https://github.com/user-attachments/assets/ea05eca2-fa53-4b17-9c85-67a692607376">


4. **Reload the Page:**  
   - Refresh the webpage or re-open the plugin to restart.
