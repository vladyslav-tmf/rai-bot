const API_URL = 'http://localhost:8000';

class ApiService {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...(this.token && { 'Authorization': `Bearer ${this.token}` })
        };

        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                ...options,
                headers
            });

            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('token');
                    window.location.href = '/login.html';
                    return;
                }
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getChats() {
        return this.request('/chats');
    }

    async createChat() {
        return this.request('/chats', {
            method: 'POST',
            body: JSON.stringify({})
        });
    }
}

class ChatManager {
    constructor() {
        this.api = new ApiService();
        this.chatsList = document.getElementById('chats-list');
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('new-chat-btn').addEventListener('click', () => this.createNewChat());
        document.getElementById('logout-btn').addEventListener('click', () => this.logout());
    }

    async initialize() {
        if (!localStorage.getItem('token')) {
            window.location.href = '/login.html';
            return;
        }
        try {
            await this.loadChats();
        } catch (error) {
            console.error('Failed to initialize:', error);
            alert('Failed to load chats. Please try again later.');
        }
    }

    async loadChats() {
        const chats = await this.api.getChats();
        this.renderChats(chats);
    }

    renderChats(chats) {
        this.chatsList.innerHTML = '';

        if (!chats.length) {
            this.chatsList.innerHTML = `
                <div class="empty-state">
                    <p>No chats yet. Start a new conversation!</p>
                </div>
            `;
            return;
        }

        chats.forEach(chat => {
            const chatElement = this.createChatElement(chat);
            this.chatsList.appendChild(chatElement);
        });
    }

    createChatElement(chat) {
        const div = document.createElement('div');
        div.className = 'chat-item';
        div.innerHTML = `
            <span class="chat-title">${chat.title || 'New Chat'}</span>
            <span class="chat-date">${new Date(chat.timestamp).toLocaleDateString()}</span>
        `;

        div.addEventListener('click', () => {
            window.location.href = `/chat.html?id=${chat.id}`;
        });

        return div;
    }

    async createNewChat() {
        try {
            const chat = await this.api.createChat();
            window.location.href = `/chat.html?id=${chat.id}`;
        } catch (error) {
            console.error('Failed to create chat:', error);
            alert('Failed to create new chat. Please try again.');
        }
    }

    logout() {
        localStorage.removeItem('token');
        window.location.href = '/login.html';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    const chatManager = new ChatManager();
    await chatManager.initialize();
});
