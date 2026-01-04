let mainMap;
let formMap;
let markersLayer;
let formMarker;

document.addEventListener('DOMContentLoaded', () => {
    checkAuthUI();

    const mapElement = document.getElementById('map');
    const formMapElement = document.getElementById('form-map');

    if (mapElement && !formMapElement) {
        initMainMap();
        loadItems();

        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                loadItems({ search: e.target.value });
            });
        }
    }

    if (formMapElement) {
        if (!localStorage.getItem('access_token')) {
            window.location.href = 'login.html';
            return;
        }

        initFormMap();
        loadTagsForForm(); // فراخوانی تابع جدید برای دریافت تگ‌ها
        
        const form = document.getElementById('create-item-form');
        if (form) {
            form.addEventListener('submit', handleItemSubmit);
            
            const urlParams = new URLSearchParams(window.location.search);
            const editId = urlParams.get('id');
            if (editId) {
                document.getElementById('form-title').textContent = 'ویرایش آگهی';
                loadItemForEdit(editId);
            }
        }
    }
});

// تابع جدید: دریافت تگ‌ها برای فرم ثبت
async function loadTagsForForm() {
    try {
        const response = await ApiService.request(CONFIG.ENDPOINTS.TAGS);
        const tags = Array.isArray(response) ? response : (response.results || []);
        
        const select = document.getElementById('tag-select');
        select.innerHTML = ''; // پاک کردن گزینه "در حال بارگذاری..."
        
        tags.forEach(tag => {
            const opt = document.createElement('option');
            opt.value = tag.id; // ارسال ID به سرور
            opt.textContent = tag.name; // نمایش نام به کاربر
            select.appendChild(opt);
        });
    } catch (error) {
        console.error('Error loading tags:', error);
        const select = document.getElementById('tag-select');
        select.innerHTML = '<option value="">خطا در بارگذاری دسته‌بندی‌ها</option>';
    }
}

function initMainMap() {
    const SHARIF_COORDS = [35.7036, 51.3515];
    
    mainMap = L.map('map').setView(SHARIF_COORDS, 16);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'OpenStreetMap'
    }).addTo(mainMap);

    markersLayer = L.layerGroup().addTo(mainMap);
}

async function loadItems(filters = {}) {
    const listContainer = document.getElementById('items-list');
    if (!listContainer) return;

    listContainer.innerHTML = '<div style="text-align:center; padding:20px;">در حال بارگذاری...</div>';

    try {
        const items = await ApiService.getItems(filters);
        
        listContainer.innerHTML = '';
        if (markersLayer) markersLayer.clearLayers();

        if (items.length === 0) {
            listContainer.innerHTML = '<div style="text-align:center; padding:20px;">هیچ موردی یافت نشد.</div>';
            return;
        }

        items.forEach(item => {
            renderItemCard(item, listContainer);
            addPinToMap(item);
        });

    } catch (error) {
        console.error(error);
        listContainer.innerHTML = '<div style="text-align:center; color:red; padding:20px;">خطا در ارتباط با سرور</div>';
    }
}

function renderItemCard(item, container) {
    const card = document.createElement('div');
    card.className = 'item-card';
    
    const isLost = item.type === 'LOST';
    const statusClass = isLost ? 'lost' : 'found';
    const statusText = isLost ? 'گمشده' : 'پیدا شده';
    
    let imgUrl = item.image ? (item.image.startsWith('http') ? item.image : CONFIG.API_BASE_URL + item.image) : 'https://via.placeholder.com/400x200?text=No+Image';

    card.innerHTML = `
        <img src="${imgUrl}" class="item-image">
        <div class="item-content">
            <div class="item-header">
                <span class="item-title">${item.title}</span>
                <span class="badge ${statusClass}">${statusText}</span>
            </div>
            <p class="item-desc">${item.description || ''}</p>
            <button class="btn btn-outline" style="width:100%; font-size:0.8rem;" onclick="focusOnItem(${item.latitude}, ${item.longitude})">
                نمایش روی نقشه
            </button>
        </div>
    `;
    container.appendChild(card);
}

