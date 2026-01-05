document.addEventListener('DOMContentLoaded', () => {
    checkAuthUI();

    if (document.body.classList.contains('protected-page')) {
        requireAuth();
    }

    const loginForm = document.getElementById('login-form');
    const otpStep1 = document.getElementById('otp-step-1');
    const otpStep2 = document.getElementById('otp-step-2');
    const signupEmailInput = document.getElementById('signup-email');
    
    let userEmail = '';

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const btn = e.target.querySelector('button');
            
            try {
                btn.textContent = 'در حال ورود...';
                btn.disabled = true;
                await ApiService.login(email, password);
                window.location.href = 'index.html';
            } catch (error) {
                console.error(error);
                alert('اطلاعات ورود صحیح نیست');
                btn.textContent = 'ورود به حساب';
                btn.disabled = false;
            }
        });
    }

    if (otpStep1) {
        otpStep1.addEventListener('submit', async (e) => {
            e.preventDefault();
            userEmail = signupEmailInput.value;
            const btn = e.target.querySelector('button');

            try {
                btn.textContent = 'ارسال کد...';
                btn.disabled = true;
                await ApiService.sendOtp(userEmail);
                alert('کد تایید به ایمیل شما ارسال شد. لطفا صندوق ورودی یا اسپم را بررسی کنید.');
                otpStep1.classList.add('hidden');
                otpStep2.classList.remove('hidden');
            } catch (error) {
                alert('خطا: ' + error.message);
                btn.textContent = 'دریافت کد تایید';
                btn.disabled = false;
            }
        });
    }

    if (otpStep2) {
        otpStep2.addEventListener('submit', async (e) => {
            e.preventDefault();
            const otp = document.getElementById('otp-code').value;
            const password = document.getElementById('signup-password').value;
            const firstName = document.getElementById('first-name').value;
            const lastName = document.getElementById('last-name').value;
            const btn = e.target.querySelector('button');

            try {
                btn.textContent = 'در حال ثبت...';
                btn.disabled = true;
                
                await ApiService.verifyRegister(userEmail, otp, password, firstName, lastName);
                
                alert('ثبت نام موفقیت‌آمیز بود! لطفا وارد شوید.');
                window.location.href = 'login.html';
            } catch (error) {
                console.error(error);
                alert('خطا در ثبت نام: ' + error.message);
                btn.textContent = 'تکمیل ثبت نام';
                btn.disabled = false;
            }
        });
    }
});

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = 'index.html';
}

function checkAuthUI() {
    const token = localStorage.getItem('access_token');
    const authLinks = document.getElementById('auth-links');
    const userLinks = document.getElementById('user-links');

    if (token) {
        if (authLinks) authLinks.classList.add('hidden');
        if (userLinks) userLinks.classList.remove('hidden');
    } else {
        if (authLinks) authLinks.classList.remove('hidden');
        if (userLinks) userLinks.classList.add('hidden');
    }
}

function requireAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
    }
}