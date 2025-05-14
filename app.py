import os
import logging
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import json
from utils.metadata_extractor import extract_metadata
from utils.privacy_analyzer import analyze_privacy

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    """Extract metadata from uploaded file"""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No file selected'
        }), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': 'File type not supported. Allowed types: JPG, PNG, PDF'
        }), 400
    
    try:
        # Get the filename safely
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Extract metadata
        metadata = extract_metadata(file, file_ext)
        if not metadata:
            return jsonify({
                'status': 'error',
                'message': 'Unable to extract metadata from this file'
            }), 400
        
        # Analyze for privacy concerns
        privacy_concerns = analyze_privacy(metadata)
        
        # Prepare final response
        response = {
            'status': 'success',
            'filename': filename,
            'metadata': metadata,
            'privacy_concerns': privacy_concerns
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing file: {str(e)}'
        }), 500

@app.route('/download', methods=['POST'])
def download_metadata():
    """Generate downloadable metadata file"""
    try:
        data = request.json
        if not data or 'metadata' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No metadata provided'
            }), 400
        
        metadata = data['metadata']
        format_type = data.get('format', 'json')
        
        if format_type == 'json':
            return jsonify({
                'status': 'success',
                'format': 'json',
                'data': json.dumps(metadata, indent=2)
            })
        else:  # text format
            # Convert metadata to text
            text_data = ""
            for key, value in metadata.items():
                text_data += f"{key}: {value}\n"
            
            return jsonify({
                'status': 'success',
                'format': 'text',
                'data': text_data
            })
            
    except Exception as e:
        logging.error(f"Error generating download: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error generating download: {str(e)}'
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
