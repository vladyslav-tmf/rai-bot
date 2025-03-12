const API_URL = 'http://localhost:8000/api/v1';

class AuthService {
    async login(email, password) {
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            if (!data.access_token) {
                throw new Error('Invalid server response: missing access token');
            }

            localStorage.setItem('token', data.access_token);
            window.location.href = '/';
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async register(email, password) {
        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }

            await this.login(email, password);
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }
}

class AuthManager {
    constructor() {
        this.authService = new AuthService();
        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');
        this.loginTab = document.getElementById('login-tab');
        this.registerTab = document.getElementById('register-tab');
        this.loginSection = document.getElementById('login-section');
        this.registerSection = document.getElementById('register-section');

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.registerForm.addEventListener('submit', (e) => this.handleRegister(e));

        this.loginTab.addEventListener('click', () => this.switchTab('login'));
        this.registerTab.addEventListener('click', () => this.switchTab('register'));
    }

    switchTab(tab) {
        if (tab === 'login') {
            this.loginTab.classList.add('active');
            this.registerTab.classList.remove('active');
            this.loginSection.style.display = 'block';
            this.registerSection.style.display = 'none';
        } else {
            this.loginTab.classList.remove('active');
            this.registerTab.classList.add('active');
            this.loginSection.style.display = 'none';
            this.registerSection.style.display = 'block';
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = this.loginForm.querySelector('input[type="email"]').value;
        const password = this.loginForm.querySelector('input[type="password"]').value;

        try {
            await this.authService.login(email, password);
        } catch (error) {
            console.error('Full login error:', error);
            alert(error.message || 'Login failed. Please check your credentials and try again.');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const email = this.registerForm.querySelector('input[type="email"]').value;
        const password = this.registerForm.querySelector('input[type="password"]').value;
        const confirmPassword = this.registerForm.querySelector('input[name="confirm-password"]').value;

        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        try {
            await this.authService.register(email, password);
        } catch (error) {
            console.error('Full registration error:', error);
            alert(error.message || 'Registration failed. Please try again.');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => new AuthManager());
