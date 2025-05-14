document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadForm = document.getElementById('upload-form');
    const fileUpload = document.getElementById('file-upload');
    const uploadButton = document.getElementById('upload-button');
    const loadingContainer = document.getElementById('loading-container');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const filenameElement = document.getElementById('filename');
    const metadataSummary = document.getElementById('metadata-summary');
    const metadataTable = document.getElementById('metadata-table');
    const privacyCard = document.getElementById('privacy-card');
    const privacyList = document.getElementById('privacy-list');
    const locationCard = document.getElementById('location-card');
    const downloadJsonBtn = document.getElementById('download-json');
    const downloadTextBtn = document.getElementById('download-text');
    
    // Global variables
    let currentMetadata = null;
    let map = null;
    let marker = null;

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileUpload.files[0];
        if (!file) {
            showError('Please select a file to upload');
            return;
        }

        // File size validation (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            showError('File size exceeds 10MB limit');
            return;
        }

        // Check file extension
        const extension = file.name.split('.').pop().toLowerCase();
        if (!['jpg', 'jpeg', 'png', 'pdf'].includes(extension)) {
            showError('Unsupported file type. Please upload JPG, PNG, or PDF files only');
            return;
        }

        // Reset previous results
        resetUI();
        
        // Show loading indicator
        loadingContainer.classList.remove('d-none');
        
        // Create form data for submission
        const formData = new FormData();
        formData.append('file', file);
        
        // Send file to server
        fetch('/extract', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingContainer.classList.add('d-none');
            
            if (data.status === 'error') {
                showError(data.message);
                return;
            }
            
            // Store metadata for download
            currentMetadata = data.metadata;
            
            // Display results
            displayResults(data);
        })
        .catch(error => {
            loadingContainer.classList.add('d-none');
            showError('An error occurred while processing your file: ' + error.message);
            console.error('Error:', error);
        });
    });
    
    // Download metadata as JSON
    downloadJsonBtn.addEventListener('click', function() {
        if (!currentMetadata) return;
        
        downloadMetadata('json');
    });
    
    // Download metadata as Text
    downloadTextBtn.addEventListener('click', function() {
        if (!currentMetadata) return;
        
        downloadMetadata('text');
    });
    
    // Function to download metadata
    function downloadMetadata(format) {
        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                metadata: currentMetadata,
                format: format
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                showError(data.message);
                return;
            }
            
            // Create file content
            const content = data.data;
            
            // Create blob and download
            const blob = new Blob([content], { 
                type: format === 'json' ? 'application/json' : 'text/plain' 
            });
            const url = URL.createObjectURL(blob);
            
            // Create download link and click it
            const a = document.createElement('a');
            a.href = url;
            a.download = `metadata.${format === 'json' ? 'json' : 'txt'}`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 0);
        })
        .catch(error => {
            showError('An error occurred while generating download: ' + error.message);
            console.error('Error:', error);
        });
    }
    
    // Function to display results
    function displayResults(data) {
        // Show result container
        resultContainer.classList.remove('d-none');
        
        // Display filename
        filenameElement.textContent = data.filename;
        
        // Create summary
        createMetadataSummary(data.metadata);
        
        // Fill metadata table
        populateMetadataTable(data.metadata);
        
        // Display privacy concerns
        displayPrivacyConcerns(data.privacy_concerns);
        
        // Check and display location data
        checkForLocationData(data.metadata);
    }
    
    // Function to create metadata summary
    function createMetadataSummary(metadata) {
        let summary = '<div class="row">';
        
        // Key information to highlight
        const highlights = [
            { key: 'Make', icon: 'camera', label: 'Camera Make' },
            { key: 'Model', icon: 'camera', label: 'Camera Model' },
            { key: 'Software', icon: 'laptop-code', label: 'Software Used' },
            { key: 'Author', icon: 'user', label: 'Author' },
            { key: 'Creator', icon: 'user', label: 'Creator' },
            { key: 'DateTime', icon: 'calendar-alt', label: 'Date Taken' },
            { key: 'DateTimeOriginal', icon: 'calendar-alt', label: 'Original Date' },
            { key: 'CreationDate', icon: 'calendar-plus', label: 'Created On' },
            { key: 'Page Count', icon: 'file-alt', label: 'Pages' }
        ];
        
        let foundAny = false;
        
        for (const item of highlights) {
            // Look for exact match or readable version
            let value = metadata[item.key];
            const readableKey = item.key + 'Readable';
            
            if (!value && metadata[readableKey]) {
                value = metadata[readableKey];
            }
            
            // Skip if not found
            if (!value) continue;
            
            foundAny = true;
            
            // Add to summary
            summary += `
                <div class="col-md-6 mb-3">
                    <div class="d-flex align-items-center">
                        <div class="icon-container text-primary me-2">
                            <i class="fas fa-${item.icon}"></i>
                        </div>
                        <div>
                            <div class="text-muted small">${item.label}</div>
                            <div>${value}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        summary += '</div>';
        
        if (!foundAny) {
            metadataSummary.innerHTML = '<p class="text-muted">No summary information available.</p>';
        } else {
            metadataSummary.innerHTML = summary;
        }
    }
    
    // Function to populate metadata table
    function populateMetadataTable(metadata) {
        metadataTable.innerHTML = '';
        
        // Sort keys alphabetically
        const sortedKeys = Object.keys(metadata).sort();
        
        for (const key of sortedKeys) {
            const value = metadata[key];
            
            // Create row
            const row = document.createElement('tr');
            
            // Create and add field cell
            const fieldCell = document.createElement('td');
            fieldCell.textContent = key;
            row.appendChild(fieldCell);
            
            // Create and add value cell
            const valueCell = document.createElement('td');
            valueCell.textContent = value;
            row.appendChild(valueCell);
            
            // Add row to table
            metadataTable.appendChild(row);
        }
    }
    
    // Function to display privacy concerns
    function displayPrivacyConcerns(concerns) {
        if (!concerns || concerns.length === 0) {
            privacyCard.classList.add('d-none');
            return;
        }
        
        // Show privacy card
        privacyCard.classList.remove('d-none');
        
        // Clear previous concerns
        privacyList.innerHTML = '';
        
        // Add each concern
        concerns.forEach(concern => {
            const item = document.createElement('li');
            item.className = 'list-group-item bg-dark';
            
            item.innerHTML = `
                <div class="d-flex flex-column">
                    <div class="d-flex align-items-start">
                        <div class="me-2 text-danger">
                            <i class="fas fa-exclamation-circle"></i>
                        </div>
                        <div>
                            <strong>${concern.field}</strong>
                            <p class="mb-1">${concern.description}</p>
                            <div class="text-muted small">Value: ${concern.value}</div>
                        </div>
                    </div>
                </div>
            `;
            
            privacyList.appendChild(item);
        });
    }
    
    // Function to check for location data
    function checkForLocationData(metadata) {
        let latitude = null;
        let longitude = null;
        
        // Check for standard GPS coordinates
        if (metadata.GPSLatitude && metadata.GPSLongitude) {
            latitude = parseFloat(metadata.GPSLatitude);
            longitude = parseFloat(metadata.GPSLongitude);
        }
        
        // Look for other GPS field formats
        if (!latitude || !longitude) {
            for (const key in metadata) {
                if (key.toLowerCase().includes('latitude')) {
                    latitude = parseFloat(metadata[key]);
                }
                if (key.toLowerCase().includes('longitude')) {
                    longitude = parseFloat(metadata[key]);
                }
            }
        }
        
        // If we found valid coordinates, display the map
        if (latitude && longitude && !isNaN(latitude) && !isNaN(longitude)) {
            displayMap(latitude, longitude);
        } else {
            locationCard.classList.add('d-none');
        }
    }
    
    // Function to display map
    function displayMap(latitude, longitude) {
        // Show location card
        locationCard.classList.remove('d-none');
        
        // Set coordinates display
        document.getElementById('coordinates-display').textContent = 
            `Latitude: ${latitude.toFixed(6)}, Longitude: ${longitude.toFixed(6)}`;
        
        // Initialize map if it doesn't exist
        if (!map) {
            map = L.map('map').setView([latitude, longitude], 13);
            
            // Add tile layer (OpenStreetMap)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            // Add marker
            marker = L.marker([latitude, longitude]).addTo(map);
        } else {
            // Update map view and marker position
            map.setView([latitude, longitude], 13);
            marker.setLatLng([latitude, longitude]);
        }
    }
    
    // Function to show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
    }
    
    // Function to reset UI
    function resetUI() {
        resultContainer.classList.add('d-none');
        errorContainer.classList.add('d-none');
        loadingContainer.classList.add('d-none');
        privacyCard.classList.add('d-none');
        locationCard.classList.add('d-none');
        metadataTable.innerHTML = '';
        metadataSummary.innerHTML = '';
        filenameElement.textContent = '';
        
        // Reset map if it exists
        if (map) {
            map.remove();
            map = null;
            marker = null;
        }
    }
});
