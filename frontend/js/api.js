// API Service
const API = {
    getAuthHeaders() {
        const token = localStorage.getItem('auth_token');
        return {
            'Authorization': `Bearer ${token}`
        };
    },

    async fetchDocuments() {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents`, {
            headers: this.getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                throw new Error('Unauthorized');
            }
            throw new Error('Failed to fetch documents');
        }
        return await response.json();
    },

    async deleteDocument(key) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/${encodeURIComponent(key)}`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                throw new Error('Unauthorized');
            }
            throw new Error('Failed to delete document');
        }
        return await response.json();
    },

    async renameDocument(key, newName) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/${encodeURIComponent(key)}/rename?new_name=${encodeURIComponent(newName)}`, {
            method: 'PUT',
            headers: this.getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                throw new Error('Unauthorized');
            }
            const error = await response.json();
            throw new Error(error.detail || 'Failed to rename document');
        }
        return await response.json();
    },

    async getDownloadUrl(key) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/${encodeURIComponent(key)}/download-url`, {
            headers: this.getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                throw new Error('Unauthorized');
            }
            throw new Error('Failed to get download URL');
        }
        return await response.json();
    }
};
