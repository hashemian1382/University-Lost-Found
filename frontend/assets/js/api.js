// frontend/assets/js/api.js
class ApiService {
    static getHeaders(auth = false, multipart = false) {
        const headers = {};
        if (!multipart) headers['Content-Type'] = 'application/json';
        const token = localStorage.getItem('access_token');
        if (auth && token) headers['Authorization'] = `Bearer ${token}`;
        return headers;
    }

    static async request(url, method = 'GET', body = null, auth = false) {
        const isMultipart = body instanceof FormData;
        const options = {
            method,
            headers: this.getHeaders(auth, isMultipart)
        };
        
        if (body) {
            options.body = isMultipart ? body : JSON.stringify(body);
        }

        const fullUrl = `${CONFIG.API_BASE_URL}${url}`;

        try {
            const response = await fetch(fullUrl, options);
            
            if (response.status === 401) {
                localStorage.clear();
                window.location.href = 'login.html';
                return;
            }

            if (response.status === 204) {
                return true;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(JSON.stringify(data));
            }
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    static async login(email, password) {
        const data = await this.request(CONFIG.ENDPOINTS.LOGIN, 'POST', { email, password });
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        return data;
    }

    static async sendOtp(email) {
        return await this.request(CONFIG.ENDPOINTS.SEND_OTP, 'POST', { email });
    }

    static async verifyRegister(email, otp, password, firstName, lastName) {
        await this.request(CONFIG.ENDPOINTS.VERIFY_OTP, 'POST', { email, otp_code: otp });
        return await this.request(CONFIG.ENDPOINTS.SET_PASSWORD, 'POST', { 
            email, otp_code: otp, password, first_name: firstName, last_name: lastName 
        });
    }

    static async getProfile() {
        return await this.request(CONFIG.ENDPOINTS.USER_PROFILE, 'GET', null, true);
    }

    static async updateProfile(data) {
        return await this.request(CONFIG.ENDPOINTS.USER_PROFILE, 'PATCH', data, true);
    }

    static async changePassword(oldPassword, newPassword) {
        return await this.request(CONFIG.ENDPOINTS.CHANGE_PASSWORD, 'POST', { 
            old_password: oldPassword, 
            new_password: newPassword 
        }, true);
    }

    static async getItems(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await this.request(`${CONFIG.ENDPOINTS.ITEMS}?${query}`, 'GET');
    }

    static async createItem(formData) {
        return await this.request(CONFIG.ENDPOINTS.ITEMS, 'POST', formData, true);
    }
    
    static async updateItem(id, formData) {
        return await this.request(`${CONFIG.ENDPOINTS.ITEMS}${id}/`, 'PATCH', formData, true);
    }

    static async deleteItem(id) {
        return await this.request(`${CONFIG.ENDPOINTS.ITEMS}${id}/`, 'DELETE', null, true);
    }

    static async getItemComments(itemId) {
        return await this.request(`${CONFIG.ENDPOINTS.ITEMS}${itemId}/comments/`, 'GET');
    }

    static async addComment(data) {
        return await this.request(CONFIG.ENDPOINTS.COMMENTS_ADD, 'POST', data, true);
    }
}
