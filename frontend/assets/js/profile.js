document.addEventListener('DOMContentLoaded', async () => {
    // محافظت از صفحه
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'login.html';
        return;
    }

    await loadProfile();
    await loadUserItems();

    // فرم ویرایش مشخصات
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;
        
        try {
            btn.textContent = 'در حال ذخیره...';
            btn.disabled = true;

            const firstName = document.getElementById('profile-name').value;
            const lastName = document.getElementById('profile-family').value;

            await ApiService.updateProfile({ 
                first_name: firstName, 
                last_name: lastName 
            });

            alert('مشخصات با موفقیت بروزرسانی شد.');
        } catch (error) {
            console.error(error);
            alert('خطا در بروزرسانی مشخصات.');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });

    // فرم تغییر رمز
    document.getElementById('password-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const oldPass = document.getElementById('old-pass').value;
        const newPass = document.getElementById('new-pass').value;
        const confirmPass = document.getElementById('confirm-pass').value;

        if (newPass !== confirmPass) {
            alert('رمز عبور جدید و تکرار آن مطابقت ندارند.');
            return;
        }

        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;

        try {
            btn.textContent = 'در حال تغییر...';
            btn.disabled = true;

            await ApiService.changePassword(oldPass, newPass);
            
            alert('رمز عبور با موفقیت تغییر کرد.');
            e.target.reset();
        } catch (error) {
            console.error(error);
            alert('خطا: رمز عبور فعلی اشتباه است یا مشکلی پیش آمده.');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });
});

async function loadProfile() {
    try {
        const user = await ApiService.getProfile();
        document.getElementById('profile-email').value = user.email;
        document.getElementById('profile-name').value = user.first_name || '';
        document.getElementById('profile-family').value = user.last_name || '';
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function loadUserItems() {
    const tbody = document.getElementById('items-table-body');
    const emptyState = document.getElementById('empty-state');
    const filterType = document.getElementById('items-filter').value;
    
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">در حال بارگذاری...</td></tr>';

    try {
        // دریافت پروفایل برای گرفتن ID کاربر فعلی
        const user = await ApiService.getProfile();
        const currentUserId = user.id;

        // دریافت همه آیتم‌ها
        const items = await ApiService.getItems();
        const allItems = Array.isArray(items) ? items : (items.results || []);

        // فیلتر: فقط آیتم‌های من
        let myItems = allItems.filter(item => item.author === currentUserId);

        // آپدیت آمار
        document.getElementById('stat-total').textContent = myItems.length;
        document.getElementById('stat-active').textContent = myItems.length; 

        // فیلتر نوع (گمشده/پیداشده)
        if (filterType !== 'ALL') {
            myItems = myItems.filter(item => item.type === filterType);
        }

        tbody.innerHTML = '';

        if (myItems.length === 0) {
            emptyState.style.display = 'block';
        } else {
            emptyState.style.display = 'none';
            myItems.forEach(item => {
                const tr = document.createElement('tr');
                const isLost = item.type === 'LOST';
                const date = new Date(item.created_at).toLocaleDateString('fa-IR');

                tr.innerHTML = `
                    <td style="font-weight:600;">${item.title}</td>
                    <td>
                        <span class="status-badge ${isLost ? 'status-lost' : 'status-found'}">
                            ${isLost ? 'گمشده' : 'پیدا شده'}
                        </span>
                    </td>
                    <td>${date}</td>
                    <td>
                        <div style="display:flex; gap:8px;">
                            <a href="create-item.html?id=${item.id}" class="btn-primary" style="padding:4px 10px; border-radius:6px; font-size:0.8rem; text-decoration:none;">ویرایش</a>
                            <button onclick="deleteUserItem(${item.id})" style="background:#fee2e2; color:#ef4444; border:1px solid #fca5a5; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600; cursor:pointer;">حذف</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error(error);
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:red;">خطا در دریافت اطلاعات</td></tr>';
    }
}

// تابع حذف آیتم (باید به window متصل شود تا از داخل HTML قابل دسترسی باشد)
window.deleteUserItem = async function(itemId) {
    if (!confirm('آیا از حذف این آگهی اطمینان دارید؟ این عملیات غیرقابل بازگشت است.')) return;

    try {
        await ApiService.deleteItem(itemId);
        alert('آگهی با موفقیت حذف شد.');
        loadUserItems(); // رفرش لیست
    } catch (error) {
        console.error(error);
        alert('خطا در حذف آگهی.');
    }
};