const app = {
    map: null,
    markers: L.layerGroup(),
    allItems: [],
    filters: {
        search: '',
        tag: '',
        type: 'ALL',
        sort: 'newest'
    },

    init: async function() {
        this.initMap();
        await this.loadTags();
        await this.fetchItems();
        
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.updateFilter('search', e.target.value);
        });
    },

    initMap: function() {
        this.map = L.map('map', { zoomControl: false }).setView([35.7036, 51.3515], 16);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(this.map);
        this.markers.addTo(this.map);
        L.control.zoom({ position: 'bottomleft' }).addTo(this.map);
    },

    loadTags: async function() {
        try {
            const tags = await ApiService.request(CONFIG.ENDPOINTS.TAGS);
            const select = document.getElementById('tag-filter');
            select.innerHTML = '<option value="">همه دسته‌بندی‌ها</option>';
            
            if (Array.isArray(tags)) {
                tags.forEach(tag => {
                    const opt = document.createElement('option');
                    opt.value = tag.id;
                    opt.textContent = tag.name;
                    select.appendChild(opt);
                });
            }
        } catch (e) {
            console.error('Tags loading failed', e);
        }
    },

    fetchItems: async function() {
        const container = document.getElementById('items-list');
        container.innerHTML = '<div style="text-align:center; padding:30px; color:#6b7280;">در حال دریافت اطلاعات...</div>';

        try {
            this.allItems = await ApiService.getItems();
            this.applyFilters();
        } catch (e) {
            container.innerHTML = '<div style="text-align:center; color:#ef4444;">خطا در برقراری ارتباط با سرور</div>';
        }
    },

    updateFilter: function(key, value) {
        if (key === 'type') {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
        }
        this.filters[key] = value;
        this.applyFilters();
    },

    applyFilters: function() {
        let result = this.allItems.filter(item => {
            const f = this.filters;
            
            if (f.type !== 'ALL' && item.type !== f.type) return false;
            
            if (f.tag && f.tag !== "") {
                if (!item.tags.includes(parseInt(f.tag))) return false;
            }
            
            if (f.search) {
                const term = f.search.toLowerCase();
                const titleMatch = item.title.toLowerCase().includes(term);
                const descMatch = (item.description || '').toLowerCase().includes(term);
                if (!titleMatch && !descMatch) return false;
            }

            return true;
        });

        if (this.filters.sort === 'newest') {
            result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        } else {
            result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        }

        this.renderList(result);
    },

    renderList: function(items) {
        const container = document.getElementById('items-list');
        container.innerHTML = '';
        this.markers.clearLayers();

        if (items.length === 0) {
            container.innerHTML = `
                <div style="text-align:center; padding:40px; color:#9ca3af; display:flex; flex-direction:column; align-items:center;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:10px;">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>موردی با این مشخصات یافت نشد</span>
                </div>`;
            return;
        }

        items.forEach(item => {
            container.appendChild(this.createCard(item));
            this.addPin(item);
        });
    },

    createCard: function(item) {
        const div = document.createElement('div');
        div.className = 'card';
        div.onclick = () => this.openModal(item);

        const isLost = item.type === 'LOST';
        const imgUrl = item.image 
            ? (item.image.startsWith('http') ? item.image : CONFIG.API_BASE_URL + item.image)
            : 'https://via.placeholder.com/400x200?text=No+Image';

        const dateStr = new Date(item.created_at).toLocaleDateString('fa-IR', { month: 'long', day: 'numeric' });
        
        let tagsHtml = '';
        if (item.tags_details) {
            tagsHtml = item.tags_details.slice(0, 3).map(t => `<span class="tag-pill">#${t.name}</span>`).join('');
        }

        div.innerHTML = `
            <div class="card-img-wrap">
                <img src="${imgUrl}" class="card-img">
                <span class="card-status ${isLost ? 'status-lost' : 'status-found'}">
                    ${isLost ? 'گمشده' : 'پیدا شده'}
                </span>
            </div>
            <div class="card-body">
                <h3 class="card-title">${item.title}</h3>
                <div class="card-info">
                    <span class="author-name">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        ${item.author_name || 'ناشناس'}
                    </span>
                    <span class="item-date">${dateStr}</span>
                </div>
                <div class="card-tags">${tagsHtml}</div>
            </div>
        `;
        return div;
    },

    addPin: function(item) {
        const color = item.type === 'LOST' ? '#ef4444' : '#10b981';
        const marker = L.circleMarker([item.latitude, item.longitude], {
            color: 'white', fillColor: color, fillOpacity: 1, radius: 9, weight: 2
        });
        marker.on('click', () => this.openModal(item));
        this.markers.addLayer(marker);
    },

    openModal: function(item) {
        const modal = document.getElementById('item-modal');
        document.getElementById('modal-title').textContent = item.title;
        document.getElementById('modal-desc').textContent = item.description || 'توضیحات ندارد';
        document.getElementById('modal-user').textContent = item.author_name || 'ناشناس';
        document.getElementById('modal-date').textContent = new Date(item.created_at).toLocaleDateString('fa-IR');
        
        const statusEl = document.getElementById('modal-status');
        statusEl.textContent = item.type === 'LOST' ? 'گمشده' : 'پیدا شده';
        statusEl.style.color = item.type === 'LOST' ? '#ef4444' : '#10b981';

        const imgEl = document.getElementById('modal-image');
        const imgUrl = item.image ? (item.image.startsWith('http') ? item.image : CONFIG.API_BASE_URL + item.image) : null;
        
        if (imgUrl) {
            imgEl.src = imgUrl;
            imgEl.style.display = 'block';
        } else {
            imgEl.style.display = 'none';
        }

        const tagBox = document.getElementById('modal-tags');
        tagBox.innerHTML = '';
        if (item.tags_details) {
            item.tags_details.forEach(t => {
                tagBox.innerHTML += `<span class="tag-pill" style="font-size:0.9rem;">#${t.name}</span>`;
            });
        }

        modal.classList.remove('hidden');
    },

    closeModal: function() {
        document.getElementById('item-modal').classList.add('hidden');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});