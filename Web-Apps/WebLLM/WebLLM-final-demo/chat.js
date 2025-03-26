import * as webllm from "https://esm.run/@mlc-ai/web-llm";

// DOM Selectors
const messageContainer = document.getElementById("message-container");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-btn");
const loadingProgress = document.getElementById("loading-progress");
const modelSelection = document.getElementById("model-selection");
const downloadButton = document.getElementById("download");

// CSS Classes
const messageCSS = ["p-2", "rounded-lg", "max-w-xs", "message-content"];
const userCSS = messageCSS.concat(["bg-blue-500", "text-white"]);
const assistantCSS = messageCSS.concat(["bg-gray-200", "text-gray-800"]);

// System Message
const messages = [
    {content: "You are a helpful AI assistant", role: "system"},
];


// Update model options
let selectedModel = "SmolLM2-135M-Instruct-q0f16-MLC";
const availableModels = webllm.prebuiltAppConfig.model_list;

function updateModelOptions() {
    availableModels.forEach((model) => {
        if (model.low_resource_required) {
            const option = document.createElement("option");
            option.value = model.model_id;
            option.textContent = `${model.model_id} (${model.vram_required_MB} MB)`;
            modelSelection.appendChild(option);
        }
    });
    modelSelection.value = selectedModel;
}

updateModelOptions();


// Initialize with a progress callback
const initProgressCallback = (progress) => {
    loadingProgress.textContent = `Model loading progress: ${progress.text}`;
    console.log("Model loading progress:", progress);
};

// Create WebLLM engine instance
const engine = new webllm.MLCEngine({
    initProgressCallback: initProgressCallback,
});

// Initialize engine with selected model
async function initializeWebLLMEngine() {
    loadingProgress.classList.remove("hidden");
    selectedModel = modelSelection.value;
    const config = { temperature: 1.0, top_p: 1 };
    await engine.reload(selectedModel, config);
}

downloadButton.addEventListener("click", function () {
    initializeWebLLMEngine().then(() => {
        sendButton.disabled = false;
    });
});

// Update chat UI with new messages
function updateChatUI(message) {
    const messageDiv = document.createElement("div");
    const messageContent = document.createElement("div");
    messageDiv.appendChild(messageContent);
    messageContainer.appendChild(messageDiv);

    if (message.role === "user") {
        messageDiv.classList.add("flex", "justify-end", "message");
        messageContent.classList.add(...userCSS);
    } else {
        messageDiv.classList.add("flex", "flex-col", "justify-start", "message");
        messageContent.classList.add(...assistantCSS);
    }

    messageContent.textContent = message.content;
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// Update the content of the last message
function updateLastMessage(content) {
    const messageDoms = messageContainer.querySelectorAll(".message-content");
    const lastMessage = messageDoms[messageDoms.length - 1];
    lastMessage.textContent = content;
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// Extract key-value pairs for stats
function extractKeysAndValues(obj, result = [], prefix = "") {
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const fullKey = prefix ? `${prefix}.${key}` : key;
            if (typeof obj[key] === "object" && obj[key] !== null) {
                extractKeysAndValues(obj[key], result, fullKey);
            } else {
                result.push(`${fullKey}: ${obj[key]}`);
            }
        }
    }
    return result;
}

// Create the info component for usage stats
function createInfoComponent(stats) {
    const usageDiv = document.createElement("div");
    usageDiv.classList.add("chat-stats", "flex", "items-center", "justify-left");
    
    const groupDiv = document.createElement("div");
    groupDiv.classList.add("relative", "group");
    
    const infoIcon = document.createElement("div");
    infoIcon.classList.add("w-6", "h-6", "flex", "items-center", "justify-center", "bg-blue-500", "text-white", "rounded-full", "cursor-pointer");
    infoIcon.textContent = "i";
    groupDiv.appendChild(infoIcon);
    
    const toolTip = document.createElement("div");
    toolTip.classList.add("absolute", "bottom-full", "left-1/2", "transform-translate-x-1/2", "mb-2", "px-3", "py-1", "text-sm", "text-white", "bg-gray-700", "rounded", "shadow-lg", "opacity-0", "group-hover:opacity-100", "transition-opacity", "whitespace-pre-wrap");
    toolTip.textContent = extractKeysAndValues(stats).join("\n");
    groupDiv.appendChild(toolTip);
    
    usageDiv.appendChild(groupDiv);
    messageContainer.querySelector(".message:last-child").appendChild(usageDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// Finalize message generation and display stats
function onFinishGenerating(message, stats) {
    updateLastMessage(message);  // Update the generated message content
    createInfoComponent(stats);  // Add usage stats component
    sendButton.disabled = false;
    chatInput.setAttribute("placeholder", "Type a message...");

}

// Stream message generation from the engine
async function streamGeneration(messages, onUpdate, onFinish) {
    try {
        const chunks = await engine.chat.completions.create({
            messages,
            stream: true,
            stream_options: { include_usage: true },
        });

        let currentMessage = "";
        let stats = "";
        for await (const chunk of chunks) {
            currentMessage += chunk.choices[0]?.delta.content || "";
            onUpdate(currentMessage);
            if (chunk.usage) {
                stats = chunk.usage;
            }
        }
        const finalMessage = await engine.getMessage();
        onFinish(finalMessage, stats);
    } catch (err) {
        console.error(err);
    }
}

// Send a new message
function onSend() {
    if (chatInput.value.trim() !== "") {
        sendButton.disabled = true;

        // User message
        const userMessage = { content: chatInput.value, role: "user" };
        messages.push(userMessage);
        updateChatUI(userMessage);

        // Clear input field
        chatInput.value = "";
        chatInput.setAttribute("placeholder", "Generating...");

        // Add AI typing placeholder
        const aiMessage = { content: "typing...", role: "assistant" };
        updateChatUI(aiMessage);

        // Generate response
        streamGeneration(messages, updateLastMessage, onFinishGenerating);
    }
}

// Event listener for send button
sendButton.addEventListener("click", onSend);