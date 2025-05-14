import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define potentially sensitive metadata fields
SENSITIVE_FIELDS = {
    # Location data
    'GPSLatitude': 'Contains your geographical latitude',
    'GPSLongitude': 'Contains your geographical longitude',
    'GPSInfo': 'Contains geographical positioning information',
    'GPSPosition': 'Contains your geographical position',
    'location': 'Contains location information',
    
    # Personal info
    'Author': 'Contains the document author name',
    'Creator': 'Contains information about who created the document',
    'Producer': 'Reveals which software was used to create the document',
    'Artist': 'Contains the name of the image creator',
    'Copyright': 'Contains copyright information that may include personal names',
    'Owner': 'Contains ownership information',
    'CameraOwnerName': 'Contains the camera owner\'s name',
    'UserComment': 'May contain personal comments or information',
    
    # Device info
    'Make': 'Reveals your camera/device manufacturer',
    'Model': 'Reveals your specific camera/device model',
    'Software': 'Reveals which software was used to create or edit the file',
    'HostComputer': 'Reveals your computer name',
    'SerialNumber': 'Contains your device serial number',
    'DeviceSettingDescription': 'Contains detailed device settings',
    
    # Timestamps
    'DateTime': 'Contains the date and time the image was taken',
    'DateTimeOriginal': 'Contains the original date and time the image was taken',
    'DateTimeDigitized': 'Contains when the image was digitized',
    'CreationDate': 'Contains when the document was created',
    'ModDate': 'Contains when the document was last modified',
}

def analyze_privacy(metadata):
    """
    Analyze metadata for privacy concerns
    
    Args:
        metadata: Dictionary of metadata to analyze
        
    Returns:
        List of dictionaries containing privacy concerns with field name and description
    """
    concerns = []
    
    try:
        # Look for sensitive fields in the metadata
        for field in metadata.keys():
            # Check if the field or a similar field is in our list of sensitive fields
            for sensitive_field, description in SENSITIVE_FIELDS.items():
                if sensitive_field.lower() in field.lower():
                    concerns.append({
                        'field': field,
                        'description': description,
                        'value': metadata[field]
                    })
                    break
        
        # Check for GPS coordinates specifically
        has_latitude = any('latitude' in key.lower() for key in metadata.keys())
        has_longitude = any('longitude' in key.lower() for key in metadata.keys())
        
        if has_latitude and has_longitude:
            # Check if we already added these as concerns
            if not any(concern['field'].lower() == 'gpslatitude' for concern in concerns):
                concerns.append({
                    'field': 'GPS Coordinates',
                    'description': 'This file contains precise location information that could reveal where the file was created',
                    'value': 'Geographical coordinates present'
                })
        
        # Check for email addresses in any field
        for field, value in metadata.items():
            if isinstance(value, str) and '@' in value and '.' in value.split('@')[1]:
                if not any(concern['field'] == field for concern in concerns):
                    concerns.append({
                        'field': field,
                        'description': 'This field may contain an email address',
                        'value': value
                    })
        
        return concerns
    
    except Exception as e:
        logger.error(f"Error analyzing privacy concerns: {str(e)}")
        return [{'field': 'Error', 'description': f'Failed to analyze privacy concerns: {str(e)}', 'value': 'Error'}]
