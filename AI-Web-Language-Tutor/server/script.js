'use strict';

// Establish a WebSocket connection to the server running on localhost at port 8080.
const ws = new WebSocket('ws://localhost:8080');
let modelLoaded = false; // Flag to track model loading status

// Event handler for when the WebSocket connection is successfully opened.
ws.onopen = () => {
    console.log('WebSocket connection opened');
    // Optionally, send a message to the server to inquire about the model's loading status.
    // This can be useful to synchronize the client's UI with the server's model readiness.
    ws.send(JSON.stringify({ type: 'checkModelLoaded' }));
};

// Event handler for when a message is received from the WebSocket server.
ws.onmessage = (event) => {
    const chatBox = document.getElementById('chat-box');
    const loadingIndicator = document.getElementById('loading-indicator');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const data = JSON.parse(event.data);

    // Check if the received message indicates that the AI model on the server is loaded.
    if (data.type === 'modelLoaded') {
        modelLoaded = true;
        loadingIndicator.style.display = 'none';
        chatBox.style.display = 'block'; // Or 'block' depending on your CSS
        messageInput.style.display = 'block';
        sendButton.style.display = 'block';
        alert('AI model is ready!');
        return; // Important to exit the function after handling the 'modelLoaded' event.
    }

    // If the model is loaded, handle subsequent messages (chat messages).
    if (modelLoaded) {
        if (data.message === 'typing') {
            document.getElementById('typing-indicator').classList.add('visible');
        } else {
            const message = document.createElement('div');
            message.classList.add('message', data.sender === 'LLM' ? 'llm-message' : 'user-message');

            const avatar = document.createElement('img');
            avatar.classList.add('avatar');
            avatar.src = data.sender === 'LLM' ? 'images/llm-avatar.png' : 'images/user-avatar.png';

            const content = document.createElement('div');
            content.classList.add('content');
            content.textContent = data.message;

            message.appendChild(avatar);
            message.appendChild(content);
            chatBox.appendChild(message);
            // Scroll the chat box to the bottom to show the latest message.
            chatBox.scrollTop = chatBox.scrollHeight;

            document.getElementById('typing-indicator').classList.remove('visible');
        }
    }
};

// Function to send the user's message to the WebSocket server.
const sendMessage = () => {
    const input = document.getElementById('message-input');
    if (input.value.trim() !== '') {
        const userMessage = {
            sender: 'User',
            message: input.value
        };
        ws.send(JSON.stringify(userMessage));
        input.value = '';
    }
};

// Add an event listener to the send button to call the sendMessage function when clicked.
document.getElementById('send-button').addEventListener('click', sendMessage);

// Add an event listener to the message input field to handle pressing the Enter key.
document.getElementById('message-input').addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});