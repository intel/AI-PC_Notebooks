# `AI Upscaling with Intel® AI Boost NPU` Sample

This notebook guides you through the process of running AI Upscaling models on Intel® AI Boost NPU using OpenVINO.

| Area                | Description                                       |
| :------------------ | :------------------------------------------------ |
| What you will learn | Running AI Upscaling models on NPU using OpenVINO |
| Time to complete    | 15 minutes                                        |
| Category            | Code Optimization                                 |

## Purpose

This sample notebook shows how to leverage Intel® AI Boost Neural Processing Unit (NPU) to boost the performance of AI upscaling. We will use `OpenVINO` to upscale images and video using the `BSRGAN` model.

The sample starts by loading in the `BSRGAN` model and then converts and compiles the model for the NPU using `OpenVINO`. After loading the model, the sample applies the model to a sample image and video to demonstrate the upscaling capabilities of the model as well as the performance benefits of using the NPU.

## Prerequisites

| Optimized for | Description                                                                                                                                                                                      |
| :------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OS            | Windows 11 64-bit (22H2, 23H2) and newer or Ubuntu* 22.04 64-bit (with Linux kernel 6.6+) and newer                                                                                              |
| Hardware      | Intel® Core™ Ultra                                                                                                                                                                               |
| Software      | [Intel® NPU Driver for Windows](https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html) or [Linux NPU Driver](https://github.com/intel/linux-npu-driver/releases) |

## Run the `AI Upscaling with Intel® AI Boost NPU` Sample

The command for both Windows and Linux will install the necessary dependencies and run the sample. The sample uses [`pixi`](https://github.com/prefix-dev/pixi/) for environment and task management.

### Windows

To run the sample, run the following command:

```powershell
.\tools\run_pixi.ps1 run execute
```

### Linux

To run the sample, run the following command:

```bash
./tools/run_pixi.sh run execute
```

## Key Implementation Details

This sample tutorial contains one Jupyter Notebook.

| Notebook                      | Description                                                                                |
| :---------------------------- | :----------------------------------------------------------------------------------------- |
| `AI_Upscaling_With_NPU.ipynb` | Gain performance boost during inference using Intel® AI Boost Neural Processing Unit (NPU) |

### Exporting Dependencies to Conda Environment

**Exporting dependencies to a `conda` environment not necessary for running the sample.**

[`pixi`](https://github.com/prefix-dev/pixi/) relies on the [`conda-forge`](https://conda-forge.org/) project and [`PyPi`](https://pypi.org/) for package retrieval. This means that you can use `pixi` to export dependencies to a `conda` environment and use this exact environment in other projects.

#### Windows

To export the dependencies to a `conda` environment, run the following command:

```powershell
.\tools\run_pixi.ps1 project export conda-environment --platform win-64 environment.yml
```

This will create a `conda` environment file named `environment.yml`.

#### Linux

To export the dependencies to a `conda` environment, run the following command:

```text
./tools/run_pixi.sh project export conda-environment --platform linux-64 environment.yml
```

## Example Output

Users should be able to see a side-by-side comparison of the original and upscaled images and videos as well as the performance comparison between running the model on the CPU and NPU.

## License

Code samples are licensed under the MIT license. See [License.txt](https://github.com/oneapi-src/oneAPI-samples/blob/master/License.txt) for details.

Third party program Licenses can be found here: [third-party-programs.txt](https://github.com/oneapi-src/oneAPI-samples/blob/master/third-party-programs.txt).
