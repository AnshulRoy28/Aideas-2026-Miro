// API Service
const API = {
    async fetchDocuments() {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents`);
        if (!response.ok) throw new Error('Failed to fetch documents');
        return await response.json();
    },

    async deleteDocument(key) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/${encodeURIComponent(key)}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete document');
        return await response.json();
    },

    async renameDocument(key, newName) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/${encodeURIComponent(key)}/rename?new_name=${encodeURIComponent(newName)}`, {
            method: 'PUT'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to rename document');
        }
        return await response.json();
    },

    async getDownloadUrl(key) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/${encodeURIComponent(key)}/download-url`);
        if (!response.ok) throw new Error('Failed to get download URL');
        return await response.json();
    }
};
