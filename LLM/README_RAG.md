# Building a Retrieval-Augmented Generation (RAG) System on AI PCs

This notebook demonstrates how to run LLM inference for a Retrieval-Augmented Generation (RAG) application locally on an AI PC. It is optimized for Intel® Core™ Ultra processors, utilizing the combined capabilities of the CPU, GPU, and NPU for efficient AI workloads.

## Installing Prerequisites
### Windows:
The following software are to be installed prior to the setting up of Llamacpp-python SYCL backend
1. **GPU Drivers installation**
    - Download and Install the GPU driver from Intel® Arc™ & Iris® Xe Graphics - Windows* [link](https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html)
    - (Optional) Download and Install the NPU driver from [here](https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html)
    - For NPU, if the Neural processor is not available, Check the PCI device to update the driver.
      Follow this document [NPU_Win_Release_Notes_v2540.pdf](https://downloadmirror.intel.com/825735/NPU_Win_Release_Notes_v2540.pdf)

    **IMPORTANT:** Reboot the system after the installation

2. **CMake for windows**\
Download and install the latest CMake for Windows from [here](https://cmake.org/download/)

3. **Microsoft Visual Studio 2022 community version**\
Download and install VS 2022 community from [here](https://visualstudio.microsoft.com/downloads/)\
**IMPORTANT:** Please select "Desktop Development with C++" option while installing Visual studio

4. **Git for Windows**\
Download and install Git from [here](https://git-scm.com/downloads/win)

5. **Intel oneAPI Base Toolkit for Windows**\
Download and install Intel oneAPI Base Toolkit for Windows from [here](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html?operatingsystem=windows&windows-install-type=offline)

**Note: Its important you need to download the 2025.0.1 version(older)of the oneAPI Basekit as llamacpp python is not yet compatible with latest oneAPI Basekit.
When downloading the installer please select the "Choose a Version" dropdown and select 2025.0.1**

7. **Miniconda for Windows**\
Download and install Miniconda from [here](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)

### Linux:

1. **GPU Drivers installation**\
Download and install the GPU drivers from [here](https://dgpu-docs.intel.com/driver/client/overview.html)

2. **Miniconda for Linux**\
Download, install the Miniconda using the below commands. 
    ```
    wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
    bash Miniforge3-$(uname)-$(uname -m).sh
    ```
    Replace </move/to/miniforge3/bin/folder> with your actual Miniforge bin folder path and run the cd command to go there. Initialize the conda environment and restart the terminal.
    ```
    cd </move/to/miniforge3/bin/folder>
    ```
    ``` 
    ./conda init 
    ```

3. **Intel oneAPI Base Toolkit for Linux**\
Download and install Intel oneAPI Base Toolkit for Linux from [here](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html?packages=oneapi-toolkit&oneapi-toolkit-os=linux&oneapi-lin=offline)

4. **CMake and Git for Linux**\
Install the CMake using below commands:
    - For Debian/Ubuntu-based systems:
      ```
      sudo apt update && sudo apt -y install cmake git
      ```
    - For RHEL/CentOS-based systems:
      ```
      sudo dnf update && sudo dnf -y install cmake git
      ```
 
## Setting up environment and LlamaCPP-python GPU backend

Open a new Mini-forge terminal and perform the following steps:

1. **Create and activate the conda environment**
   ```
   conda create -n llamacpp python=3.11 -y
   conda activate llamacpp
   ```
2. **Initialize oneAPI environment**\
   On Windows:
   ```
   @call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64 --force
   ```
   On Linux:
   ```
   source /opt/intel/oneapi/setvars.sh --force
   ```
3. **Set the environment variables and install Llamacpp-Python bindings**\
   On Windows:
   ```
   set CMAKE_GENERATOR=Ninja
   set CMAKE_C_COMPILER=cl
   set CMAKE_CXX_COMPILER=icx
   set CXX=icx
   set CC=cl
   set CMAKE_ARGS="-DGGML_SYCL=ON -DGGML_SYCL_F16=ON -DCMAKE_CXX_COMPILER=icx -DCMAKE_C_COMPILER=cl"
   pip install llama-cpp-python==0.3.8 -U --force --no-cache-dir --verbose
   ```
   On Linux:
   ```
   CMAKE_ARGS="-DGGML_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx" pip install llama-cpp-python==0.3.8 -U --force --no-cache-dir --verbose
   ```
4. **Install the required pip packages**
   ```
   pip install -r rag/requirements.txt
   ```
5. **Install a ipykernel to select the llamacpp environment**
   ```
   python -m ipykernel install --user --name=llamacpp
   ```


6. **Launch the Jupyter notebook using the below command**
   ```
   jupyter lab
   ```
   - Open the [LLM](./09_rag_langchain.ipynb) in the jupyter notebook, select the llamacpp kernel and run the code cells one by one in the notebook.
   
