from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.analyze import router as analyze_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Scam Detection API",
        description="Real-time API for assessing scam risk of text messages.",
        version="1.0.0",
    )

    # CORS (frontend ke liye)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def home():
        return {
            "status": "ok",
            "message": "Scam Detection API is running 🚀",
            "docs": "/docs"
        }

    app.include_router(analyze_router, prefix="/api/v1")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
