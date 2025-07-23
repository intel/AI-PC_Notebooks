# WebNN
WebNN content for trainings and workshops, includes basics of getting started with WebNN application developement, WebNN samples using different JS-frameworks and also direct WebNN API access. Finally a demo showcasing real-world usage of WebNN inference in WebApp.

## Getting Started

Simple WebNN examples to get started with understanding WebNN and try on Browser. 

| file | details |
|---|---|
| [webnn_enable.html](getting-started/01_webnn_enable.html) | Checks if WebNN is enabled or not in browser |
| [webnn_devices.html](getting-started/02_webnn_devices.html) | Checks which of the WebNN devices (npu, gpu, cpu) are available |
| [webnn_device_select.html](getting-started/03_webnn_device_select.html) | Shows how to select a device to use WebNN |
| [webnn_compute.html](getting-started/04_webnn_compute.html) | Selects a device and uses WebNN to do simple computation |
| [webnn_compute_large.html](getting-started/05_webnn_compute_large.html) | Uses WebNN to do large computation and check device usage |

## WebNN Samples

Simple WebNN samples showcasing AI inference using WebNN that can be run on Browser

|Sample Name | Details|
|---|---|
|[image_classification_onnx](webnn-samples/image_classification_onnx)|The sample uses __WebNN with ONNX Runtime Web__ library to build an image classification system on the web that uses ONNX model exported from HuggingFace.|
|[image_classification_transformers.js](webnn-samples/image_classification_transformers.js)|The sample uses __transformers.js library__ to build an image classification system on the web that uses model directly from HuggingFace or local model|
|[image_classification_webnn](webnn-samples/image_classification_webnn)|The sample uses __WebNN API directly__ to build an image classification system on the web that uses MobileNetV2 model.|


## WebNN Demos

WebApp Demos showcasing WebNN AI Inference in Web Browser.

|Sample Name | Details|
|---|---|
|[demo-image-classify](webnn-demos/demo-image-classify)| The webapp demo show chat application that shows receiving images and image-classification model is used to clasify the received image, the demo uses transformers.js and reset image-classification model.|

As of 01/2025, these examples work on Windows* 11 on Google* Chrome or Microsoft* Edge browser.
