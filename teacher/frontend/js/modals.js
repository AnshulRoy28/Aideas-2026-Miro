// Modal Management
const Modals = {
    // Delete Modal
    showDeleteModal(index) {
        const file = DocumentManager.currentDocuments[index];
        AppState.fileToDelete = file.key;
        document.getElementById('deleteFileName').textContent = file.key;
        document.getElementById('deleteModal').classList.remove('hidden');
    },

    closeDeleteModal() {
        document.getElementById('deleteModal').classList.add('hidden');
        AppState.fileToDelete = null;
    },

    async confirmDelete() {
        if (!AppState.fileToDelete) return;

        const fileToDelete = AppState.fileToDelete;
        
        // Close delete modal and show progress
        this.closeDeleteModal();
        document.getElementById('deleteProgress').classList.remove('hidden');

        try {
            await API.deleteDocument(fileToDelete);
            document.getElementById('deleteProgress').classList.add('hidden');
            await DocumentManager.loadDocuments();
            this.showSuccessToast('Document deleted successfully');
        } catch (error) {
            console.error('Error deleting file:', error);
            document.getElementById('deleteProgress').classList.add('hidden');
            this.showErrorModal('Failed to delete document', error.message);
        }
    },

    // Rename Modal
    showRenameModal(index) {
        const file = DocumentManager.currentDocuments[index];
        AppState.fileToRename = file.key;
        document.getElementById('currentFileName').textContent = file.key;
        document.getElementById('newFileName').value = file.key.replace('.pdf', '');
        document.getElementById('renameModal').classList.remove('hidden');
        
        setTimeout(() => {
            const input = document.getElementById('newFileName');
            input.focus();
            input.select();
        }, 100);
    },

    closeRenameModal() {
        document.getElementById('renameModal').classList.add('hidden');
        AppState.fileToRename = null;
    },

    async confirmRename() {
        if (!AppState.fileToRename) return;

        const newName = document.getElementById('newFileName').value.trim();
        
        if (!newName) {
            this.showErrorModal('Invalid Name', 'Please enter a new name');
            return;
        }

        if (newName === AppState.fileToRename.replace('.pdf', '')) {
            this.showErrorModal('Same Name', 'New name is the same as current name');
            return;
        }

        try {
            await API.renameDocument(AppState.fileToRename, newName);
            this.closeRenameModal();
            await DocumentManager.loadDocuments();
            this.showSuccessToast('Document renamed successfully');
        } catch (error) {
            console.error('Error renaming file:', error);
            this.showErrorModal('Failed to rename document', error.message);
        }
    },

    // Error Modal
    showErrorModal(title, message) {
        document.getElementById('errorTitle').textContent = title;
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorModal').classList.remove('hidden');
    },

    closeErrorModal() {
        document.getElementById('errorModal').classList.add('hidden');
    },

    // Success Toast
    showSuccessToast(message) {
        const toast = document.getElementById('successToast');
        document.getElementById('successMessage').textContent = message;
        toast.classList.remove('hidden');
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    },

    // Initialize modal event listeners
    init() {
        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDeleteModal();
                this.closeRenameModal();
                this.closeErrorModal();
            }
        });

        // Close modals when clicking outside
        const deleteModal = document.getElementById('deleteModal');
        if (deleteModal) {
            deleteModal.addEventListener('click', (e) => {
                if (e.target.id === 'deleteModal') this.closeDeleteModal();
            });
        }

        const renameModal = document.getElementById('renameModal');
        if (renameModal) {
            renameModal.addEventListener('click', (e) => {
                if (e.target.id === 'renameModal') this.closeRenameModal();
            });
        }

        const errorModal = document.getElementById('errorModal');
        if (errorModal) {
            errorModal.addEventListener('click', (e) => {
                if (e.target.id === 'errorModal') this.closeErrorModal();
            });
        }

        // Submit rename on Enter key
        const newFileNameInput = document.getElementById('newFileName');
        if (newFileNameInput) {
            newFileNameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.confirmRename();
            });
        }
    }
};
