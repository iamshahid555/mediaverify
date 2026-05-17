from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analyze import router as analyze_router
from app.db.database import init_db

app = FastAPI(
    title="MediaVerify API",
    description="Backend service for news credibility analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(analyze_router)


@app.get("/")
def root():
    return {"message": "MediaVerify backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
