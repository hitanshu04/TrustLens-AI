from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# We import directly from the router, skipping the config file entirely
from app.routers.analyze import router as analyze_router

app = FastAPI(title="TrustLens Cloud API")

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the Brain
app.include_router(analyze_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "TrustLens Engine Online", "platform": "Render Cloud"}
