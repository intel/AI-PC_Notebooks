// Original source from https://learn.microsoft.com/en-us/windows/ai/directml/webnn-tutorial
// Modified some functions
// Used exported ONNX model and get labels from exported config.json

'use strict';

  async function classifyImage(pathToImage){
    var imageTensor = await getImageTensorFromPath(pathToImage); // Convert image to a tensor
    var predictions = await runModel(imageTensor); // Run inference on the tensor
    console.log(predictions); // Print predictions to console
    // Display result
    document.getElementById("output").innerHTML = predictions[0].name; // Display prediction in HTML
  }

  async function getImageTensorFromPath(path, width = 224, height = 224) {
    var image = await loadImagefromPath(path, width, height); // 1. load the image
    var imageTensor = imageDataToTensor(image); // 2. convert to tensor
    return imageTensor; // 3. return the tensor
  } 

  async function loadImagefromPath(path, resizedWidth, resizedHeight) {
    var imageData = await Jimp.read(path).then(imageBuffer => { // Use Jimp to load the image and resize it.
      return imageBuffer.resize(resizedWidth, resizedHeight);
    });
    return imageData.bitmap;
  }

  function imageDataToTensor(image) {
    var imageBufferData = image.data;
    let pixelCount = image.width * image.height;
    const float32Data = new Float32Array(3 * pixelCount); // Allocate enough space for red/green/blue channels.

    // Loop through the image buffer, extracting the (R, G, B) channels, rearranging from
    // packed channels to planar channels, and converting to floating point.
    for (let i = 0; i < pixelCount; i++) {
      float32Data[pixelCount * 0 + i] = imageBufferData[i * 4 + 0] / 255.0; // Red
      float32Data[pixelCount * 1 + i] = imageBufferData[i * 4 + 1] / 255.0; // Green
      float32Data[pixelCount * 2 + i] = imageBufferData[i * 4 + 2] / 255.0; // Blue
      // Skip the unused alpha channel: imageBufferData[i * 4 + 3].
    }
    let dimensions = [1, 3, image.height, image.width];
    const inputTensor = new ort.Tensor("float32", float32Data, dimensions);
    return inputTensor;
  }

  async function runModel(preprocessedData) { 

    // Configure WebNN.
    const path = "./google_mobilenet_v2_1.0_224/"
    const modelPath = path + "model.onnx";
    const modelConfig = path + "config.json";
    const devicePreference = "gpu"; // Other options include "npu" and "cpu".
    /*
    const options = {
	    executionProviders: [{ name: "webnn", deviceType: devicePreference, powerPreference: "default" }],
      freeDimensionOverrides: {"batch": 1, "channels": 3, "height": 224, "width": 224}
      // The key names in freeDimensionOverrides should map to the real input dim names in the model.
      // For example, if a model's only key is batch_size, you only need to set
      // freeDimensionOverrides: {"batch_size": 1}
    };
    modelSession = await ort.InferenceSession.create(modelPath, options); 
    */

    // TODO: Device Priority not working: find work-around or fix
    //       ort.InferenceSession.create error is not caught to continue
    const devices = ['npu', 'gpu', 'cpu'];
    let modelSession = null;

    for (const device of devices) {
      try {
        console.log(`Trying device: ${device}`);
        modelSession = await ort.InferenceSession.create(modelPath, {
          executionProviders: [{ name: "webnn", deviceType: device, powerPreference: "default" }],
          freeDimensionOverrides: {"batch": 1, "channels": 3, "height": 224, "width": 224}
        });
        console.log(`Using device: ${device}`);
        break;
      } catch (e) {
        console.warn(`Device ${device} not available:`, e.message || e);
      }
    }

    // Create feeds with the input name from model export and the preprocessed data. 
    const feeds = {}; 
    feeds[modelSession.inputNames[0]] = preprocessedData; 
    // Run the session inference.
    const outputData = await modelSession.run(feeds); 
    // Get output results with the output name from the model export. 
    const output = outputData[modelSession.outputNames[0]]; 
    // Get the softmax of the output data. The softmax transforms values to be between 0 and 1.
    var outputSoftmax = softmax(Array.prototype.slice.call(output.data)); 
    // Get the top 5 results.
    var results = await topLabels(outputSoftmax, modelConfig, 5);
    return results; 
  }

  // For debugging
  window.addEventListener("unhandledrejection", event => {
    console.error("Unhandled promise rejection:", event.reason);
  });

  // The softmax transforms values to be between 0 and 1.
function softmax(resultArray) {
    // Get the largest value in the array.
    const largestNumber = Math.max(...resultArray);
    // Apply the exponential function to each result item subtracted by the largest number, using reduction to get the
    // previous result number and the current number to sum all the exponentials results.
    const sumOfExp = resultArray 
      .map(resultItem => Math.exp(resultItem - largestNumber)) 
      .reduce((prevNumber, currentNumber) => prevNumber + currentNumber);
  
    // Normalize the resultArray by dividing by the sum of all exponentials.
    // This normalization ensures that the sum of the components of the output vector is 1.
    return resultArray.map((resultValue, index) => {
      return Math.exp(resultValue - largestNumber) / sumOfExp
    });
  }

  async function topLabels(classProbabilities, modelConfig, k=5) {
    const config_json  = await fetch(modelConfig).then(function(response) { return response.json(); })
    const labels = config_json.id2label;

    const probs = _.isTypedArray(classProbabilities)
      ? Array.prototype.slice.call(classProbabilities)
      : classProbabilities;
  
    const sorted = _.reverse(
      _.sortBy(
        probs.map((prob, index) => [prob, index]),
        probIndex => probIndex[0]
      )
    );
  
    const topK = _.take(sorted, k).map(probIndex => {
      return {
        index: parseInt(probIndex[1].toString(), 10),
        name: labels[probIndex[1]],
        probability: probIndex[0]
      }
    });
    return topK;
  }

  // Customized Image selector in HTML
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
      classifyImage(document.getElementById('inputImage').src);
    });
  });


