import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.memory import router as memory_router
from app.api.routes.npc import router as npc_router
from app.api.routes.player import router as player_router
from app.api.routes.relationship import router as relationship_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="EchoMind API",
    version="1.0.0",
    description="AI-powered NPC memory system for interactive game worlds",
)

# ------------------------------------
# CORS – allow any local frontend origin
# ------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://echo-mind-delta-six.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app|http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------
# Routers
# ------------------------------------
app.include_router(chat_router)
app.include_router(player_router)
app.include_router(npc_router)
app.include_router(memory_router)
app.include_router(relationship_router)


@app.get("/")
def root():
    return {
        "project": "EchoMind",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}