# RAI Bot

RAI Bot is a ChatGPT clone built with FastAPI, PostgreSQL, and a simple web frontend. It provides a chat interface for interacting with AI using the OpenAI API.

## Features

- User authentication (registration and login)
- Chat history
- Real-time AI responses using OpenAI API
- Simple web interface
- RESTful API with FastAPI
- PostgreSQL database for data persistence
- Docker support

## Prerequisites

- Python 3.12+
- Poetry (for local setup)
- PostgreSQL (for local setup)
- Docker and Docker Compose (for Docker setup)

## Local Development Setup

### Backend Setup

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file in the `backend` directory using `.env.sample` as a template:

3. Apply database migrations:
```bash
cd backend
alembic upgrade head
```

4. Start the backend server:
```bash
uvicorn backend.app.main:app --reload
```

The backend API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Start a local web server (you can use Python's built-in server):
```bash
python -m http.server 3000
```

The frontend will be available at http://localhost:3000

## Docker Setup

1. Create a `.env` file in the `backend` directory (same as in local setup).

2. Build and start the containers:
```bash
docker-compose up --build
```

This will start:
- Frontend at http://localhost:3000
- Backend API at http://localhost:8000
- PostgreSQL database

To stop the containers:
```bash
docker-compose down
```

To remove all data (including database volume):
```bash
docker-compose down -v
```

## API Documentation

Once the backend is running, you can access:
- Swagger UI documentation: http://localhost:8000/api/v1/docs

## Development

- Backend uses FastAPI with async SQLAlchemy for database operations
- Frontend is built with vanilla JavaScript and CSS
- API follows RESTful principles
- Database migrations are handled by Alembic
- Docker setup includes hot-reload for development
