'use strict';

// Import necessary modules from Node.js core and third-party libraries.
const https = require('https');
const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, '..'); // main directory path

// HTTPS Configuration: Read the SSL certificate and key files.
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
        '.jpg': 'image/jpg',
    };

    // Extract filename and extension for validation
    const filename = path.basename(normalizedUrlPath);
    const fileExtension = path.extname(filename).toLowerCase();

    // Determine the content type; default to text/plain if not recognized
    let contentType = allowedExtensions[fileExtension] || 'text/plain';

    if (normalizedUrlPath.includes('..') || normalizedUrlPath.includes('\\')) {
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('Forbidden: Invalid path characters');
        return;
    }

    let targetFilePath;
    if (normalizedUrlPath === '/' || normalizedUrlPath === '' ) { // Handle both '/' and empty string after normalization
        targetFilePath = path.join(publicDir, 'index.html');
        contentType = 'text/html'; // Ensure correct content type for index.html
    } else {
        //    c. Ensure the requested file has an allowed extension.
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
    fs.readFile(filePath, (err, content) => {
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

// Start the HTTPS server and listen for incoming requests on port 8080.
server.listen(8080, () => {
    console.log('Static file server is listening on port 8080');
});