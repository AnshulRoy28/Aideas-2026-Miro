# Teacher Component - Document Management

Teacher-facing document management system for uploading and organizing educational materials.

## Quick Start

```bash
cd teacher
python server.py
```

Then open: `http://localhost:8000`

## Files

- `server.py` - FastAPI backend server
- `upload_to_s3.py` - CLI upload script
- `upload_with_metadata.py` - Upload with class/subject metadata
- `list_s3_metadata.py` - List S3 files and metadata
- `frontend/` - Web interface (HTML, CSS, JS)

## Features

- Upload PDFs with class/subject metadata
- Browse and filter documents
- Rename and delete documents
- Modern web interface

See main README for setup instructions.
