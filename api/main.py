
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.interview import router as interview_router
from api.routes.auth import router as auth_router

app = FastAPI(
    title="AI Multi-Agent Interview System",
    description="Multi-Agent AI Technical Interview API",
    version="1.0.0",
)

# Allow the existing React + Vite frontend to call the API.
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

app.include_router(auth_router)
app.include_router(interview_router)


@app.get("/")
def root():
    return {
        "message": "AI Multi-Agent Interview System API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
