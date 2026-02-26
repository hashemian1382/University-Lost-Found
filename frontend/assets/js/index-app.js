// frontend/assets/js/index-app.js
const app = {
    map: null,
    markers: L.layerGroup(),
    hotspotMarkers: L.layerGroup(),
    userLocationMarker: null,
    allItems: [],
    hotspots: [],
    activeHotspots: new Set(),
    filters: { search: '', tags: [], type: 'ALL', sort: 'newest' },

    init: async function() {
        this.initMap();
        this.setupHotspots();
        await this.loadTags();
        await this.fetchItems();
        
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.updateFilter('search', e.target.value);
        });
    },

    initMap: function() {
        this.map = L.map('map', { zoomControl: false }).setView(DEFAULT_COORDS, DEFAULT_ZOOM);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(this.map);
        
        this.markers.addTo(this.map);
        this.hotspotMarkers.addTo(this.map);
        
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

    setupHotspots: function() {
        const centerLat = 35.7036;
        const centerLng = 51.3515;
        


        this.hotspots = [
            { id: 1, name: 'Zone A', latitude: centerLat + 0.0012, longitude: centerLng - 0.0010, radius: 50 },
            { id: 2, name: 'Zone B', latitude: centerLat + 0.0011, longitude: centerLng + 0.0006, radius: 55 },
            { id: 3, name: 'Zone C', latitude: centerLat + 0.0005, longitude: centerLng + 0.0013, radius: 50 },
            { id: 4, name: 'Zone D', latitude: centerLat + 0.0002, longitude: centerLng - 0.0016, radius: 45 },
            { id: 5, name: 'Zone E', latitude: centerLat - 0.0001, longitude: centerLng + 0.0001, radius: 40 },
            { id: 6, name: 'Zone F', latitude: centerLat - 0.0004, longitude: centerLng + 0.0008, radius: 45 },
            { id: 7, name: 'Zone G', latitude: centerLat - 0.0012, longitude: centerLng - 0.0013, radius: 50 },
            { id: 8, name: 'Zone H', latitude: centerLat - 0.0016, longitude: centerLng + 0.0004, radius: 55 },
            { id: 9, name: 'Zone I', latitude: centerLat - 0.0018, longitude: centerLng + 0.0018, radius: 50 },
            { id: 10, name: 'Zone J', latitude: centerLat - 0.0024, longitude: centerLng - 0.0008, radius: 45 },
            { id: 11, name: 'Zone K', latitude: centerLat - 0.0021, longitude: centerLng + 0.0009, radius: 40 },
	    { id: 12, name: 'Zone L', latitude: centerLat - 0.0012, longitude: centerLng - 0.0004, radius: 40 }
        ];
        
        this.renderHotspots();
    },

    renderHotspots: function() {
        this.hotspotMarkers.clearLayers();

        this.hotspots.forEach(hs => {
            const count = this.countItemsInRadius(hs.latitude, hs.longitude, hs.radius);
            
            const icon = L.divIcon({
                className: 'custom-div-icon',
                html: `<div class="hotspot-marker ${this.activeHotspots.has(hs.id) ? 'active' : ''}" data-id="${hs.id}">${count}</div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });

            const marker = L.marker([hs.latitude, hs.longitude], { icon: icon });
            
            marker.on('click', () => this.toggleHotspot(hs.id));
            
            this.hotspotMarkers.addLayer(marker);
        });
    },

    toggleHotspot: function(id) {
        if (this.activeHotspots.has(id)) {
            this.activeHotspots.delete(id);
        } else {
            this.activeHotspots.add(id);
        }
        this.renderHotspots();
        this.applyFilters();
    },

    countItemsInRadius: function(lat, lon, radius) {
        return this.allItems.filter(item => {
            const d = this.getDistance(lat, lon, item.latitude, item.longitude);
            return d <= radius;
        }).length;
    },

    getDistance: function(lat1, lon1, lat2, lon2) {
        const R = 6371e3;
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;

        const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    },

    loadTags: async function() {
        try {
            const tags = await ApiService.request(CONFIG.ENDPOINTS.TAGS);
            const container = document.getElementById('tags-scroll-container');
            
            if (container) {
                container.innerHTML = '';
                const tagsList = Array.isArray(tags) ? tags : (tags.results || []);
                
                tagsList.forEach(tag => {
                    const chip = document.createElement('div');
                    chip.className = 'tag-chip'; 
                    chip.textContent = tag.name;
                    chip.dataset.id = tag.id;

                    chip.onclick = () => {
                        const id = Number(tag.id);
                        const index = this.filters.tags.indexOf(id);
                        
                        if (index === -1) {
                            this.filters.tags.push(id);
                            chip.classList.add('active');
                        } else {
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
            this.renderHotspots();
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
            
            if (f.tags && f.tags.length > 0) {
                const itemTags = item.tags ? item.tags.map(Number) : [];
                const hasMatch = itemTags.some(t => f.tags.includes(t));
                if (!hasMatch) return false;
            }

            if (f.search) {
                const term = f.search.toLowerCase();
                const titleMatch = item.title.toLowerCase().includes(term);
                const descMatch = (item.description || '').toLowerCase().includes(term);
                if (!titleMatch && !descMatch) return false;
            }

            if (this.activeHotspots.size > 0) {
                let isInsideAny = false;
                for (let hsId of this.activeHotspots) {
                    const hs = this.hotspots.find(h => h.id === hsId);
                    if (hs) {
                        const d = this.getDistance(hs.latitude, hs.longitude, item.latitude, item.longitude);
                        if (d <= hs.radius) {
                            isInsideAny = true;
                            break;
                        }
                    }
                }
                if (!isInsideAny) return false;
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
            color: 'white', fillColor: color, fillOpacity: 1, radius: 7, weight: 2
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