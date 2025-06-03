document.addEventListener('DOMContentLoaded', function() {
    const selectModelStep = document.getElementById('selectModelStep');
    const summarizersStep = document.getElementById('summarizersStep');
    const modelSelect = document.getElementById('modelSelect');
    const selectModelButton = document.getElementById('selectModelButton');
    const urlInput = document.getElementById('urlInput');
    const sendUrlButton = document.getElementById('sendUrlButton');
    const responseElement = document.getElementById('responseElement');
    const pdfFileInput = document.getElementById('pdfFile');
    const uploadPdfButton = document.getElementById('uploadPdfButton');
    const fileNameElement = document.getElementById('fileName');
    const progressContainer = document.getElementById('progressContainer');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadPercentage = document.getElementById('uploadPercentage');
    const pdfResponseElement = document.getElementById('pdfResponseElement');
    const pdfQueryInput = document.getElementById('pdfQueryInput');
    const pdfQueryButton=document.getElementById('pdfQueryButton');
    const answerListPdf = document.getElementById('answerListPdf');
    const selectedModelElement = document.getElementById('selectedModelElement');
    const urlfurtherq = document.getElementById('urlfurtherq');
    const pdffurtherq = document.getElementById('pdffurtherq');
    const urlQueryInput = document.getElementById('urlQueryInput');
    const urlQueryButton=document.getElementById('urlQueryButton');
    const answerList = document.getElementById('answerList');
    
    // Step 1: Select Model
    selectModelButton.addEventListener('click', () => {
        const selectedModel = modelSelect.value;

        if (selectedModel=== "") {
            alert("Please select a model.");
            selectModelButton.innerHTML=`Select Model`;
        }
        else {
            selectModelButton.innerHTML=`Loading ${selectedModel} <span class="button-spinner"></span>`;
            const modelName = selectedModel;
            if (modelName) {
                selectedModelElement.textContent = `Selected model: ${modelName}`;
                
            } else {
                console.error('Could not find the model name.');
                selectModelButton.disabled=True;
                selectModelButton.innerHTML="Failed to Load"
            }
            // Send selected model to the backend to load and compile
            fetch('http://localhost:5000/select-model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_id: modelName }),
            })
            .then(response => {
                response.json()
                selectModelStep.classList.add('hidden');
                summarizersStep.classList.remove('hidden');
            })
            .catch((error) => {
                console.error('Error:', error);
                selectModelButton.remove('hidden');
            });
        }
        
    });
    

    // Step 2: Web Summarizer
    function ValidURL(url){
        var regex = /https?:\/\/[^\s/$.?#].[^\s]*/i;
        if(!regex .test(url)) {
            alert("Please enter valid URL."); 
        } 
        else 
        {
            sendUrlButton.disabled = true;
            sendUrlButton.innerHTML = 'Summarizing... <span class="button-spinner"></span>';
            responseElement.classList.add('hidden');
            urlfurtherq.classList.add('hidden');
            urlQueryButton.classList.add('hidden') ;
            urlQueryInput.classList.add('hidden');
        
            fetch('http://localhost:5000/process-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
        
                // Get the reader for streaming the response
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let receivedText = '';
                responseElement.classList.remove('hidden');
                responseElement.innerHTML='';
                urlfurtherq.classList.add('hidden');
                urlQueryButton.classList.add('hidden') ;
                urlQueryInput.classList.add('hidden');
        
                // Function to read chunks of data
                function readStream() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            // Stream finished
                            sendUrlButton.innerHTML = 'Summarize';  // Reset the button text
                            sendUrlButton.disabled = false;
                            urlfurtherq.classList.remove('hidden');
                            urlQueryButton.classList.remove('hidden') ;
                            urlQueryInput.classList.remove('hidden');
                            return;
                        }
        
                        // Decode the chunk and append to the result
                        
                        const chunk = decoder.decode(value, { stream: true });
                        receivedText += chunk;
                        responseElement.innerHTML += `${chunk}`;
        
                        // Continue reading the next chunk
                        readStream();
                    }).catch(error => {
                        console.error('Error reading stream:', error);
                        responseElement.textContent = 'Error: ' + error.message;
                        sendUrlButton.innerHTML = 'Summarize';  
                        sendUrlButton.disabled = false;
                    });
                }
        
                // Start reading the stream
                readStream();
            })
            .catch(error => {
                console.error('Error:', error);
                responseElement.textContent = 'Error: ' + error.message;
                sendUrlButton.innerHTML = 'Summarize';  
                sendUrlButton.disabled = false;
            });
        }}
    sendUrlButton.addEventListener('click', () => {
        const urlValue = urlInput.value.trim();
        answerList.innerHTML='';
        if (urlValue=== "") {
            alert("Enter a url");
        }
        else(ValidURL(urlValue))
    });

 
    // Step 2: PDF Summarizer
    uploadPdfButton.addEventListener('click', () => {
        const file = pdfFileInput.files[0];
        answerListPdf.innerHTML='';
    
        if (file && file.type === 'application/pdf') {
            const formData = new FormData();
            formData.append('pdf', file);
    
            progressContainer.style.display = 'block';
    
            const xhr = new XMLHttpRequest();
            xhr.open('POST', 'http://localhost:5000/upload-pdf', true);
            uploadPdfButton.disabled = true;
            uploadPdfButton.innerHTML = 'Summarizing... <span class="button-spinner"></span>';
            pdfResponseElement.classList.add('hidden');
            answerListPdf.value = ``;
    
            let previousResponseLength = 0;
            pdfResponseElement.innerHTML='';
            fileNameElement.classList.add('hidden');
            pdffurtherq.classList.add('hidden');
            fileNameElement.classList.add('hidden');
            pdfQueryButton.classList.add('hidden');
            pdfQueryInput.classList.add('hidden');
            answerListPdf.classList.add('hidden');
    
            // Handle the response from the server
            xhr.onprogress = function() {
                const currentResponse = xhr.responseText;
                
                // Extract the new chunk by getting the substring from the previous response length to the current length
                const newChunk = currentResponse.slice(previousResponseLength);
                previousResponseLength = currentResponse.length; // Update for the next iteration
    
                // Append the new chunk to the response element
                pdfResponseElement.innerHTML += newChunk;
                
            };
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    fileNameElement.classList.remove('hidden');
                    fileNameElement.innerHTML = `<strong>Uploaded File: </strong>${file.name}`;
                    pdfResponseElement.classList.remove('hidden');
                    uploadPdfButton.disabled = false;
                    uploadPdfButton.innerHTML = 'Upload and Summarize';
                    pdffurtherq.classList.remove('hidden')
                    pdfQueryButton.classList.remove('hidden');
                    pdfQueryInput.classList.remove('hidden');
                    answerListPdf.classList.remove('hidden');
                } else {
                    uploadPdfButton.innerHTML = 'Upload and Summarize';
                    uploadPdfButton.disabled = false;
                    pdfResponseElement.textContent = 'Upload failed. Please try again.';
                }
            };
    
            xhr.onerror = function() {
                pdfResponseElement.textContent = 'Error during upload. Please try again.';
                uploadPdfButton.innerHTML = 'Upload and Summarize';
                uploadPdfButton.disabled = false;
            };
    
            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    uploadProgress.style.width = percentComplete + '%';
                    uploadPercentage.textContent = percentComplete + '% uploaded';
                }
            };
    
            // Send the form data with the file
            xhr.send(formData);
        } else {
            alert("Please enter a valid pdf file");
            // pdfResponseElement.textContent = 'Please select a valid PDF file.';
            uploadPdfButton.innerHTML = 'Upload and Summarize';
            uploadPdfButton.disabled = false;
        }
    });
  
    //url query part
    async function fetchAnswer(query) {
        const response = await fetch('http://localhost:5000/your_query_url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query: query })
        });
      
        if (!response.ok) {
          throw new Error('Error fetching answer: ' + response.statusText);
        }
        const data = await response.json();
        return data.message;
      }
      
        urlQueryButton.addEventListener('click', async () => {
            const query = urlQueryInput.value;
            urlQueryButton.disabled = true;
            urlQueryButton.innerHTML = `<span class="button-spinner"></span>`;
            if (query) {
                try {
                    const answer = await fetchAnswer(query);
                    const questionItem = document.createElement('li');
                    questionItem.innerHTML = `<strong>Question:</strong> ${query}<br><strong>Answer:</strong> ${answer}`;
                    answerList.appendChild(questionItem);
                    urlQueryInput.value = '';
                    urlQueryButton.disabled = false;
                    urlQueryButton.innerHTML = `Answer`;
                 }
                 catch (error) {
                    console.error(error);
                    urlInput.value ='';
                    urlQueryButton.disabled = false;
                    urlQueryButton.innerHTML = `Answer`;
                } 
            }
            else {
                alert("Please enter a query!");
                urlQueryButton.innerHTML = `Answer`;
            } 
        });
    
    //functionality for pdf query input
    async function fetchAnswerPdf(query) {
        const response = await fetch('http://localhost:5000/your_query_pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query: query })
        });
        console.log(response)
        if (!response.ok) {
          throw new Error('Error fetching answer: ' + response.statusText);
        }
        const data = await response.json();
        console.log(data.message);
        return data.message;
       }
      
        pdfQueryButton.addEventListener('click', async () => {
            const query = pdfQueryInput.value;
            console.log(query);
            pdfQueryButton.disabled = true;
            pdfQueryButton.innerHTML = `<span class="button-spinner"></span>`;
            if (query) {
                try {
                    const answer = await fetchAnswerPdf(query);
                    const questionItemPdf = document.createElement('li');
                    questionItemPdf.innerHTML = `<strong>Question:</strong> ${query}<br><strong>Answer:</strong> ${answer}`;
                    answerListPdf.appendChild(questionItemPdf);
                    pdfQueryInput.value = '';
                    pdfQueryButton.disabled = false;
                    pdfQueryButton.innerHTML = `Answer`;
                } catch (error) {
                    console.error(error);
                    pdfQueryInput.value = '';
                    pdfQueryButton.disabled = false;
                    pdfQueryButton.innerHTML = `Answer`;
                } 
            }
            else {
                alert("Please enter a query!");
                pdfQueryButton.innerHTML = `Answer`;
            }
        });

    // web Summarizer tab content
    document.getElementById('webSummarizerButton').addEventListener('click', function() {
        document.getElementById('webSummarizer').style.display = 'block';
        document.getElementById('pdfSummarizer').style.display = 'none';
    });
 
    //pdf summarizer tab content
    document.getElementById('pdfSummarizerButton').addEventListener('click', function() {
        document.getElementById('webSummarizer').style.display = 'none';
        document.getElementById('pdfSummarizer').style.display = 'block';
    });
});