import logging
import io
from PIL import Image
import exifread
import PyPDF2
import fitz  # PyMuPDF
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def extract_metadata(file, file_ext):
    """
    Extract metadata from the provided file
    
    Args:
        file: The file object from request.files
        file_ext: The file extension (jpg, png, pdf)
        
    Returns:
        Dictionary containing extracted metadata
    """
    if file_ext in ['jpg', 'jpeg', 'png']:
        return extract_image_metadata(file)
    elif file_ext == 'pdf':
        return extract_pdf_metadata(file)
    else:
        logger.error(f"Unsupported file extension: {file_ext}")
        return None

def extract_image_metadata(file):
    """Extract metadata from image files using exifread"""
    metadata = {}
    try:
        # Reset file cursor
        file.seek(0)
        
        # Extract EXIF data
        tags = exifread.process_file(file)
        
        # Handle common metadata fields
        if tags:
            for tag, value in tags.items():
                # Skip thumbnail data
                if "thumbnail" in tag.lower():
                    continue
                
                # Clean tag name
                tag_name = tag.split("EXIF ", 1)[-1] if "EXIF " in tag else tag
                
                # Convert value to string and add to metadata
                metadata[tag_name] = str(value)
        
        # Process GPS coordinates if available
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            try:
                lat = _convert_to_degrees(tags['GPS GPSLatitude'].values)
                lon = _convert_to_degrees(tags['GPS GPSLongitude'].values)
                
                # Apply negative sign if needed
                if 'GPS GPSLatitudeRef' in tags and tags['GPS GPSLatitudeRef'].values == 'S':
                    lat = -lat
                if 'GPS GPSLongitudeRef' in tags and tags['GPS GPSLongitudeRef'].values == 'W':
                    lon = -lon
                
                metadata['GPSLatitude'] = str(lat)
                metadata['GPSLongitude'] = str(lon)
            except Exception as e:
                logger.error(f"Error processing GPS data: {str(e)}")
        
        # If EXIF data is missing or empty, try using Pillow
        if not metadata:
            file.seek(0)
            img = Image.open(file)
            img_info = img.info
            
            # Extract basic image properties
            metadata['Image Format'] = img.format
            metadata['Image Size'] = f"{img.width} x {img.height}"
            metadata['Image Mode'] = img.mode
            
            # Add any additional info from img.info
            for key, value in img_info.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = str(value)
            
        # Add human-readable date if available
        if 'DateTime' in metadata:
            try:
                date_str = metadata['DateTime']
                date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                metadata['DateTimeReadable'] = date_obj.strftime('%B %d, %Y at %I:%M %p')
            except Exception as e:
                logger.error(f"Error processing date: {str(e)}")
                
        return metadata
    
    except Exception as e:
        logger.error(f"Error extracting image metadata: {str(e)}")
        return {'Error': f'Failed to extract metadata: {str(e)}'}

def extract_pdf_metadata(file):
    """Extract metadata from PDF files using PyPDF2 and PyMuPDF"""
    metadata = {}
    try:
        # Reset file cursor
        file.seek(0)
        
        # First try with PyPDF2
        pdf_reader = PyPDF2.PdfReader(file)
        if pdf_reader.metadata:
            for key, value in pdf_reader.metadata.items():
                # Clean up key name (remove leading '/')
                clean_key = key[1:] if key.startswith('/') else key
                metadata[clean_key] = str(value)
        
        # Get additional info
        metadata['Page Count'] = len(pdf_reader.pages)
        
        # If metadata is limited, try with PyMuPDF (fitz)
        if len(metadata) <= 1:
            file.seek(0)
            file_bytes = file.read()
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for key, value in doc.metadata.items():
                    if value:
                        metadata[key] = str(value)
                
                # Get page count if not already set
                if 'Page Count' not in metadata:
                    metadata['Page Count'] = len(doc)
        
        # Format dates for better readability
        date_fields = ['CreationDate', 'ModDate']
        for field in date_fields:
            if field in metadata:
                try:
                    # Handle PDF date format (D:YYYYMMDDHHmmSS)
                    date_str = metadata[field]
                    if date_str.startswith('D:'):
                        date_str = date_str[2:]
                        # Basic format: YYYYMMDDHHmmSS
                        if len(date_str) >= 14:
                            year = date_str[0:4]
                            month = date_str[4:6]
                            day = date_str[6:8]
                            hour = date_str[8:10]
                            minute = date_str[10:12]
                            second = date_str[12:14]
                            
                            readable_date = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                            metadata[f"{field}Readable"] = readable_date
                except Exception as e:
                    logger.error(f"Error processing date {field}: {str(e)}")
        
        return metadata
    
    except Exception as e:
        logger.error(f"Error extracting PDF metadata: {str(e)}")
        return {'Error': f'Failed to extract metadata: {str(e)}'}

def _convert_to_degrees(value):
    """Helper function to convert GPS coordinates from degrees/minutes/seconds to decimal degrees"""
    degrees = float(value[0].num) / float(value[0].den)
    minutes = float(value[1].num) / float(value[1].den)
    seconds = float(value[2].num) / float(value[2].den)
    
    return degrees + (minutes / 60.0) + (seconds / 3600.0)
