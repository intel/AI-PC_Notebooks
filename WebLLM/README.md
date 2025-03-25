# WebLLM - Chat Application

This project demonstrates how to use WebLLM, a high-performance in-browser LLM inference engine. The examples provided showcase various functionalities and UI implementations to help you get started with integrating WebLLM into your own projects.

Below is a summary of the files included in this project:

## Code Snippets

These files show JavaScript code snippets and display everything on the console, focusing on introducing functionalities to the user without the UI.

| File                                                                 | Description                                      |
|----------------------------------------------------------------------|--------------------------------------------------|
| [01_completion.html](./01_completion.html)                           | Demonstrates basic chat completion with WebLLM, showing how to get a response from the model. |
| [02_streaming.html](./02_streaming.html)                             | Shows how to stream LLM output using WebLLM, providing real-time response updates. |
| [03_model_select.html](./03_model_select.html)                       | Displays available models in the console, allowing users to see which models can be used. |

## UI Demos

These files incrementally build the UI for generation and chat use-cases.

| File                                                                 | Description                                      |
|----------------------------------------------------------------------|--------------------------------------------------|
| [11_basicUI.html](./11_basicUI.html)                                 | Basic generation UI for sending messages to the chatbot, demonstrating a simple interface. |
| [12_generationUI.html](./12_generationUI.html)                       | Enhanced generation UI with model selection and message streaming capabilities, showing real-time message generation. |
| [13_chatUI.html](./13_chatUI.html)                                   | Advanced chat UI with model selection and usage stats, providing a comprehensive chat experience. |

## Final Implementation

The final implementation splits the UI and JavaScript into separate files for better practice. You can find it in the [Final](./Final) folder.

## Screenshot

![image](./webll-chatui.png)
