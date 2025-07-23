# Image Classification using WebNN with onnxruntime-web

Sample created using [Microsoft WebNN Tutorial](https://learn.microsoft.com/en-us/windows/ai/directml/webnn-tutorial), with these changes:
- Uses ONNX model that is exported from HuggingFace using _optimum-cli_
- labels are parsed from model's _config.json_ file
- HTML UI modified to select images using image selector
- added device selection priority to try in this order: webnn-npu, webnn-gpu, webgpu, wasm, webnn-cpu.
- created _model_export.sh_ script to export any HuggingFace model to ONNX using _optimum-cli_

The sample uses ONNX model exported from HuggingFace to build an image classification system on the web that uses __WebNN with ONNX Runtime Web__. 

| Files | Details
|---|---|
|index.html|HTML for basic UI|
|main.js|main javasvript file to perform image selection and classification using ONNX Runtime Web|
|main_device_priority.js| (optional) same as _main.js_ but with device selection priority added to try webnn-npu first, if not available tries webnn-gpu, then webgpu, wasm, ...|
|model_export.sh|script for linux to export HuggingFace models:<br>- google/mobilenet_v2_1.0_224<br>- facebook/convnextv2-atto-1k-224<br>- microsoft/resnet-18|
|model_export.bat|script for Windows to export HuggingFace models:<br>- google/mobilenet_v2_1.0_224<br>- facebook/convnextv2-atto-1k-224<br>- microsoft/resnet-18|
|google_mobilenet_v2_1.0_224/ |ONNX exported model folder generated from _model_export.sh_ script. The folder contains 3 files: [config.json, model.onnx, preprocessor_config.json]|

Can be tested using the "Live Preview" extension for VSCode

### Exporting HuggingFace models to ONNX

_model_export.sh_ script can be used to export any HuggingFace image classification model to ONNX and can be used by updating model path in _main.js_

#### Instructions for Linux

Make sure conda is installed (install mini-forge) and then run commands below in terminal.

To run the _model_export.sh_ script, first create an virtual environment and then run the script:
```
conda create -n onnx_export python=3.10
conda activate onnx_export
source model_export.sh
```

#### Instructions for Windows

Make sure conda is installed (install mini-forge) and then run commands below in terminal.

To run the _model_export.bat_ script, first create an virtual environment and then run the script:
```
conda create -n onnx_export python=3.10
conda activate onnx_export
model_export.bat
```

#### model_export script details

_model_export.sh_ script will install necessary packages using _pip_ and will use _optimum-cli_ to export HuggingFace models to ONNX.

The pip packages installed are:
- optimum[exporters]
- huggingface_hub==0.25.2

Command to export HuggingFace model to ONNX:
```
optimum-cli export onnx --model {{model-checkpoint-name/model-local-path}} {{output-onnx-directory}}
```

Example command to export HuggingFace model checkpoint to ONNX:
```
optimum-cli export onnx --model google/mobilenet_v2_1.0_224 google_mobilenet_v2_1.0_224
```
- _google/mobilenet_v2_1.0_224_ is the HuggingFace checkpoint model name.
- _google_mobilenet_v2_1.0_224_ is the directory where the ONNX model is exported to

The _model_export.sh_ script has commands to export more that one image-classification models which are commented out, uncomment to export and any of the exported models can be used in the sample code by changing the value of _path_ in _main.js_

