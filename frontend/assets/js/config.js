const CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:8000',
    ENDPOINTS: {
        // Auth
        LOGIN: '/api/auth/login/',
        SEND_OTP: '/api/auth/send-otp/',
        VERIFY_OTP: '/api/auth/verify-otp/',
        SET_PASSWORD: '/api/auth/set-password/',
        USER_PROFILE: '/api/auth/profile/',
        CHANGE_PASSWORD: '/api/auth/change-password/',
        

        ITEMS: '/api/items/', 
        TAGS: '/api/tags/',
        

        COMMENTS_ADD: '/api/comments/add/',
        REPORT: '/api/report/',
    }
};

const DEFAULT_COORDS = [35.7026, 51.3509];
const DEFAULT_ZOOM = 17;
