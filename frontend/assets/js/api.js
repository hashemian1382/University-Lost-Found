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
        if (body) options.body = isMultipart ? body : JSON.stringify(body);

        const response = await fetch(`${CONFIG.API_BASE_URL}${url}`, options);
        
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = 'login.html';
            return;
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(JSON.stringify(data) || 'API Request Failed');
        }
        return data;
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
        await this.request(CONFIG.ENDPOINTS.VERIFY_OTP, 'POST', { 
            email: email, 
            otp_code: otp 
        });

        return await this.request(CONFIG.ENDPOINTS.SET_PASSWORD, 'POST', { 
            email: email, 
            otp_code: otp,
            password: password,
            first_name: firstName,
            last_name: lastName
        });
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
}