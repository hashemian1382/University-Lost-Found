// frontend/assets/js/index-app.js
const app = {
    map: null,
    markers: L.layerGroup(),
    userLocationMarker: null,
    allItems: [],
    filters: { search: '', tags: [], type: 'ALL', sort: 'newest' },

    init: async function() {
        this.initMap();
        // ابتدا تگ‌ها لود می‌شوند تا رابط کاربری کامل شود
        await this.loadTags();
        // سپس آیتم‌ها دریافت می‌شوند
        await this.fetchItems();
        
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.updateFilter('search', e.target.value);
        });
    },

    initMap: function() {
        this.map = L.map('map', { zoomControl: false }).setView([35.7036, 51.3515], 16);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(this.map);
        this.markers.addTo(this.map);
        L.control.zoom({ position: 'bottomleft' }).addTo(this.map);

        const locateBtn = document.getElementById('locate-btn-index');
        if (locateBtn) {
            locateBtn.addEventListener('click', () => {
                if (!navigator.geolocation) {
                    alert('مرورگر شما از موقعیت مکانی پشتیبانی نمی‌کند.');
                    return;
                }
                
                const originalColor = locateBtn.style.color;
                locateBtn.style.color = '#1B3B6F';

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const { latitude, longitude } = position.coords;
                        
                        this.map.flyTo([latitude, longitude], 17);

                        if (this.userLocationMarker) {
                            this.map.removeLayer(this.userLocationMarker);
                        }

                        this.userLocationMarker = L.circleMarker([latitude, longitude], {
                            color: '#ffffff',
                            fillColor: '#3b82f6',
                            fillOpacity: 1,
                            radius: 8,
                            weight: 3
                        }).addTo(this.map);
                        
                        this.userLocationMarker.bindPopup("مکان شما").openPopup();
                        
                        locateBtn.style.color = originalColor;
                    },
                    (error) => {
                        console.error(error);
                        alert('دسترسی به موقعیت مکانی داده نشد یا خطایی رخ داد.');
                        locateBtn.style.color = originalColor;
                    },
                    { enableHighAccuracy: true }
                );
            });
        }
    },

    loadTags: async function() {
        try {
            const tags = await ApiService.request(CONFIG.ENDPOINTS.TAGS);
            // ما از کانتینر جدید که در HTML ساختیم استفاده می‌کنیم
            const container = document.getElementById('tags-scroll-container');
            
            if (container) {
                container.innerHTML = ''; // پاکسازی محتوای قبلی (اگر بود)
                const tagsList = Array.isArray(tags) ? tags : (tags.results || []);
                
                tagsList.forEach(tag => {
                    const chip = document.createElement('div');
                    // کلاس tag-chip که در CSS تعریف کردیم
                    chip.className = 'tag-chip'; 
                    chip.textContent = tag.name;
                    chip.dataset.id = tag.id;

                    chip.onclick = () => {
                        const id = Number(tag.id);
                        const index = this.filters.tags.indexOf(id);
                        
                        if (index === -1) {
                            // انتخاب تگ
                            this.filters.tags.push(id);
                            chip.classList.add('active');
                        } else {
                            // حذف انتخاب تگ
                            this.filters.tags.splice(index, 1);
                            chip.classList.remove('active');
                        }
                        this.applyFilters();
                    };

                    container.appendChild(chip);
                });
            }
        } catch (e) { console.error('Error loading tags:', e); }
    },

    fetchItems: async function() {
        const container = document.getElementById('items-list');
        container.innerHTML = '<div style="text-align:center; padding:30px; color:#6b7280;">در حال دریافت اطلاعات...</div>';
        try {
            const response = await ApiService.getItems();
            this.allItems = Array.isArray(response) ? response : (response.results || []);
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
            // فیلتر نوع (گمشده/پیداشده)
            if (f.type !== 'ALL' && item.type !== f.type) return false;
            
            // فیلتر تگ‌ها (اگر تگی انتخاب شده باشد)
            if (f.tags && f.tags.length > 0) {
                const itemTags = item.tags ? item.tags.map(Number) : [];
                // اگر حداقل یکی از تگ‌های آیتم با تگ‌های فیلتر همخوانی داشته باشد
                const hasMatch = itemTags.some(t => f.tags.includes(t));
                if (!hasMatch) return false;
            }

            // فیلتر جستجو
            if (f.search) {
                const term = f.search.toLowerCase();
                const titleMatch = item.title.toLowerCase().includes(term);
                const descMatch = (item.description || '').toLowerCase().includes(term);
                if (!titleMatch && !descMatch) return false;
            }
            return true;
        });

        // مرتب‌سازی نتایج
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
            container.innerHTML = `<div style="text-align:center; padding:40px; color:#9ca3af;">موردی یافت نشد</div>`;
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
        let imgUrl = 'assets/images/placeholder.png';
        if (item.image) {
            imgUrl = item.image.startsWith('http') ? item.image : `${CONFIG.API_BASE_URL}${item.image}`;
        }

        const dateStr = new Date(item.created_at).toLocaleDateString('fa-IR', { month: 'long', day: 'numeric' });
        
        let tagsHtml = '';
        if (item.tags_details) {
            // نمایش حداکثر 3 تگ در کارت برای جلوگیری از شلوغی
            tagsHtml = item.tags_details.slice(0, 3).map(t => `<span class="tag-pill">#${t.name}</span>`).join('');
        }

        div.innerHTML = `
            <div class="card-img-wrap">
                <img src="${imgUrl}" class="card-img" onerror="this.src='assets/images/placeholder.png'">
                <span class="card-status ${isLost ? 'status-lost' : 'status-found'}">
                    ${isLost ? 'گمشده' : 'پیدا شده'}
                </span>
            </div>
            <div class="card-body">
                <h3 class="card-title">${item.title}</h3>
                <div class="card-info">
                    <span class="author-name">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        ${item.author_name || 'کاربر'}
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
        if (item.image) {
            imgEl.src = item.image.startsWith('http') ? item.image : `${CONFIG.API_BASE_URL}${item.image}`;
        } else {
            imgEl.src = 'assets/images/placeholder.png';
        }
        imgEl.onerror = function() { this.src = 'assets/images/placeholder.png'; };

        const tagBox = document.getElementById('modal-tags');
        tagBox.innerHTML = '';
        if (item.tags_details) {
            item.tags_details.forEach(t => {
                tagBox.innerHTML += `<span class="tag-pill" style="font-size:0.9rem;">#${t.name}</span>`;
            });
        }

        const btn = document.getElementById('modal-details-btn');
        if (btn) btn.onclick = () => window.location.href = `item-details.html?id=${item.id}`;

        modal.classList.remove('hidden');
    },

    closeModal: function() {
        document.getElementById('item-modal').classList.add('hidden');
    }
};

document.addEventListener('DOMContentLoaded', () => { app.init(); });