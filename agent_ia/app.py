# agent_ia/app.py
# 🏛️ PHOENIX AGENTS IA - Point d'entrée Render
# Smart Router + Security Guardian unifiés

import os
import logging
from fastapi import FastAPI
from smart_router_api import router as smart_router
from security_api import router as security_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Phoenix Agents IA",
    description="Smart Router + Security Guardian unifiés",
    version="1.0.0"
)

# Include routers
app.include_router(smart_router, prefix="/api/smart", tags=["Smart Router"])
app.include_router(security_api, prefix="/api/security", tags=["Security Guardian"])

@app.get("/")
def root():
    return {"message": "🤖 Phoenix Agents IA - Smart Router + Security Guardian"}

@app.get("/health")
def health():
    return {"status": "healthy", "services": ["smart-router", "security-guardian"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)