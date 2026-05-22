from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 — register models with Base.metadata
from app.database import Base, engine
from app.routers import auth, feedback, websites, widget, workspaces

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Qafied API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(websites.router)
app.include_router(feedback.router)
app.include_router(widget.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}
