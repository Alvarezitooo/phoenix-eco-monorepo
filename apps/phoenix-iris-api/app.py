# apps/phoenix-iris-api/app.py
# 🏛️ PHOENIX IRIS API - Point d'entrée Render
# Conforme architecture monorepo microservices

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)