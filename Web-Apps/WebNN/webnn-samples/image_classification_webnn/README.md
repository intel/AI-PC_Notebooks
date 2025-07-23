# Image Classification using WebNN API

Sample created from by simplifying the original [webmachinelearning image classification sample](https://github.com/webmachinelearning/webnn-samples/tree/master/image_classification)

The sample uses __MobileNetV2__ model to build an image classification system on the web that uses __WebNN API__. 

| Files | Details
|---|---|
|index.html|HTML for basic UI|
|main.js|main javasvript file to perform image selection and classification using WebNN APIs|
|utils.js|utils.js javasvript helper file|
|numpy.js|numpy.js javasvript helper file|
|mobilenet_nhwc.js| Javasvript library for MobileNet V2 model with nhwc input layout|
|models/mobilenetv2_nhwc/*|mobilenetv2 tflite model test-data from the [github.com/webmachinelearning/test-data](https://github.com/webmachinelearning/test-data/tree/9ddde064bbab8fd21bbcc4071c2546393304db1a/models/mobilenetv2_nhwc)|

Can be tested using the "Live Preview" extension for VSCode
