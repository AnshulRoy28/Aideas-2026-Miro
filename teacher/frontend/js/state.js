// Application State
const AppState = {
    allDocuments: [],
    selectedClass: null,
    selectedSubject: null,
    fileToDelete: null,
    fileToRename: null,

    setDocuments(documents) {
        this.allDocuments = documents;
    },

    setSelectedClass(cls) {
        this.selectedClass = cls;
    },

    setSelectedSubject(subject) {
        this.selectedSubject = subject;
    },

    clearFilters() {
        this.selectedClass = null;
        this.selectedSubject = null;
    },

    getFilteredDocuments(searchQuery = '') {
        return this.allDocuments.filter(doc => {
            const matchesClass = !this.selectedClass || doc.class === this.selectedClass;
            const matchesSubject = !this.selectedSubject || doc.subject === this.selectedSubject;
            const matchesSearch = !searchQuery || doc.key.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesClass && matchesSubject && matchesSearch;
        });
    }
};
