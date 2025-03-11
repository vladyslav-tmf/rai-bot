from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import Settings
from backend.app.routes import auth, chats, messages, users

settings = Settings()

app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.VERSION, description="RAI Bot API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(chats.router, prefix=settings.API_PREFIX)
app.include_router(messages.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to RAI Bot API",
        "version": settings.VERSION,
        "docs_url": "/docs",
    }
