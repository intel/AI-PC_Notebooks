import timeit
import requests
import os
import cv2
import numpy as np
import torch
import ffmpeg
from safetensors.torch import load_file
from tqdm.auto import tqdm


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


# Sourced from https://github.com/cszn/BSRGAN/blob/main/main_test_bsrgan.py
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


# Sourced from https://github.com/cszn/BSRGAN/blob/main/main_test_bsrgan.py
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
        return (
            torch.from_numpy(np.ascontiguousarray(img))
            .permute(2, 0, 1)
            .float()
            .div(255.0)
            .unsqueeze(0)
        )
    except Exception as e:
        print("Error converting uint to tensor")
        raise e


# Modified from https://github.com/cszn/BSRGAN/blob/main/main_test_bsrgan.py
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


def time_execution(stmt, globals=None, number=1, repeat=5):
    """times the execution of a statement

    Args:
        stmt (callable): a callable object that will be timed
        globals (Any, optional): Global variables. Defaults to None.
        number (int, optional): Number of times to run the statement. Defaults to 1.
        repeat (int, optional): Number of times to repeat the timing. Defaults to 5.

    Returns:
        tuple: Tuple of execution times (List[float]), mean (float), and standard deviation (float)
    """
    try:
        times = timeit.repeat(stmt, globals=globals, number=number, repeat=repeat)

        mean = np.mean(times)
        std = np.std(times)

        print(f"{mean:.2f} ± {std:.2f} seconds")

        return times, mean, std
    except Exception as e:
        print("Error timing execution")
        raise e


def preprocess(frame: np.ndarray) -> torch.Tensor:
    """preprocesses a frame to convert it to a format that can be fed to the model

    Args:
        frame (np.ndarray): NumPy array of the frame

    Returns:
        torch.Tensor: PyTorch tensor of the frame
    """
    try:
        return uint2tensor4(frame)
    except Exception as e:
        print("Error converting frame to tensor")
        raise e


def postprocess(frame: torch.Tensor) -> np.ndarray:
    """postprocesses a frame to convert it to a format that can be displayed

    Args:
        frame (torch.Tensor): PyTorch tensor of the frame

    Returns:
        np.ndarray: NumPy array of the frame
    """
    try:
        res = tensor2uint(frame)
        return res
    except Exception as e:
        print("Error converting tensor to frame")
        raise e


def collect_all_frames(video: cv2.VideoCapture) -> list[np.ndarray]:
    """collects all the frames from a video

    Args:
        video (cv2.VideoCapture): Video capture object

    Returns:
        list[np.ndarray]: List of frames
    """
    try:
        frames = []

        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = tqdm(total=num_frames, desc="Collecting frames from video")

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break

            frames.append(frame)
            pbar.update(1)

        return frames
    except Exception as e:
        print("Error collecting frames")
        raise e


def write_all_frames(frames: list[np.ndarray], output_video: cv2.VideoWriter) -> None:
    """writes all the frames to an output video

    Args:
        frames (list[np.ndarray]): List of frames
        output_video (cv2.VideoWriter): Video writer object
    """
    try:
        for frame in tqdm(frames, desc="Writing frames to output video"):
            output_video.write(frame)
    except Exception as e:
        print("Error writing frames to output video")
        raise e


def download_file(url, output_file):
    """downloads a file from the given URL and saves it to the specified output file

    Args:
        url: The URL of the file to download
        output_file: The path where the downloaded file will be saved
    """

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"File has been downloaded as {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def resize_video(input_path, scale=2):
    """reduces the resolution of the given video by a given scale factor, \
        so the output video will have a resolution that is 1 / scale times \
        the original resolution

    Args:
        input_path: The file path to the input video
        scale: The factor by which to scale the video resolution. \
            The output size will be original_size / scale. Default value is 2
    """

    try:
        original_video_info = ffmpeg.probe(input_path)
        original_video_height = original_video_info["streams"][0]["height"]
        original_video_width = original_video_info["streams"][0]["width"]

        new_height = int(original_video_height / scale)
        new_width = int(original_video_width / scale)

        temp_output_path = "temp_resized_video.mp4"

        ffmpeg.input(input_path).output(
            temp_output_path, vf=f"scale={new_width}:{new_height}"
        ).overwrite_output().run()

        # After processing, replace the original file with the resized one
        os.replace(temp_output_path, input_path)
        print(f"Video resized successfully and overwritten: {input_path}")

    except ffmpeg.Error as e:
        print(f"Error: {e}")
        print("ffmpeg stderr output:\n", e.stderr.decode("utf-8"))
