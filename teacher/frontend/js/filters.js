// Filter Management
const FilterManager = {
    renderClassFilters(classes) {
        const container = document.getElementById('classFilters');
        if (!classes || classes.length === 0) {
            container.innerHTML = '<div class="text-xs text-zinc-400 px-3 py-2">No classes available</div>';
            return;
        }
        
        container.innerHTML = classes.map(cls => {
            const isActive = AppState.selectedClass === cls;
            return `
                <button 
                    onclick="FilterManager.selectClass('${cls}')"
                    class="class-filter w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-white border border-zinc-200 text-zinc-900 shadow-sm' : 'text-zinc-600 hover:bg-zinc-200/50 hover:text-zinc-900'}"
                    data-class="${cls}"
                >
                    <div class="flex items-center gap-3">
                        ${isActive ? '<iconify-icon icon="solar:folder-with-files-linear" class="text-[#1E3A8A] text-lg"></iconify-icon>' : '<div class="w-1.5 h-1.5 rounded-full bg-[#1E3A8A] opacity-50"></div>'}
                        <span>Class ${cls}</span>
                    </div>
                    <span class="text-xs text-zinc-400 font-normal" id="count-class-${cls}">0</span>
                </button>
            `;
        }).join('');
    },

    renderSubjectFilters(subjects) {
        const container = document.getElementById('subjectFilters');
        if (!subjects || subjects.length === 0) {
            container.innerHTML = '<div class="text-xs text-zinc-400 px-3 py-2">No subjects available</div>';
            return;
        }
        
        container.innerHTML = subjects.map(subject => {
            const iconInfo = Utils.getSubjectIcon(subject);
            const isActive = AppState.selectedSubject === subject;
            return `
                <button 
                    onclick="FilterManager.selectSubject('${Utils.escapeHtml(subject)}')"
                    class="subject-filter w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive ? 'bg-white border border-zinc-200 text-zinc-900 shadow-sm' : 'text-zinc-600 hover:bg-zinc-200/50 hover:text-zinc-900'}"
                    data-subject="${Utils.escapeHtml(subject)}"
                >
                    <div class="flex items-center gap-3">
                        ${isActive ? `<iconify-icon icon="${iconInfo.icon}" class="text-[#1E3A8A] text-lg"></iconify-icon>` : '<div class="w-1.5 h-1.5 rounded-full bg-[#064E3B] opacity-50"></div>'}
                        <span>${Utils.escapeHtml(subject)}</span>
                    </div>
                    <span class="text-xs text-zinc-400 font-normal" id="count-subject-${Utils.sanitizeId(subject)}">0</span>
                </button>
            `;
        }).join('');
    },

    selectClass(cls) {
        AppState.setSelectedClass(AppState.selectedClass === cls ? null : cls);
        this.updateFilters();
        DocumentManager.filterDocuments();
    },

    selectSubject(subject) {
        AppState.setSelectedSubject(AppState.selectedSubject === subject ? null : subject);
        this.updateFilters();
        DocumentManager.filterDocuments();
    },

    clearClassFilter() {
        AppState.setSelectedClass(null);
        this.updateFilters();
        DocumentManager.filterDocuments();
    },

    clearSubjectFilter() {
        AppState.setSelectedSubject(null);
        this.updateFilters();
        DocumentManager.filterDocuments();
    },

    updateFilters() {
        const classes = [...new Set(AppState.allDocuments.map(doc => doc.class))].sort((a, b) => parseInt(a) - parseInt(b));
        const subjects = [...new Set(AppState.allDocuments.map(doc => doc.subject))].sort();
        
        this.renderClassFilters(classes);
        this.renderSubjectFilters(subjects);
        this.updateFilterCounts();
    },

    updateFilterCounts() {
        const classCounts = {};
        const subjectCounts = {};
        
        AppState.allDocuments.forEach(doc => {
            classCounts[doc.class] = (classCounts[doc.class] || 0) + 1;
            subjectCounts[doc.subject] = (subjectCounts[doc.subject] || 0) + 1;
        });
        
        Object.keys(classCounts).forEach(cls => {
            const el = document.getElementById(`count-class-${cls}`);
            if (el) el.textContent = classCounts[cls];
        });
        
        Object.keys(subjectCounts).forEach(subject => {
            const el = document.getElementById(`count-subject-${Utils.sanitizeId(subject)}`);
            if (el) el.textContent = subjectCounts[subject];
        });
    }
};
