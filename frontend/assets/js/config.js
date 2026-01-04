const CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:8000',
    ENDPOINTS: {
        LOGIN: '/api/auth/login/',
        SEND_OTP: '/api/auth/send-otp/',
        VERIFY_OTP: '/api/auth/verify-otp/',
        SET_PASSWORD: '/api/auth/set-password/',
        USER_PROFILE: '/api/auth/profile/',
        CHANGE_PASSWORD: '/api/auth/change-password/',
        ITEMS: '/api/items/', 
        TAGS: '/api/tags/',  
    }
};

const DEFAULT_COORDS = [35.7036, 51.3515];
const DEFAULT_ZOOM = 18;