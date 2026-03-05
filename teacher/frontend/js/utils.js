// Utility Functions
const Utils = {
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    },

    getSubjectIcon(subject) {
        return CONFIG.SUBJECT_ICONS[subject] || CONFIG.SUBJECT_ICONS['General'];
    },

    sanitizeId(str) {
        return str.replace(/[^a-zA-Z0-9]/g, '_');
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
