document.addEventListener('DOMContentLoaded', function() {
    // API endpoint configuration
    const API_BASE_URL = 'http://localhost:5000';
    
    // DOM element references
    const elements = {
        // Model selection elements
        selectModelStep: document.getElementById('selectModelStep'),
        summarizersStep: document.getElementById('summarizersStep'),
        modelSelect: document.getElementById('modelSelect'),
        selectModelButton: document.getElementById('selectModelButton'),
        selectedModelElement: document.getElementById('selectedModelElement'),
        modelErrorMessage: document.getElementById('modelErrorMessage'),
        
        // URL summarizer elements
        urlInput: document.getElementById('urlInput'),
        sendUrlButton: document.getElementById('sendUrlButton'),
        responseElement: document.getElementById('responseElement'),
        urlfurtherq: document.getElementById('urlfurtherq'),
        urlQueryInput: document.getElementById('urlQueryInput'),
        urlQueryButton: document.getElementById('urlQueryButton'),
        urlErrorMessage: document.getElementById('urlErrorMessage'),
        urlQueryErrorMessage: document.getElementById('urlQueryErrorMessage'),
        answerList: document.getElementById('answerList'),
        
        // PDF summarizer elements
        pdfFileInput: document.getElementById('pdfFile'),
        uploadPdfButton: document.getElementById('uploadPdfButton'),
        fileNameElement: document.getElementById('fileName'),
        progressContainer: document.getElementById('progressContainer'),
        uploadProgress: document.getElementById('uploadProgress'),
        uploadPercentage: document.getElementById('uploadPercentage'),
        pdfResponseElement: document.getElementById('pdfResponseElement'),
        pdfQueryInput: document.getElementById('pdfQueryInput'),
        pdfQueryButton: document.getElementById('pdfQueryButton'),
        pdfErrorMessage: document.getElementById('pdfErrorMessage'),
        pdfQueryErrorMessage: document.getElementById('pdfQueryErrorMessage'),
        answerListPdf: document.getElementById('answerListPdf'),
        pdffurtherq: document.getElementById('pdffurtherq'),
        
        // Tab elements
        webSummarizer: document.getElementById('webSummarizer'),
        pdfSummarizer: document.getElementById('pdfSummarizer'),
        webSummarizerButton: document.getElementById('webSummarizerButton'),
        pdfSummarizerButton: document.getElementById('pdfSummarizerButton')
    };
    
    /**
     * Helper functions for API calls
     */
    const api = {
        /**
         * Send a request to the backend API
         * @param {string} endpoint - The API endpoint path
         * @param {Object} data - The data to send
         * @param {string} method - HTTP method (default: 'POST')
         * @returns {Promise} - API response promise
         */
        async request(endpoint, data = null, method = 'POST') {
            try {
                const options = {
                    method,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                if (data) {
                    options.body = JSON.stringify(data);
                }
                
                const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`API error (${response.status}): ${errorText}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error(`API error on ${endpoint}:`, error);
                // Check if server is reachable on error
                try {
                    await fetch(API_BASE_URL);
                } catch (connectionError) {
                    throw new Error(`Server connection failed: ${connectionError.message}`);
                }
                throw error;
            }
        },
        
        /**
         * Select a model on the backend
         * @param {string} modelId - The model ID to select
         * @returns {Promise} - API response
         */
        selectModel(modelId) {
            return this.request('/select-model', { model_id: modelId });
        },

        /**
         * Process a URL for summarization
         * @param {string} url - The URL to summarize
         * @returns {Promise} - API response
         */
        processUrl(url) {
            return this.request('/process-url', { url });
        },
        
        /**
         * Answer a query about previously processed content
         * @param {string} query - The query to answer
         * @returns {Promise} - API response
         */
        answerQuery(query) {
            return this.request(`/query?query=${encodeURIComponent(query)}`);
        }
    };

    /**
     * UI utility functions
     */
    const ui = {
        /**
         * Show a loading spinner on a button
         * @param {HTMLElement} button - The button element
         * @param {string} loadingText - Text to show while loading
         */
        showButtonLoading(button, loadingText) {
            button.disabled = true;
            button.innerHTML = `${loadingText} <span class="button-spinner"></span>`;
        },
        
        /**
         * Reset a button to its original state
         * @param {HTMLElement} button - The button element
         * @param {string} text - Text to show on the button
         */
        resetButton(button, text) {
            button.disabled = false;
            button.innerHTML = text;
        },
        
        /**
         * Toggle visibility of elements
         * @param {HTMLElement[]} showElements - Elements to show
         * @param {HTMLElement[]} hideElements - Elements to hide
         */
        toggleVisibility(showElements = [], hideElements = []) {
            showElements.forEach(el => el.classList.remove('hidden'));
            hideElements.forEach(el => el.classList.add('hidden'));
        },
        
        /**
         * Show an error message in the specified error container
         * @param {HTMLElement} errorContainer - The container for the error message
         * @param {string} message - The error message to display
         */
        showError(errorContainer, message) {
            // Clear any existing errors
            this.clearErrors();
            
            // Show the error
            errorContainer.textContent = message;
            errorContainer.classList.remove('hidden');
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                this.clearError(errorContainer);
            }, 5000);
        },
        
        /**
         * Clear a specific error message
         * @param {HTMLElement} errorContainer - The error container to clear
         */
        clearError(errorContainer) {
            errorContainer.textContent = '';
            errorContainer.classList.add('hidden');
        },
        
        /**
         * Clear all error messages
         */
        clearErrors() {
            [
                elements.modelErrorMessage,
                elements.urlErrorMessage,
                elements.urlQueryErrorMessage,
                elements.pdfErrorMessage,
                elements.pdfQueryErrorMessage
            ].forEach(errorElement => {
                if (errorElement) {
                    errorElement.textContent = '';
                    errorElement.classList.add('hidden');
                }
            });
        }
    };
    
    /**
     * Model selection handler
     */
    async function handleModelSelection() {
        const selectedModel = elements.modelSelect.value;
        
        if (!selectedModel) {
            ui.showError(elements.modelErrorMessage, "Please select a model.");
            return;
        }
        
        // Clear any existing errors
        ui.clearErrors();
        
        ui.showButtonLoading(elements.selectModelButton, `Loading ${selectedModel}`);
        elements.selectedModelElement.textContent = `Selected model: ${selectedModel}`;
        
        try {
            const response = await api.selectModel(selectedModel);
            console.log('Model loaded successfully:', response.message);
            
            // Show summarizer tools once model is loaded
            ui.toggleVisibility(
                [elements.summarizersStep], 
                [elements.selectModelStep]
            );
        } catch (error) {
            console.error('Model selection failed:', error);
            elements.selectModelButton.innerHTML = 'Failed to Load';
            ui.showError(elements.modelErrorMessage, `Failed to load model: ${error.message}`);
        } finally {
            elements.selectModelButton.disabled = false;
        }
    }
    
    // Attach model selection event handler
    elements.selectModelButton.addEventListener('click', handleModelSelection);
    
    /**
     * URL validation and processing
     */
    async function handleUrlSummarization() {
        const url = elements.urlInput.value.trim();
        
        // Reset previous answers
        elements.answerList.innerHTML = '';
        
        // Clear any existing errors
        ui.clearErrors();
        
        if (!url) {
            ui.showError(elements.urlErrorMessage, "Please enter a URL.");
            return;
        }
        
        // Validate URL format
        const urlRegex = /^https?:\/\/[^\s/$.?#].[^\s]*/i;
        if (!urlRegex.test(url)) {
            ui.showError(elements.urlErrorMessage, "Please enter a valid URL.");
            return;
        }
        
        // Show loading state
        ui.showButtonLoading(elements.sendUrlButton, 'Summarizing');
        
        // Hide elements while processing
        ui.toggleVisibility(
            [], 
            [
                elements.responseElement, 
                elements.urlfurtherq, 
                elements.urlQueryButton,
                elements.urlQueryInput
            ]
        );
        
        try {
            // Process the URL
            const response = await api.processUrl(url);
            
            // Display the results
            elements.responseElement.innerHTML = response.message;
            
            // Show elements for further interaction
            ui.toggleVisibility(
                [
                    elements.responseElement, 
                    elements.urlfurtherq,
                    elements.urlQueryButton,
                    elements.urlQueryInput
                ]
            );
        } catch (error) {
            console.error('URL processing failed:', error);
            elements.responseElement.classList.remove('hidden');
            elements.responseElement.textContent = `Error: ${error.message}`;
        } finally {
            ui.resetButton(elements.sendUrlButton, 'Summarize');
        }
    }
    
    // Attach URL processing event handler
    elements.sendUrlButton.addEventListener('click', handleUrlSummarization);

 
    /**
     * PDF file upload and processing
     */
    async function handlePdfSummarization() {
        const file = elements.pdfFileInput.files[0];
        elements.answerListPdf.innerHTML = '';
        
        // Clear any existing errors
        ui.clearErrors();
        
        if (!file || file.type !== 'application/pdf') {
            ui.showError(elements.pdfErrorMessage, "Please select a valid PDF file.");
            return;
        }
        
        // Show loading state
        ui.showButtonLoading(elements.uploadPdfButton, 'Summarizing');
        
        // Reset and hide elements
        elements.pdfResponseElement.innerHTML = '';
        elements.progressContainer.style.display = 'block';
        
        ui.toggleVisibility(
            [], 
            [
                elements.pdfResponseElement,
                elements.fileNameElement,
                elements.pdffurtherq,
                elements.pdfQueryButton,
                elements.pdfQueryInput,
                elements.answerListPdf
            ]
        );
        
        // Use XMLHttpRequest for upload progress tracking
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('pdf_file', file);
        
        // Set up a promise to handle the XHR
        const uploadPromise = new Promise((resolve, reject) => {
            xhr.open('POST', `${API_BASE_URL}/upload-pdf`, true);
            
            // Handle successful response
            xhr.onload = function() {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('Invalid response format'));
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.statusText}`));
                }
            };
            
            // Handle error
            xhr.onerror = function() {
                reject(new Error('Connection error during upload'));
            };
            
            // Track upload progress
            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    elements.uploadProgress.style.width = `${percentComplete}%`;
                    elements.uploadPercentage.textContent = `${percentComplete}% uploaded`;
                }
            };
            
            // Send the request
            xhr.send(formData);
        });
        
        try {
            // Wait for the upload to complete
            const response = await uploadPromise;
            
            // Display the results
            elements.fileNameElement.innerHTML = `<strong>Uploaded File: </strong>${file.name}`;
            elements.pdfResponseElement.innerHTML = response.message;
            
            // Show elements for further interaction
            ui.toggleVisibility(
                [
                    elements.fileNameElement,
                    elements.pdfResponseElement,
                    elements.pdffurtherq,
                    elements.pdfQueryButton,
                    elements.pdfQueryInput,
                    elements.answerListPdf
                ]
            );
        } catch (error) {
            console.error('PDF processing failed:', error);
            elements.pdfResponseElement.classList.remove('hidden');
            elements.pdfResponseElement.textContent = `Error: ${error.message}`;
        } finally {
            ui.resetButton(elements.uploadPdfButton, 'Upload and Summarize');
        }
    }
    
    // Attach PDF processing event handler
    elements.uploadPdfButton.addEventListener('click', handlePdfSummarization);
  
    /**
     * Handle user queries about processed content
     * 
     * @param {string} queryType - Type of query ('url' or 'pdf')
     * @returns {Function} - Event handler function
     */
    function createQueryHandler(queryType) {
        return async function() {
            // Get the appropriate elements based on query type
            const inputElement = queryType === 'url' ? elements.urlQueryInput : elements.pdfQueryInput;
            const buttonElement = queryType === 'url' ? elements.urlQueryButton : elements.pdfQueryButton;
            const listElement = queryType === 'url' ? elements.answerList : elements.answerListPdf;
            const errorElement = queryType === 'url' ? elements.urlQueryErrorMessage : elements.pdfQueryErrorMessage;
            
            const query = inputElement.value.trim();
            
            // Clear any existing errors
            ui.clearErrors();
            
            if (!query) {
                ui.showError(errorElement, "Please enter a query!");
                return;
            }
            
            // Show loading state
            ui.showButtonLoading(buttonElement, '');
            
            try {
                // Send the query to the backend
                const response = await api.answerQuery(query);
                
                // Create and append the question-answer item
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <strong>Question:</strong> ${query}<br>
                    <strong>Answer:</strong> ${response.message}
                `;
                listElement.appendChild(listItem);
                
                // Clear the input field
                inputElement.value = '';
            } catch (error) {
                console.error(`${queryType.toUpperCase()} query failed:`, error);
                ui.showError(errorElement, `Query failed: ${error.message}`);
            } finally {
                ui.resetButton(buttonElement, 'Answer');
            }
        };
    }
    
    // Attach query handlers
    elements.urlQueryButton.addEventListener('click', createQueryHandler('url'));
    elements.pdfQueryButton.addEventListener('click', createQueryHandler('pdf'));

    /**
     * Tab switching functionality
     */
    function setupTabHandlers() {
        // Web summarizer tab
        elements.webSummarizerButton.addEventListener('click', function() {
            elements.webSummarizer.style.display = 'block';
            elements.pdfSummarizer.style.display = 'none';
        });
        
        // PDF summarizer tab
        elements.pdfSummarizerButton.addEventListener('click', function() {
            elements.webSummarizer.style.display = 'none';
            elements.pdfSummarizer.style.display = 'block';
        });
    }
    
    // Initialize tab handlers
    setupTabHandlers();
});
