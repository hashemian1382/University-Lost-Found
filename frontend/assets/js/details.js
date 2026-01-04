document.addEventListener('DOMContentLoaded', async () => {
    // گرفتن ID از URL
    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');

    if (!itemId) {
        alert('آیتم یافت نشد');
        window.location.href = 'index.html';
        return;
    }

    try {
        // دریافت اطلاعات از API
        const item = await ApiService.request(`${CONFIG.ENDPOINTS.ITEMS}${itemId}/`);
        renderDetails(item);
        initDetailMap(item.latitude, item.longitude);
    } catch (error) {
        console.error(error);
        alert('خطا در دریافت اطلاعات آیتم');
        window.location.href = 'index.html';
    }
});

function renderDetails(item) {
    document.title = item.title + ' - جزئیات';
    
    // پر کردن متون
    setText('item-title', item.title);
    setText('item-desc', item.description || 'بدون توضیحات');
    setText('item-author', item.author_name || 'کاربر ناشناس');
    setText('item-date', new Date(item.created_at).toLocaleDateString('fa-IR', { 
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    }));

    // وضعیت
    const statusEl = document.getElementById('item-status');
    const isLost = item.type === 'LOST';
    statusEl.textContent = isLost ? 'گمشده' : 'پیدا شده';
    statusEl.className = `status-badge ${isLost ? 'status-lost' : 'status-found'}`;

    // تصویر
    const imgEl = document.getElementById('item-image');
    if (item.image) {
        imgEl.src = item.image.startsWith('http') ? item.image : `${CONFIG.API_BASE_URL}${item.image}`;
    } else {
        imgEl.style.display = 'none';
    }

    // تگ‌ها
    const tagsContainer = document.getElementById('item-tags');
    if (item.tags_details) {
        item.tags_details.forEach(tag => {
            const span = document.createElement('span');
            span.className = 'tag-pill';
            span.textContent = `#${tag.name}`;
            tagsContainer.appendChild(span);
        });
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function initDetailMap(lat, lng) {
    if (!lat || !lng) return;

    const map = L.map('detail-map', {
        zoomControl: false,
        dragging: false,      // غیرفعال کردن حرکت نقشه برای حالت نمایشی
        scrollWheelZoom: false,
        doubleClickZoom: false
    }).setView([lat, lng], 18); // زوم بسیار بالا

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    const color = document.getElementById('item-status').classList.contains('status-lost') ? '#ef4444' : '#10b981';

    L.circleMarker([lat, lng], {
        color: 'white',
        fillColor: color,
        fillOpacity: 1,
        radius: 12,
        weight: 3
    }).addTo(map);
}