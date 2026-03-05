# EDU_VAULT Frontend - Modular Architecture

## Project Structure

```
frontend/
├── index.html              # Main HTML file
├── components/
│   └── modals.html        # All modal components
├── js/
│   ├── config.js          # Configuration (API URL, icons, etc.)
│   ├── state.js           # Application state management
│   ├── api.js             # API service layer
│   ├── utils.js           # Utility functions
│   ├── modals.js          # Modal management
│   ├── filters.js         # Filter management
│   └── documents.js       # Document management
└── css/
    └── (future custom styles)
```

## Module Responsibilities

### config.js
- API base URL configuration
- Subject icon mappings
- Global constants

### state.js
- Centralized application state
- Document storage
- Filter state (selected class/subject)
- State getters and setters

### api.js
- All API calls to backend
- Fetch documents
- Delete documents
- Rename documents
- Get download URLs

### utils.js
- Format file sizes
- Format dates
- Get subject icons
- Sanitize IDs
- Escape HTML

### modals.js
- Show/hide delete modal
- Show/hide rename modal
- Show/hide error modal
- Show success toast
- Modal event listeners

### filters.js
- Render class filters
- Render subject filters
- Handle filter selection
- Update filter counts
- Clear filters

### documents.js
- Load documents from API
- Render document cards
- Filter documents
- Toggle document menu
- Download files
- Coordinate with modals for delete/rename

## Features

✅ No browser alert() or confirm() popups
✅ Beautiful custom modals for all interactions
✅ Modular, maintainable code structure
✅ Separation of concerns
✅ Easy to extend and modify
✅ Clean error handling with error modal
✅ Success toast notifications

## Usage

1. Make sure the FastAPI server is running:
   ```bash
   python server.py
   ```

2. Open `frontend/index.html` in your browser

3. All modals and interactions are custom-designed
