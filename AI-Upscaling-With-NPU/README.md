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

## Key Implementation Details

This sample tutorial contains one Jupyter Notebook.

| Notebook                      | Description                                                                                |
| :---------------------------- | :----------------------------------------------------------------------------------------- |
| `AI_Upscaling_With_NPU.ipynb` | Gain performance boost during inference using Intel® AI Boost Neural Processing Unit (NPU) |

## Run the `AI Upscaling with Intel® AI Boost NPU` Sample

### Using `pixi`

The command for both Windows and Linux will install the necessary dependencies and run the sample. The sample uses [pixi](https://github.com/prefix-dev/pixi/) for environment and task management. The sample will automatically install `pixi` as well. The `pixi` executable, cache, and packages will be contained within the `.pixi` directory located in the root of the sample.

To run the sample, run the following command:

**Windows:** `.\tools\run_pixi.ps1 run execute`
**Linux:** `./tools/run_pixi.sh run execute`

To clean up the created environment, delete the `.pixi` directory located in the root of the sample.

### Using `conda`

The sample can also be run using `conda`. The following steps will guide you through the process.

1. Export the dependencies to a `conda` environment

**Windows:** `.\tools\run_pixi.ps1 project export conda-environment --platform win-64 environment.yml`
**Linux:** `./tools/run_pixi.sh project export conda-environment --platform linux-64 environment.yml`

2. Remove `.pixi` folder

**Windows:** `rm -r -fo .pixi`
**Linux:** `rm -rf .pixi`

3. Create the `conda` environment using the exported `environment.yml` file

`conda env create -f environment.yml`

4. Activate the `conda` environment

`conda activate default`

5. Execute the Jupyter Notebook via command line

`jupyter nbconvert --execute --to notebook --inplace --debug AI_Upscaling_With_NPU.ipynb`

To clean up the created environment, run `conda env remove -n default`

## Opening Jupyter Notebook

If you choose to run the Jupyter Notebook directly, you can open the Jupyter Notebook by running the following command:

### Using `pixi`

**Windows:** `.\tools\run_pixi.ps1 run jupyter notebook AI_Upscaling_With_NPU.ipynb`
**Linux:** `./tools/run_pixi.sh run jupyter notebook AI_Upscaling_With_NPU.ipynb`

### Using `conda`

`jupyter notebook AI_Upscaling_With_NPU.ipynb`

## Example Output

Users should be able to see a side-by-side comparison of the original and upscaled images and videos as well as the performance comparison between running the model on the CPU and NPU.

## License

Code samples are licensed under the MIT license. See [License.txt](https://github.com/oneapi-src/oneAPI-samples/blob/master/License.txt) for details.

Third party program Licenses can be found here: [third-party-programs.txt](https://github.com/oneapi-src/oneAPI-samples/blob/master/third-party-programs.txt).
