# transformers.js

transformers.js is designed to be functionally equivalent to Hugging Face's transformers python library.

transformers.js uses ONNX Runtime Web to run models in the browser. 

You can convert any pretrained PyTorch, TensorFlow, and other models to ONNX using Optimum tools.

Learn more about [transformers.js](https://huggingface.co/docs/transformers.js/)

# WebNN transformers.js Samples

| Files | Details
|---|---|
| index.html | Image Classification Web App using transformers.js that will use model directly from HuggingFace|
| index_device_priority.html | Image Classification Web App using transformers.js that will use model directly from HuggingFace and tried multiple backends until successful like: webnn-npu, webnn-gpu, webgpu, wasm,... |
| index_local_model.html | Image Classification Web App using transformers.js that will use locally stored model file, the local ONNX model files are stored in 'Xenova_resnet-18' folder|

# WebNN using transformers.js Tutorial

This tutorial will show you how to create a Web App that uses WebNN with transformers.js to build an image classification system on the web that uses on-device GPU. This example will use _Xenova/resnet-18_ ONNX model from HuggingFace to classify images.

## Setup Environment

1. Launch Chrome or Edge browser, enable WebNN by navigating to "chrome:\\\\flags", search for "webnn", set to enabled and restart as prompted.
2. Install Microsoft VSCode
3. Launch VSCode and install the "Live Preview" extension for VSCode.
4. Open a blank folder for your image classification app

## Step 1: Initialize the web app

1. Create a new index.html file. Add the following boilerplate code to your index.html:
```
<!DOCTYPE html>
<html>
  <head>
    <script type="module">
         
    </script>
  </head>
  <body>
    <h1>WebNN</h1>
    <h3>Image Classification with transformers.js</h3>

  </body>
</html>
```
2. Verify the boilerplate code by right-click and selecting the "Show Preview" button, then copy the URL and paste in external browser.

## Step 2: Build UI elements for the Image Classification App

1. Create a Image Selector, Image element, Button and element for printing output. Replace the existing code within <body> element with the following elements:
```
    <h1>WebNN</h1>
    <h3>Image Classification with transformers.js</h3>
    <p><input type='file' id='imageSelector' accept='image/*' /></p>
    <div><img id="inputImage" src="" width="400"></div> 
    <button id="classifyImage" hidden type="button">Classify Image</button> 
    <p id="log"></p>
    <h2 id="output"></h2>
```
2. Next, lets add javascript event listeners to the Image Selector and Button, add the following code within the <script> tag of your HTML page:
```
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('imageSelector').addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
          document.getElementById('inputImage').src = URL.createObjectURL(files[0]);
          document.getElementById('classifyImage').removeAttribute('hidden');
        }
      });
      document.getElementById('classifyImage').addEventListener('click', (e) => {
        document.getElementById("output").innerHTML = '';
        classify();
      });
    });  
```
3. This should allow you to select a test image, and the image should show up on the page, the "Classify" button should appear. Test this on the browser.

## Step 3: Setup transformers.js Image Classifier

1. Import pipeline from transformers.js by adding the following code within the <script> tag:
```
    import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers';
```

2. Add the classify() function code to the <script> tag, which has three things:
   - setup transformers pipeline with model from huggingface, specify webnn as execution providor, device as gpu and data type.
   - run inference by calling the classifier with image path as input
   - parse the output and display in html element
```
    async function classify() {
      // Setup transformers pipline: model, ep, device, dtype
      document.getElementById("log").innerHTML = 'Loading Model... ';
      const classifier = await pipeline('image-classification', 'Xenova/resnet-18', {
        dtype: 'q8',
        device: 'webnn-gpu',
      });
      // Run inference
      document.getElementById("log").innerHTML += 'Running Inference... ';
      var input = document.getElementById('inputImage').src;
      const output = await classifier(input);
      document.getElementById("log").innerHTML += 'Done';
      // Display output
      document.getElementById("output").innerHTML = output[0].label
      console.log(output);
    };
```

3. Your Web App is complete, test on browser by selecting an image and click the "Classify" button, this should download the model from hugging face and will do the inference on your GPU using WebNN in the browser. 

The final code of this tutorial is available here: [index_huggingface_model.html](index_huggingface_model.html)

## Step 4: Change to use locally stored model file (Optional)

You can also modify this code so that the web app will use locally stored model file instead of accessing model from HuggingFace checkpoint. 

To do this, download the model from HuggingFace by clonning the checkpoint to project folder. 
```
git clone https://huggingface.co/Xenova/resnet-18/
```

Add the following code to allow local model access:

```
    import { env, pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers';

    // Allow local model
    env.allowLocalModels = true
    env.allowRemoteModels = false
    env.localModelPath = window.location.href.substring(0, window.location.href.lastIndexOf('/'))
```
change the HuggingFace checkpoint name to local model folder name:
```
CHANGE:

const classifier = await pipeline('image-classification', 'Xenova/resnet-18', {

TO:

const classifier = await pipeline('image-classification', 'resnet-18', {
```

The final code of this version is available here: [index_local_model.html](index_local_model.html)

END OF TUTORIAL

# Setting execution provider, device type and data type in transformers.js

The Execution Provider and device type is setup by setting ___device___ = `webnn_gpu` | `webnn_npu` | `webnn_cpu` | `webnn`

The data type for ONNX model is specified by setting  ___dtype___ = `fp32` | `fp16` | `int8` | `uint8` |`q8` | `q4` | `q4f16` | `bnb4`

For the ___dtype___ to work, corresponding ONNX model files should exist in `{model_name}/onnx` folder. The ONNX model quantization can be done by using optimum tools.
| dtype | onnx model file name
|---|---|
|fp32|model.onnx|
|fp16|model_fp16.onnx|
|q8|model_quantized.onnx|
|int8|model_int8.onnx|
|uint8|model_uint8.onnx|
|q4|model_q4.onnx|
|q4f16|model_q4f16.onnx|
|bnb4|model_bnb4.onnx|
