const API_URL = 'http://localhost:8000/api/v1';

class ChatService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.chatId = new URLSearchParams(window.location.search).get('id');

        if (!this.chatId) {
            window.location.href = '/';
            return;
        }
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

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getMessages() {
        return this.request(`/chats/${this.chatId}/messages`);
    }

    async sendMessage(content) {
        return this.request(`/chats/${this.chatId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content })
        });
    }

    async getChat() {
        return this.request(`/chats/${this.chatId}`);
    }
}

class ChatManager {
    constructor() {
        this.chatService = new ChatService();
        this.messagesContainer = document.getElementById('messages-container');
        this.messageForm = document.getElementById('message-form');
        this.messageInput = document.getElementById('message-input');
        this.backButton = document.getElementById('back-btn');
        this.chatTitle = document.getElementById('chat-title');

        this.setupEventListeners();
        this.initialize();
    }

    setupEventListeners() {
        this.messageForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.backButton.addEventListener('click', () => window.location.href = '/');

        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
    }

    async initialize() {
        if (!localStorage.getItem('token')) {
            window.location.href = '/login.html';
            return;
        }

        try {
            const [chat, messages] = await Promise.all([
                this.chatService.getChat(),
                this.chatService.getMessages()
            ]);

            this.chatTitle.textContent = chat.title || 'New Chat';
            this.renderMessages(messages);
        } catch (error) {
            console.error('Failed to initialize chat:', error);
            alert('Failed to load chat. Please try again later.');
        }
    }

    renderMessages(messages) {
        this.messagesContainer.innerHTML = '';

        if (!messages.length) {
            this.messagesContainer.innerHTML = `
                <div class="empty-state">
                    <p>No messages yet. Start a conversation!</p>
                </div>
            `;
            return;
        }

        messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            this.messagesContainer.appendChild(messageElement);
        });

        this.scrollToBottom();
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.role.toLowerCase()}`;
        div.textContent = message.content;
        return div;
    }

    async handleSubmit(e) {
        e.preventDefault();
        const content = this.messageInput.value.trim();

        if (!content) return;

        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        try {
            const userMessage = { role: 'USER', content };
            const userMessageElement = this.createMessageElement(userMessage);
            this.messagesContainer.appendChild(userMessageElement);
            this.scrollToBottom();

            const loadingElement = document.createElement('div');
            loadingElement.className = 'message assistant loading';
            loadingElement.textContent = 'RAI Bot is typing';
            this.messagesContainer.appendChild(loadingElement);
            this.scrollToBottom();

            const response = await this.chatService.sendMessage(content);

            loadingElement.remove();

            userMessageElement.remove();

            response.forEach(message => {
                const messageElement = this.createMessageElement(message);
                this.messagesContainer.appendChild(messageElement);
            });

            this.scrollToBottom();
        } catch (error) {
            console.error('Failed to send message:', error);
            alert('Failed to send message. Please try again.');
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => new ChatManager());
