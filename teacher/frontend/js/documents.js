// Document Management
const DocumentManager = {
    async loadDocuments() {
        try {
            const data = await API.fetchDocuments();
            
            AppState.setDocuments(data.documents);
            
            // Update stats
            document.getElementById('totalMaterials').textContent = data.count;
            
            // Render filters
            FilterManager.renderClassFilters(data.classes);
            FilterManager.renderSubjectFilters(data.subjects);
            
            // Render documents
            this.filterDocuments();
            
        } catch (error) {
            console.error('Error loading documents:', error);
            document.getElementById('documentsGrid').innerHTML = `
                <div class="col-span-full text-center py-12 text-red-500">
                    <iconify-icon icon="solar:danger-circle-linear" class="text-4xl"></iconify-icon>
                    <p class="mt-2 text-sm font-medium">Error loading documents</p>
                    <p class="text-xs text-zinc-400 mt-1">${error.message}</p>
                    <p class="text-xs text-zinc-400 mt-1">Make sure the FastAPI server is running</p>
                </div>
            `;
        }
    },

    filterDocuments() {
        const searchQuery = document.getElementById('searchInput')?.value || '';
        const filtered = AppState.getFilteredDocuments(searchQuery);

        // Update counts
        document.getElementById('filteredMaterials').textContent = filtered.length;
        
        // Render documents
        this.renderDocuments(filtered);
        
        // Update filter counts
        FilterManager.updateFilterCounts();
    },

    renderDocuments(documents) {
        const grid = document.getElementById('documentsGrid');
        
        if (documents.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-12 text-zinc-400">
                    <iconify-icon icon="solar:folder-open-linear" class="text-4xl"></iconify-icon>
                    <p class="mt-2 text-sm">No documents found</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = documents.map((file, index) => {
            const iconInfo = Utils.getSubjectIcon(file.subject);
            const fileSize = Utils.formatFileSize(file.size);
            const uploadDate = Utils.formatDate(file.lastModified);
            const menuId = 'menu-' + Utils.sanitizeId(file.key);
            const dataIndex = index;
            
            return `
                <article class="group bg-white rounded-xl border border-zinc-200 p-5 shadow-sm hover:shadow-md hover:border-zinc-300 transition-all duration-200 flex flex-col relative overflow-hidden cursor-pointer">
                    <div class="absolute top-0 left-0 w-full h-1 bg-[#1E3A8A] opacity-80"></div>
                    
                    <div class="flex items-start justify-between mb-4 mt-1">
                        <div class="w-10 h-10 bg-${iconInfo.color}-50 text-${iconInfo.color}-600 rounded-lg flex items-center justify-center ring-1 ring-inset ring-${iconInfo.color}-600/10">
                            <iconify-icon icon="${iconInfo.icon}" class="text-xl"></iconify-icon>
                        </div>
                        <div class="relative">
                            <button onclick="DocumentManager.toggleMenu(event, ${dataIndex})" class="text-zinc-400 hover:text-zinc-900 opacity-0 group-hover:opacity-100 transition-opacity p-1">
                                <iconify-icon icon="solar:menu-dots-bold" class="text-lg"></iconify-icon>
                            </button>
                            <div id="${menuId}" class="hidden absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border border-zinc-200 py-1 z-50">
                                <button onclick="DocumentManager.downloadFile(${dataIndex})" class="w-full text-left px-4 py-2 text-sm text-zinc-700 hover:bg-zinc-50 flex items-center gap-2">
                                    <iconify-icon icon="solar:download-minimalistic-linear"></iconify-icon>
                                    Download
                                </button>
                                <button onclick="Modals.showRenameModal(${dataIndex})" class="w-full text-left px-4 py-2 text-sm text-zinc-700 hover:bg-zinc-50 flex items-center gap-2">
                                    <iconify-icon icon="solar:pen-linear"></iconify-icon>
                                    Rename
                                </button>
                                <button onclick="Modals.showDeleteModal(${dataIndex})" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
                                    <iconify-icon icon="solar:trash-bin-minimalistic-linear"></iconify-icon>
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="mb-5 flex-1">
                        <div class="flex items-center gap-2 mb-1.5">
                            <span class="text-[10px] font-bold text-[#1E3A8A] uppercase tracking-wider px-2 py-0.5 bg-blue-50 rounded">Class ${file.class}</span>
                            <span class="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider">${Utils.escapeHtml(file.subject)}</span>
                        </div>
                        <h3 class="text-sm font-medium text-zinc-900 leading-snug break-words group-hover:text-[#1E3A8A] transition-colors">
                            ${Utils.escapeHtml(file.key)}
                        </h3>
                        <div class="mt-2 flex items-center gap-2">
                            <span class="inline-flex items-center rounded-md bg-zinc-50 px-1.5 py-0.5 text-[10px] font-medium text-zinc-600 ring-1 ring-inset ring-zinc-500/10 border border-zinc-200">PDF</span>
                            <span class="text-xs text-zinc-400">${fileSize}</span>
                        </div>
                    </div>

                    <div class="pt-4 border-t border-zinc-100 flex items-center justify-between mt-auto">
                        <span class="text-xs text-zinc-500 flex items-center gap-1.5">
                            <iconify-icon icon="solar:calendar-linear" class="text-zinc-400"></iconify-icon> 
                            <time datetime="${file.lastModified}">${uploadDate}</time>
                        </span>
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity -mr-1">
                            <button onclick="DocumentManager.downloadFile(${dataIndex})" class="p-1.5 text-zinc-400 hover:text-[#1E3A8A] hover:bg-blue-50 rounded-md transition-colors" title="Download">
                                <iconify-icon icon="solar:download-minimalistic-linear" class="text-base"></iconify-icon>
                            </button>
                        </div>
                    </div>
                </article>
            `;
        }).join('');
        
        // Store current filtered documents for reference by index
        this.currentDocuments = documents;
    },

    toggleMenu(event, index) {
        event.stopPropagation();
        const file = this.currentDocuments[index];
        const menuId = 'menu-' + Utils.sanitizeId(file.key);
        const menu = document.getElementById(menuId);
        
        // Close all other menus
        document.querySelectorAll('[id^="menu-"]').forEach(m => {
            if (m.id !== menuId) m.classList.add('hidden');
        });
        
        menu?.classList.toggle('hidden');
    },

    async downloadFile(index) {
        const file = this.currentDocuments[index];
        try {
            const data = await API.getDownloadUrl(file.key);
            window.open(data.url, '_blank');
        } catch (error) {
            console.error('Error downloading file:', error);
            Modals.showErrorModal('Download Failed', error.message);
        }
    }
};

// Close menus when clicking outside
document.addEventListener('click', () => {
    document.querySelectorAll('[id^="menu-"]').forEach(m => m.classList.add('hidden'));
});
