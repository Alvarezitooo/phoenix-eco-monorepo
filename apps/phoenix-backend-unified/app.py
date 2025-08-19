# apps/phoenix-backend-unified/app.py
# 🏛️ PHOENIX BACKEND UNIFIED - Point d'entrée Render
# Conforme architecture monorepo microservices

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)