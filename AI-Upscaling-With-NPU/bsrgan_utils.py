"""
Copyright 2022 Kai Zhang (cskaizhang@gmail.com, https://cszn.github.io/).
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file is sourced from https://github.com/cszn/BSRGAN/blob/main/main_test_bsrgan.py
and https://github.com/cszn/BSRGAN/blob/main/utils/utils_image.py and has been modified.
All functions now include error handling and docstrings.
load_model now uses safetensors to load the model checkpoint.
"""

import cv2

import numpy as np
import torch
from safetensors.torch import load_file


# Modified from https://github.com/cszn/BSRGAN/blob/main/main_test_bsrgan.py
def load_model(model, model_path):
    """loads model from safe-tensors checkpoint

    Args:
        model (RRDBNet): RRDBNet model
        model_path (str): Path to the model checkpoint
    """
    try:
        model.load_state_dict(load_file(model_path), strict=True)
        for _, v in model.named_parameters():
            v.requires_grad = False
    except Exception as e:
        print("Error loading model")
        raise e


# Sourced from https://github.com/cszn/BSRGAN/blob/main/utils/utils_image.py
def imread_uint(path, n_channels=3):
    """reads an image from a path

    Args:
        path (str): Path to the image
        n_channels (int, optional): Number of channels in image. Defaults to 3 (for RGB)

    Returns:
        numpy.ndarray: NumPy array of the image
    """
    try:
        # output: HxWx3(RGB or GGG), or HxWx1 (G)
        if n_channels == 1:
            img = cv2.imread(path, 0)  # cv2.IMREAD_GRAYSCALE
            img = np.expand_dims(img, axis=2)  # HxWx1
        elif n_channels == 3:
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # BGR or G
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # GGG
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # RGB
        return img
    except Exception as e:
        print("Error reading image")
        raise e


# Sourced from https://github.com/cszn/BSRGAN/blob/main/utils/utils_image.py
def uint2tensor4(img):
    """converts a numpy array to a PyTorch tensor

    Args:
        img (numpy.ndarray): NumPy array of the image

    Returns:
        torch.Tensor: PyTorch tensor of the image
    """
    try:
        if img.ndim == 2:
            img = np.expand_dims(img, axis=2)
        return torch.from_numpy(np.ascontiguousarray(img)).permute(2, 0, 1).float().div(255.0).unsqueeze(0)
    except Exception as e:
        print("Error converting uint to tensor")
        raise e


# Modified from https://github.com/cszn/BSRGAN/blob/main/utils/utils_image.py
def tensor2uint(img):
    """converts a 4D tensor back into 3D numpy array (HxWxC)

    Args:
        img (Union[torch.Tensor, numpy.ndarray]): Image tensor or array

    Returns:
        numpy.ndarray: NumPy array of the image
    """
    try:
        if isinstance(img, torch.Tensor):
            img = img.data.squeeze().float().clamp_(0, 1).cpu().numpy()
        elif isinstance(img, np.ndarray):
            img = np.squeeze(img).astype(np.float32).clip(0, 1)
        if img.ndim == 3:
            img = np.transpose(img, (1, 2, 0))
        return np.uint8((img * 255.0).round())
    except Exception as e:
        print("Error converting tensor to uint")
        raise e
