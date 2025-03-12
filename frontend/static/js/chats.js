const API_URL = 'http://localhost:8000/api/v1';

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
            console.log('Making request:', {
                url: `${API_URL}${endpoint}`,
                method: options.method || 'GET',
                headers,
                body: options.body
            });

            const response = await fetch(`${API_URL}${endpoint}`, {
                ...options,
                headers
            });

            const data = await response.json();
            console.log('Response:', data);

            if (!response.ok) {
                const errorMessage = typeof data === 'object'
                    ? JSON.stringify(data, null, 2)
                    : data.detail || `HTTP error! status: ${response.status}`;
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error.message);
            throw error;
        }
    }

    async getChats() {
        return this.request('/chats');
    }

    async createChat(title) {
        return this.request('/chats', {
            method: 'POST',
            body: JSON.stringify({
                title
            })
        });
    }
}

class ChatManager {
    constructor() {
        this.api = new ApiService();
        this.chatsList = document.getElementById('chats-list');
        this.modal = document.getElementById('new-chat-modal');
        this.newChatForm = document.getElementById('new-chat-form');
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('new-chat-btn').addEventListener('click', () => this.showModal());
        document.getElementById('cancel-chat-btn').addEventListener('click', () => this.hideModal());
        document.getElementById('logout-btn').addEventListener('click', () => this.logout());

        this.newChatForm.addEventListener('submit', (e) => this.handleNewChat(e));

        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });
    }

    showModal() {
        this.modal.classList.add('active');
        document.getElementById('chat-title').focus();
    }

    hideModal() {
        this.modal.classList.remove('active');
        this.newChatForm.reset();
    }

    async handleNewChat(e) {
        e.preventDefault();
        const titleInput = document.getElementById('chat-title');
        const title = titleInput.value.trim();

        if (!title) return;

        try {
            const chat = await this.api.createChat(title);
            this.hideModal();
            window.location.href = `/chat.html?id=${chat.id}`;
        } catch (error) {
            console.error('Failed to create chat:', error);
            const errorMessage = error.message.includes('validation error')
                ? 'Failed to create chat: Invalid chat title'
                : 'Failed to create chat. Please try again.';
            alert(errorMessage);
        }
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
            <span class="chat-title">${chat.title}</span>
        `;

        div.addEventListener('click', () => {
            window.location.href = `/chat.html?id=${chat.id}`;
        });

        return div;
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
