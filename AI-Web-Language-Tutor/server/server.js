'use strict';

// Import necessary modules from Node.js core and third-party libraries.
const https = require('https');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const { pipeline } = require('@huggingface/transformers');

const publicDir = path.join(__dirname, '..'); // main directory path

// HTTPS Configuration
// Read the SSL certificate and key files
const options = {
    key: fs.readFileSync(path.join(__dirname, 'server.key')),
    cert: fs.readFileSync(path.join(__dirname, 'server.cert'))
};

// Create an HTTPS server.
const server = https.createServer(options, (req, res) => {
let requestedUrl = req.url;

    requestedUrl = decodeURIComponent(requestedUrl.split('?')[0]);
    const normalizedUrlPath = path.normalize(requestedUrl);

    const allowedExtensions = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
    };

    // Extract filename and extension for validation
    const filename = path.basename(normalizedUrlPath);
    const fileExtension = path.extname(filename).toLowerCase();
    let contentType = allowedExtensions[fileExtension] || 'application/octet-stream';

    // Determine the content type; default to text/plain if not recognized
    if (normalizedUrlPath.includes('..') || normalizedUrlPath.includes('\\')) {
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('Forbidden: Invalid path characters');
        return;
    }

    let targetFilePath;
    if (normalizedUrlPath === '/' || normalizedUrlPath === '') {
        targetFilePath = path.join(publicDir, 'index.html');
        contentType = 'text/html';
    } else {
        if (!allowedExtensions[fileExtension]) {
            res.writeHead(403, { 'Content-Type': 'text/plain' });
            res.end('Forbidden: Disallowed file type');
            return;
        }
        targetFilePath = path.join(publicDir, normalizedUrlPath);

        const absolutePublicDir = path.resolve(publicDir);
        const absoluteTargetFilePath = path.resolve(targetFilePath);

        if (!absoluteTargetFilePath.startsWith(absolutePublicDir + path.sep) && absoluteTargetFilePath !== absolutePublicDir) {
            res.writeHead(403, { 'Content-Type': 'text/plain' });
            res.end('Forbidden: Attempted directory traversal');
            return;
        }
    }

    // Read the requested file asynchronously.
    fs.readFile(targetFilePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                fs.readFile(path.join(__dirname, '404.html'), (error, page) => {
                    console.error('Error reading 404.html:', error); // Log the error
                    res.writeHead(404, { 'Content-Type': 'text/html' });
                    res.end(page, 'utf-8');
                });
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${err.code}`);
            }
        } else {
            // File read successfully. Serve the content with the correct content type.
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

// Create a WebSocket server instance, attaching it to the existing HTTP server.
const wss = new WebSocket.Server({ server });

// Declare variables for the Hugging Face Transformers pipeline and its loading status.
let chatPipeline;
let modelIsLoaded = false; // Track if the model is loaded

// Set up the Hugging Face Transformers pipeline.
async function setupPipeline() {
    console.log("Starting model loading...");
    try {
        // Create a pipeline for text generation using a pre-trained ONNX model.
        // "text-generation" specifies the task.
        // "onnx-community/Llama-3.2-1B-Instruct" is the identifier of the ONNX model on the Hugging Face Hub.
        // { device: 'gpu' } attempts to offload the model computations to the GPU for faster processing.
        // Ensure the specified model is an ONNX model for compatibility with Transformers.js API.
        chatPipeline = await pipeline("text-generation", "onnx-community/Llama-3.2-1B-Instruct", { device: 'gpu' });
        console.log("Model loaded successfully.");
        modelIsLoaded = true;
        // Notify all connected WebSocket clients that the model has been loaded.
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({ type: 'modelLoaded' }));
            }
        });
    } catch (error) {
        console.error("Error loading model:", error);
    }
}

// Call the setupPipeline function to initiate the model loading process when the server starts.
setupPipeline();

// Event listener for when a new WebSocket client connects to the server.
wss.on('connection', (socket) => {
    console.log('Client connected');

    socket.on('message', (message) => {
        try {
            const parsedMessage = JSON.parse(message);
            if (parsedMessage.type === 'checkModelLoaded') {
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({ type: 'modelLoaded', loaded: modelIsLoaded }));
                }
            }
        } catch (error) {
            console.error('Error parsing message from client:', error);
        }
    });

    // Event listener for messages, specifically to handle user messages for the LLM. 
    socket.on('message', async (message) => {
        try {
            const userMessage = JSON.parse(message);

            if (userMessage && userMessage.message) {
                console.log(userMessage);
                // Broadcast the user's message to all connected WebSocket clients.
                wss.clients.forEach((client) => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify({ sender: 'User', message: userMessage.message }));
                    }
                });

                // Notify clients that the LLM is typing
                wss.clients.forEach((client) => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify({ sender: 'LLM', message: 'typing' }));
                    }
                });

                // Generate a response from the loaded language model.
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
                        "content": userMessage.message },
                    ];
                    // Provide the full prompt to the text generation pipeline and set a maximum number of new tokens to generate.
                    const llmResponse = await chatPipeline(fullPrompt, { max_new_tokens: 256 });
                    const llmMessage = llmResponse[0].generated_text;
                    console.log(llmMessage[2].content);
                    // Broadcast the LLM's response to all connected WebSocket clients.
                    wss.clients.forEach((client) => {
                        if (client.readyState === WebSocket.OPEN) {
                            client.send(JSON.stringify({ sender: 'LLM', message: llmMessage[2].content }));
                        }
                    });
                } catch (error) {
                    console.error("Error during LLM response generation:", error);
                    wss.clients.forEach((client) => {
                        if (client.readyState === WebSocket.OPEN) {
                            client.send(JSON.stringify({ sender: 'LLM', message: 'Error generating response.' }));
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error parsing message from client:', error);
        }
    });
    
    // Event listener for when a connected WebSocket client closes the connection.
    socket.on('close', () => {
        console.log('Client disconnected');
    });
});

// Start the HTTPS server and listen for incoming requests on port 8080.
server.listen(8080, () => {
    console.log('Server is listening on port 8080');
});