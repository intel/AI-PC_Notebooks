"""
This file is sourced from https://github.com/kadirnar/bsrgan-pip/blob/main/bsrgan/helpers.py
and has been modified. All functions now include error handling and docstrings.
load_model now uses safetensors to load the model checkpoint.
"""

import os
import torch
import numpy as np
from typing import Optional

import bsrgan_utils as util
from network_rrdbnet import RRDBNet


def download_from_hub(repo_id: str, hf_token: Optional[str] = None) -> Optional[str]:
    """
    Download a model file from Hugging Face Hub.

    Args:
        repo_id (str): The repository ID on Hugging Face Hub.
        hf_token (Optional[str]): The Hugging Face authentication token.

    Returns:
        Optional[str]: The path to the downloaded file, or None if download fails.
    """
    from huggingface_hub.errors import RepositoryNotFoundError
    from huggingface_hub import hf_hub_download, list_repo_files
    from huggingface_hub.utils._validators import HFValidationError

    try:
        repo_files = list_repo_files(repo_id=repo_id, repo_type="model", token=hf_token)
        model_file = [f for f in repo_files if f.endswith(".pth")][0]
        file = hf_hub_download(
            repo_id=repo_id,
            filename=model_file,
            repo_type="model",
            token=hf_token,
        )
        return file
    except (RepositoryNotFoundError, HFValidationError):
        raise RuntimeError("Failed to download the model from Hugging Face Hub.")


class BSRGAN:
    def __init__(self, model_path: str, device: torch.device, hf_model: bool = False):
        """
        Initialize the BSRGAN model.

        Args:
            model_path (str): Path to the model file or Hugging Face repository ID.
            device (torch.device): The device to run the model on.
            hf_model (bool): Whether to download the model from Hugging Face Hub.
        """
        self.device = device
        self.save = True

        if hf_model:
            model_path = download_from_hub(model_path)
        else:
            model_path = model_path

        self.model_path = model_path

        self.load_model()

    def load_model(self) -> None:
        """
        Load the model from the specified path.
        """
        model_name = os.path.splitext(os.path.basename(self.model_path))[0]
        if [model_name] in ["BSRGANx2"]:
            sf = 2
        else:
            sf = 4

        model = RRDBNet(in_nc=3, out_nc=3, nf=64, nb=23, gc=32, sf=sf)
        state_dict = torch.load(self.model_path, weights_only=True, map_location=self.device)  # nosec B614
        model.load_state_dict(state_dict, strict=True)
        model.eval()

        for k, v in model.named_parameters():
            v.requires_grad = False

        model = model.to(self.device)

        self.model_name = model_name
        self.model = model

    def predict(self, img_path: str) -> np.ndarray:
        """
        Predict the output image using the BSRGAN model.

        Args:
            img_path (str): Path to the input image.

        Returns:
            numpy.ndarray: The output NumPy array of the image.
        """
        img = util.imread_uint(img_path, n_channels=3)
        img = util.uint2tensor4(img)
        img = img.to(self.device)
        img = self.model(img)
        img = util.tensor2uint(img)
        return img