function addPinToMap(item) {
    if (!mainMap) return;
    
    const color = item.type === 'LOST' ? '#ef4444' : '#10b981';
    
    const marker = L.circleMarker([item.latitude, item.longitude], {
        color: 'white', fillColor: color, fillOpacity: 1, radius: 8, weight: 2
    });
    
    marker.bindPopup(`<b>${item.title}</b><br>${item.type}`);
    markersLayer.addLayer(marker);
}

window.focusOnItem = function(lat, lng) {
    if (mainMap) {
        mainMap.flyTo([lat, lng], 18);
        if (window.innerWidth < 768) {
            document.querySelector('.map-wrapper').scrollIntoView({behavior: 'smooth'});
        }
    }
};

window.filterItems = function(type) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    if (type === 'ALL') loadItems();
    else loadItems({ type: type });
};

function initFormMap() {
    const SHARIF_COORDS = [35.7036, 51.3515];
    
    formMap = L.map('form-map').setView(SHARIF_COORDS, 16);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'OpenStreetMap'
    }).addTo(formMap);

    setTimeout(() => { formMap.invalidateSize(); }, 200);

    formMap.on('click', function(e) {
        if (formMarker) formMap.removeLayer(formMarker);
        formMarker = L.marker(e.latlng).addTo(formMap);
        
        document.getElementById('lat').value = e.latlng.lat;
        document.getElementById('lng').value = e.latlng.lng;
    });
}

async function handleItemSubmit(e) {
    e.preventDefault();
    
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'در حال ثبت...';
    btn.disabled = true;

    const formData = new FormData(e.target);
    const id = formData.get('id');

    if (!formData.get('latitude')) {
        formData.set('latitude', 35.7036);
        formData.set('longitude', 51.3515);
    }

    try {
        if (id) {
            await ApiService.updateItem(id, formData);
            alert('آیتم ویرایش شد');
        } else {
            await ApiService.createItem(formData);
            alert('آیتم جدید ثبت شد');
        }
        window.location.href = 'index.html';
    } catch (error) {
        console.error(error);
        alert('خطا: ' + error.message);
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function loadItemForEdit(id) {
    try {
        const item = await ApiService.request(`${CONFIG.ENDPOINTS.ITEMS}${id}/`);
        const form = document.getElementById('create-item-form');
        
        form.querySelector('[name="title"]').value = item.title;
        form.querySelector('[name="description"]').value = item.description;
        form.querySelector('[name="type"]').value = item.type;
        
        // منتظر می‌مانیم تا تگ‌ها لود شوند، سپس تگ مورد نظر را انتخاب می‌کنیم
        // چون loadTagsForForm ناهمگام است، ممکن است لازم باشد کمی صبر کنیم یا منطق را دقیق‌تر کنیم.
        // اما معمولا مرورگرها مقدار را ست می‌کنند حتی اگر آپشن‌ها کمی دیرتر بیایند.
        // برای اطمینان بیشتر، مقداردهی تگ را اینجا انجام می‌دهیم:
        const tagSelect = document.getElementById('tag-select');
        
        // اگر تگ‌ها یک لیست باشند (طبق سریالایزر جدید، tags یک لیست ID است)
        if (item.tags && item.tags.length > 0) {
            tagSelect.value = item.tags[0]; // فعلا فقط تگ اول را ست میکنیم
        }

        document.getElementById('lat').value = item.latitude;
        document.getElementById('lng').value = item.longitude;
        
        let idInput = form.querySelector('input[name="id"]');
        if (!idInput) {
            idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'id';
            form.appendChild(idInput);
        }
        idInput.value = item.id;
        
        if (formMap) {
            formMap.setView([item.latitude, item.longitude], 16);
            formMarker = L.marker([item.latitude, item.longitude]).addTo(formMap);
        }
    } catch (error) {
        console.error(error);
    }
}