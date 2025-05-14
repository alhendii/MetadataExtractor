# MetaScan

![MetaScan Logo](https://img.shields.io/badge/MetaScan-Metadata%20Extraction%20Tool-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJjdXJyZW50Q29sb3IiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBjbGFzcz0iZmVhdGhlciBmZWF0aGVyLXNlYXJjaCI+PGNpcmNsZSBjeD0iMTEiIGN5PSIxMSIgcj0iOCI+PC9jaXJjbGU+PGxpbmUgeDE9IjIxIiB5MT0iMjEiIHgyPSIxNi42NSIgeTI9IjE2LjY1Ij48L2xpbmU+PC9zdmc+)

A powerful web application for extracting and analyzing metadata from images and PDF files, with a focus on privacy awareness.

![Screenshot](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-blue)

## ✨ Features

- 📁 Upload and analyze JPG, PNG, and PDF files
- 🔍 Extract comprehensive metadata including EXIF data
- 🚨 Identify privacy concerns in your files
- 🌍 View location data on an interactive map (if present)
- 💾 Download metadata as JSON or text files
- 🛡️ Secure processing - files are never stored on the server

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/metascan.git
cd metascan
```

2. Install required dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

4. Open your browser and navigate to `http://localhost:5000`

## 📋 Dependencies

- **Flask**: Web framework
- **exifread**: Extract EXIF data from images
- **PyPDF2 & PyMuPDF**: Extract metadata from PDF files
- **Pillow**: Image processing
- **Leaflet.js**: Interactive maps

## 💡 How It Works

1. **Upload**: Select a JPG, PNG, or PDF file using the browser.
2. **Process**: The file is processed in-memory to extract metadata.
3. **Analyze**: The app identifies potentially sensitive information.
4. **Display**: Results are presented in a user-friendly interface.
5. **Map View**: If GPS coordinates are found, they're displayed on a map.

## 🔒 Privacy

MetaScan is designed with privacy in mind:
- All file processing happens in-memory
- Files are never saved to the server
- No data is collected from users
- Clear warnings about sensitive information found in files

## 🛠️ Technical Overview

### Backend
- Python Flask server handles file uploads and metadata extraction
- Specialized libraries process different file types
- Privacy analyzer scans metadata for sensitive information

### Frontend
- Responsive Bootstrap UI with dark theme
- Interactive JavaScript displays for metadata visualization
- Leaflet.js integration for map display
- Client-side download functionality for extracted metadata

## 🧪 Supported File Types

| File Type | Extensions | Library Used |
|-----------|------------|--------------|
| Images    | JPG, JPEG, PNG | exifread, Pillow |
| Documents | PDF | PyPDF2, PyMuPDF (fitz) |

## 🔍 Example Metadata

### For an image:
```json
{
  "Make": "Canon",
  "Model": "Canon EOS 90D",
  "DateTime": "2023:10:02 15:42:10",
  "GPSLatitude": "37.7749",
  "GPSLongitude": "-122.4194"
}
```

### For a PDF:
```json
{
  "Author": "John Doe",
  "Producer": "Microsoft Word",
  "CreationDate": "D:20230325120000",
  "ModDate": "D:20230401153000"
}
```

## 🔮 Future Features

- [ ] Support for more file types (TIFF, DOCX, etc.)
- [ ] Metadata cleaning/removal tool
- [ ] Batch processing of multiple files
- [ ] Detailed privacy risk assessment
- [ ] Comparison of metadata between files

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

If you have any questions or suggestions, please open an issue on GitHub.

---

Built with ❤️ using Python Flask and modern web technologies.
