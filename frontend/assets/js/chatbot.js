// Chatbot JavaScript
// Handles AI-powered item description analysis and searching

console.log('=== CHATBOT.JS LOADED ===');
console.log('localStorage keys:', Object.keys(localStorage));
console.log('access_token:', !!localStorage.getItem('access_token'));
console.log('refresh_token:', !!localStorage.getItem('refresh_token'));
console.log('============================');

let isAnalyzing = false;

function fillExample(element) {
    const exampleText = String(element.textContent || '');
    document.getElementById('description').value = exampleText;
}
window.fillExample = fillExample;

async function analyzeDescription() {
    const description = String(document.getElementById('description').value || '').trim();
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsContainer = document.getElementById('resultsContainer');

    console.log('=== ANALYZE START ===');
    console.log('Description:', description);

    if (!description) {
        showError('لطفاً توضیحات شیء خود را وارد کنید');
        return;
    }

    if (isAnalyzing) return;

    // Check if user is logged in
    const accessToken = String(localStorage.getItem('access_token') || '');
    console.log('Token found:', !!accessToken);
    
    if (!accessToken) {
        console.error('No access token!');
        showError('لطفاً ابتدا وارد شوید تا از چت‌بات استفاده کنید');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        return;
    }

    isAnalyzing = true;
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '🔄 در حال تحلیل...';

    // Show loading state
    resultsContainer.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>هوش مصنوعی در حال تحلیل توضیحات شماست...</p>
        </div>
    `;

    try {
        const url = `${CONFIG.API_BASE_URL}/api/chatbot/`;
        console.log('Request URL:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                description: String(description),
                search: true
            })
        });

        console.log('Response status:', response.status);

        if (response.status === 401) {
            console.error('401 Unauthorized!');
            // Token expired, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            showError('جلسه شما منقضی شده است. لطفاً دوباره وارد شوید.');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(String(errorData.error || 'تحلیل توضیحات با خطا مواجه شد'));
        }

        const data = await response.json();
        console.log('Success! Data:', data);
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(String(error.message || 'خطایی رخ داد. لطفاً دوباره تلاش کنید.'));
    } finally {
        isAnalyzing = false;
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 تحلیل و جستجو';
        console.log('=== END ANALYZE ===');
    }
}
window.analyzeDescription = analyzeDescription;

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    const { extracted_info, similar_items, total_matches } = data;

    let html = '';

    // Display extracted information
    const typeText = String(extracted_info.type || 'LOST') === 'LOST' ? 'گم شده' : 'پیدا شده';
    const typeClass = String(extracted_info.type || 'LOST') === 'LOST' ? 'type-lost' : 'type-found';
    
    html += `
        <div class="extracted-info">
            <h3>
                📋 اطلاعات استخراج شده 
                <span class="type-badge ${typeClass}">
                    ${typeText}
                </span>
            </h3>
            <div class="info-item">
                <strong>عنوان:</strong> ${escapeHtml(String(extracted_info.title || ''))}
            </div>
            <div class="info-item">
                <strong>توضیحات:</strong> ${escapeHtml(String(extracted_info.description || ''))}
            </div>
            <div class="info-item">
                <strong>مکان:</strong> ${escapeHtml(String(extracted_info.location_description || ''))}
            </div>
            ${extracted_info.latitude && extracted_info.longitude ? `
                <div class="info-item">
                    <strong>مختصات:</strong> ${Number(extracted_info.latitude).toFixed(6)}, ${Number(extracted_info.longitude).toFixed(6)}
                </div>
            ` : ''}
            <div class="info-item">
                <strong>برچسب‌ها:</strong>
                <div class="tags-list">
                    ${Array.isArray(extracted_info.tags) ? extracted_info.tags.map(tag => `<span class="tag">${escapeHtml(String(tag || ''))}</span>`).join('') : ''}
                </div>
            </div>
        </div>
    `;

    // Display similar items
    html += '<div class="similar-items">';
    
    const totalCount = Number(total_matches || 0);
    
    if (totalCount > 0) {
        const itemTypeText = String(extracted_info.type || 'LOST') === 'LOST' ? 'پیدا شده' : 'گم شده';
        const pluralText = totalCount !== 1 ? 'مورد' : 'مورد';
        html += `<h3>🎯 ${totalCount} ${pluralText} مشابه ${itemTypeText} پیدا شد</h3>`;
        
        if (Array.isArray(similar_items)) {
            similar_items.forEach(item => {
                const matchPercentage = Math.round(Number(item.match_score || 0) * 100);
                const dateStr = new Date(String(item.created_at || '')).toLocaleDateString('fa-IR');
                
                html += `
                    <div class="item-card" onclick="viewItemDetails(${Number(item.id || 0)})">
                        <h4>
                            ${escapeHtml(String(item.title || ''))}
                            <span class="match-score">${matchPercentage}% تطابق</span>
                        </h4>
                        <p>${escapeHtml(truncateText(String(item.description || ''), 120))}</p>
                        <div class="item-meta">
                            <span>📅 ${dateStr}</span>
                            <span>👤 ${escapeHtml(String(item.author_name || ''))}</span>
                            ${Array.isArray(item.tags_details) && item.tags_details.length > 0 ? 
                                `<span>🏷️ ${item.tags_details.map(t => String(t.name || '')).join('، ')}</span>` : 
                                ''}
                        </div>
                    </div>
                `;
            });
        }
    } else {
        const oppositeType = String(extracted_info.type || 'LOST') === 'LOST' ? 'پیدا شده' : 'گم شده';
        html += `
            <h3>🔍 موردی مشابه پیدا نشد</h3>
            <div class="empty-state">
                <p>هنوز هیچ مورد ${oppositeType} مشابهی در پایگاه داده وجود ندارد.</p>
                <p style="margin-top: 10px; font-size: 14px;">بعداً دوباره بررسی کنید یا شیء خود را ثبت کنید تا به دیگران کمک کنید!</p>
            </div>
        `;
    }
    
    html += '</div>';

    resultsContainer.innerHTML = html;
}

function viewItemDetails(itemId) {
    window.location.href = `item-details.html?id=${Number(itemId || 0)}`;
}
window.viewItemDetails = viewItemDetails;

function showError(message) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = `
        <div class="error-message">
            <strong>⚠️ خطا:</strong> ${escapeHtml(String(message || ''))}
        </div>
        <div class="empty-state">
            <p>لطفاً دوباره تلاش کنید یا اگر مشکل ادامه دارد با پشتیبانی تماس بگیرید.</p>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = String(text || '');
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    const str = String(text || '');
    const max = Number(maxLength || 100);
    if (str.length <= max) return str;
    return str.substr(0, max) + '...';
}

// Allow Enter key to submit (with Shift+Enter for new line)
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded!');
    
    const textarea = document.getElementById('description');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (textarea) {
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                analyzeDescription();
            }
        });
    }
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeDescription);
        console.log('Button listener attached');
    }
});
