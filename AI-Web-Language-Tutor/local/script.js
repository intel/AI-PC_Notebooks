'use strict';

// Import necessary modules from the Hugging Face Transformers.js library.
import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2';

// Declare a variable to hold the chat pipeline instance and variable to track if the model has been loaded successfully.
let chatPipeline;
let modelLoaded = false;

// Configure the environment settings for Transformers.js.
env.allowLocalModels = false;
env.allowRemoteModels = true;
env.useBrowserCache = true;


async function setupPipeline() {
    console.log("Starting model loading...");
    try {
        // Create a pipeline for text generation using a pre-trained ONNX model.
        // "text-generation" specifies the task.
        // "onnx-community/Llama-3.2-1B-Instruct" is the identifier of the ONNX model on the Hugging Face Hub.
        // { device: "webgpu" } attempts to offload the model computations to the browser's WebGPU API for better performance if available.
        // Ensure the specified model is an ONNX model for compatibility with Transformers.js in the browser.
        chatPipeline = await pipeline("text-generation", "onnx-community/Llama-3.2-1B-Instruct", { device: "webgpu" });
        console.log("Model loaded successfully.");
        modelLoaded = true;
        document.getElementById('loading-indicator').style.display = 'none';
        document.getElementById('chat-box').style.display = 'flex';
        document.getElementById('message-input').style.display = 'block';
        document.getElementById('send-button').style.display = 'block';
        
        // Alert the user that the AI model is ready.
        alert('AI model is ready!');
    } catch (error) {
        // Error handling
        console.error(error.name, error.message);
        document.getElementById('loading-indicator').textContent = 'Error loading AI model.';
    }
}
// Call the setupPipeline function to initiate the model loading process.
setupPipeline();

// Send a message to the LLM and display the response.
const sendMessage = async () => {
    const input = document.getElementById('message-input');
    const chatBox = document.getElementById('chat-box');
    if (input.value.trim() !== '' && modelLoaded) {
        const userMessage = input.value;

        // Display the user's message
        const userDiv = document.createElement('div');
        userDiv.classList.add('message', 'user-message');
        const userAvatar = document.createElement('img');
        userAvatar.classList.add('avatar');
        userAvatar.src = 'images/user-avatar.png';

        const userContent = document.createElement('div');
        userContent.classList.add('content');
        userContent.textContent = userMessage;

        userDiv.appendChild(userAvatar);
        userDiv.appendChild(userContent);
        chatBox.appendChild(userDiv);
        // Scroll the chat box to the bottom to show the latest message.
        chatBox.scrollTop = chatBox.scrollHeight;
        input.value = '';

        // Display typing indicator
        document.getElementById('typing-indicator').classList.add('visible');

        // Generate response from the loaded language model.
        try {
            // Prompt tuning - here we are adding information that the model is a French language teacher
            // Depending on the used model you can update language to learn to a different one by switching 
            // the name in prompt
            const fullPrompt = [
                {
                    "role": "system", 
                    "content": "You are a language teacher speaking both English and French. The student wants to learn French. The student writes in French. Check the correctness of French the sentences and always provide feedback about the correctness. Provide English explanation of the errors. Provide the correct sentence in French."
                },
                {
                    "role": "user", 
                    "content": userMessage }
                ];
            
            // Pass the user's message (or the full prompt depending on the model's expected input format) to the chat pipeline.
            const llmResponse = await chatPipeline(userMessage);
            const llmMessage = llmResponse[0].generated_text;

            // Hide typing indicator after receiving the response
            document.getElementById('typing-indicator').classList.remove('visible');

            // Display LLM's message
            const llmDiv = document.createElement('div');
            llmDiv.classList.add('message', 'llm-message');
            const llmAvatar = document.createElement('img');
            llmAvatar.classList.add('avatar');
            llmAvatar.src = 'images/llm-avatar.png';
            const llmContent = document.createElement('div');
            llmContent.classList.add('content');
            llmContent.textContent = llmMessage;
            llmDiv.appendChild(llmAvatar);
            llmDiv.appendChild(llmContent);
            chatBox.appendChild(llmDiv);
            // Scroll the chat box to the bottom to show the latest message.
            chatBox.scrollTop = chatBox.scrollHeight;

        } catch (error) {
            // Handle any errors that occur
            console.error("Error generating response:", error);
            document.getElementById('typing-indicator').classList.remove('visible');
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('message', 'llm-message', 'error-message');
            errorDiv.textContent = 'Error generating response.';
            chatBox.appendChild(errorDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
};

// Add an event listener to the send button to call the sendMessage function when clicked.
document.getElementById('send-button').addEventListener('click', sendMessage);

// Add an event listener to the message input field to handle pressing the Enter key.
document.getElementById('message-input').addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});