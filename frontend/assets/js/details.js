// frontend/assets/js/details.js
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');

    if (!itemId) {
        alert('آیتم یافت نشد');
        window.location.href = 'index.html';
        return;
    }

    try {
        const item = await ApiService.request(`${CONFIG.ENDPOINTS.ITEMS}${itemId}/`);
        renderDetails(item);
        initDetailMap(item.latitude, item.longitude);
        
        loadComments(itemId);
        
        const submitBtn = document.getElementById('btn-submit-comment');
        if (submitBtn) {
            submitBtn.onclick = () => handleSubmitComment(itemId);
        }

    } catch (error) {
        console.error(error);
        alert('خطا در دریافت اطلاعات آیتم');
        window.location.href = 'index.html';
    }
});

function renderDetails(item) {
    document.title = item.title + ' - جزئیات';
    
    setText('item-title', item.title);
    setText('item-desc', item.description || 'بدون توضیحات');
    setText('item-author', item.author_name || 'کاربر ناشناس');
    
    const dateStr = new Date(item.created_at).toLocaleDateString('fa-IR', { 
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
    setText('item-date', dateStr);

    const statusEl = document.getElementById('item-status');
    const isLost = item.type === 'LOST';
    statusEl.textContent = isLost ? 'گمشده' : 'پیدا شده';
    statusEl.className = `status-badge ${isLost ? 'status-lost' : 'status-found'}`;

    const imgEl = document.getElementById('item-image');
    if (item.image) {
        imgEl.src = item.image.startsWith('http') ? item.image : `${CONFIG.API_BASE_URL}${item.image}`;
    } else {
        imgEl.src = 'assets/images/placeholder.png';
    }
    imgEl.style.display = 'block';
    imgEl.onerror = function() { this.src = 'assets/images/placeholder.png'; };

    const tagsContainer = document.getElementById('item-tags');
    tagsContainer.innerHTML = '';
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

    const mapContainer = document.getElementById('detail-map');
    if (mapContainer._leaflet_id) return;

    const map = L.map('detail-map', {
        zoomControl: false,
        dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false
    }).setView([lat, lng], 18);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    const color = document.getElementById('item-status').classList.contains('status-lost') ? '#ef4444' : '#10b981';

    L.circleMarker([lat, lng], {
        color: 'white', fillColor: color, fillOpacity: 1, radius: 12, weight: 3
    }).addTo(map);
}

async function loadComments(itemId) {
    const listEl = document.getElementById('comments-list');
    listEl.innerHTML = '<div class="loading-spinner">در حال بارگذاری نظرات...</div>';
    
    try {
        const comments = await ApiService.getItemComments(itemId);
        listEl.innerHTML = ''; 
        
        if (!comments || comments.length === 0) {
            listEl.innerHTML = '<div style="text-align:center; color:#9ca3af; padding:15px;">هنوز نظری ثبت نشده است.</div>';
            return;
        }

        comments.forEach(comment => {
            listEl.appendChild(createCommentElement(comment));
        });

    } catch (error) {
        console.error('Error loading comments:', error);
        listEl.innerHTML = '<div style="text-align:center; color:red;">خطا در دریافت نظرات</div>';
    }
}

function createCommentElement(comment) {
    const dateStr = new Date(comment.created_at).toLocaleDateString('fa-IR', {
        month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    const wrapper = document.createElement('div');
    wrapper.style.marginBottom = '15px';

    const div = document.createElement('div');
    div.className = 'comment-item';
    div.innerHTML = `
        <div class="comment-header">
            <span class="comment-author">${comment.author_name || 'کاربر ناشناس'}</span>
            <span style="font-size:0.8rem; color:#888;">${dateStr}</span>
        </div>
        <div class="comment-body">${comment.text}</div>
    `;
    wrapper.appendChild(div);

    if (comment.replies && comment.replies.length > 0) {
        const repliesContainer = document.createElement('div');
        repliesContainer.style.marginRight = '25px';
        repliesContainer.style.borderRight = '2px solid #e5e7eb';
        repliesContainer.style.paddingRight = '10px';
        repliesContainer.style.marginTop = '10px';

        comment.replies.forEach(reply => {
            repliesContainer.appendChild(createCommentElement(reply));
        });
        wrapper.appendChild(repliesContainer);
    }

    return wrapper;
}

async function handleSubmitComment(itemId) {
    const inputEl = document.getElementById('comment-text');
    const btnEl = document.getElementById('btn-submit-comment');
    const text = inputEl.value.trim();

    if (!text) {
        alert('لطفا متن نظر را وارد کنید.');
        return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('برای ارسال نظر باید وارد حساب کاربری خود شوید.');
        window.location.href = 'login.html';
        return;
    }

    try {
        btnEl.disabled = true;
        btnEl.textContent = 'در حال ارسال...';

        const payload = {
            item: parseInt(itemId, 10),
            text: text
        };

        await ApiService.addComment(payload);

        inputEl.value = '';
        await loadComments(itemId);
        
    } catch (error) {
        console.error("Submit Error:", error);
        let errorMsg = 'خطا در ارسال نظر.';
        try {
            const errObj = JSON.parse(error.message);
            if (errObj.detail) errorMsg += ` ${errObj.detail}`;
        } catch(e) {}
        
        alert(errorMsg);
    } finally {
        btnEl.disabled = false;
        btnEl.textContent = 'ارسال پیام';
    }
}
