// Chatbot JavaScript
// Handles AI-powered item description analysis and searching

let isAnalyzing = false;

function fillExample(element) {
    const exampleText = element.textContent;
    document.getElementById('description').value = exampleText;
}

async function analyzeDescription() {
    const description = document.getElementById('description').value.trim();
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsContainer = document.getElementById('resultsContainer');

    if (!description) {
        showError('Please enter a description of your item');
        return;
    }

    if (isAnalyzing) return;

    // Check if user is logged in
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        showError('Please login first to use the chatbot');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        return;
    }

    isAnalyzing = true;
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '🔄 Analyzing...';

    // Show loading state
    resultsContainer.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>AI is analyzing your description...</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/chatbot/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                description: description,
                search: true
            })
        });

        if (response.status === 401) {
            // Token expired, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            showError('Session expired. Please login again.');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to analyze description');
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while analyzing. Please try again.');
    } finally {
        isAnalyzing = false;
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 Analyze & Search';
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    const { extracted_info, similar_items, total_matches } = data;

    let html = '';

    // Display extracted information
    html += `
        <div class="extracted-info">
            <h3>
                📋 Extracted Information 
                <span class="type-badge ${extracted_info.type === 'LOST' ? 'type-lost' : 'type-found'}">
                    ${extracted_info.type}
                </span>
            </h3>
            <div class="info-item">
                <strong>Title:</strong> ${escapeHtml(extracted_info.title)}
            </div>
            <div class="info-item">
                <strong>Description:</strong> ${escapeHtml(extracted_info.description)}
            </div>
            <div class="info-item">
                <strong>Location:</strong> ${escapeHtml(extracted_info.location_description)}
            </div>
            ${extracted_info.latitude && extracted_info.longitude ? `
                <div class="info-item">
                    <strong>Coordinates:</strong> ${extracted_info.latitude.toFixed(6)}, ${extracted_info.longitude.toFixed(6)}
                </div>
            ` : ''}
            <div class="info-item">
                <strong>Tags:</strong>
                <div class="tags-list">
                    ${extracted_info.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            </div>
        </div>
    `;

    // Display similar items
    html += '<div class="similar-items">';
    
    if (total_matches > 0) {
        const itemType = extracted_info.type === 'LOST' ? 'Found' : 'Lost';
        html += `<h3>🎯 ${total_matches} Similar ${itemType} Item${total_matches !== 1 ? 's' : ''} Found</h3>`;
        
        similar_items.forEach(item => {
            const matchPercentage = Math.round(item.match_score * 100);
            const dateStr = new Date(item.created_at).toLocaleDateString();
            
            html += `
                <div class="item-card" onclick="viewItemDetails(${item.id})">
                    <h4>
                        ${escapeHtml(item.title)}
                        <span class="match-score">${matchPercentage}% Match</span>
                    </h4>
                    <p>${escapeHtml(truncateText(item.description, 120))}</p>
                    <div class="item-meta">
                        <span>📅 ${dateStr}</span>
                        <span>👤 ${escapeHtml(item.author_name)}</span>
                        ${item.tags_details && item.tags_details.length > 0 ? 
                            `<span>🏷️ ${item.tags_details.map(t => t.name).join(', ')}</span>` : 
                            ''}
                    </div>
                </div>
            `;
        });
    } else {
        html += `
            <h3>🔍 No Similar Items Found</h3>
            <div class="empty-state">
                <p>No matching ${extracted_info.type === 'LOST' ? 'found' : 'lost'} items in the database yet.</p>
                <p style="margin-top: 10px; font-size: 14px;">Try checking back later or post your item to help others find it!</p>
            </div>
        `;
    }
    
    html += '</div>';

    resultsContainer.innerHTML = html;
}

function viewItemDetails(itemId) {
    window.location.href = `item-details.html?id=${itemId}`;
}

function showError(message) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = `
        <div class="error-message">
            <strong>⚠️ Error:</strong> ${escapeHtml(message)}
        </div>
        <div class="empty-state">
            <p>Please try again or contact support if the problem persists.</p>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// Allow Enter key to submit (with Shift+Enter for new line)
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('description');
    if (textarea) {
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                analyzeDescription();
            }
        });
    }
});
