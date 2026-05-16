from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import match, health
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 AI Resume Matcher starting — model: {settings.LLM_MODEL}")
    yield
    print("👋 Shutting down.")

app = FastAPI(title="AI Resume Matcher API", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(health.router, tags=["Health"])
app.include_router(match.router, prefix="/api/v1", tags=["Resume Matching"])
