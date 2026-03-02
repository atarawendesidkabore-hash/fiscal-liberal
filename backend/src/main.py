from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Suite fiscale 2058-A/B/C pour professions libérales (SELARL/SELAS)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from src.routes import auth, company, exercice, form_2058a, form_2058b, form_2058c, dashboard, export  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(company.router, prefix="/api/companies", tags=["Sociétés"])
app.include_router(exercice.router, prefix="/api/exercices", tags=["Exercices"])
app.include_router(form_2058a.router, prefix="/api/exercices", tags=["Formulaire 2058-A"])
app.include_router(form_2058b.router, prefix="/api/exercices", tags=["Formulaire 2058-B"])
app.include_router(form_2058c.router, prefix="/api/exercices", tags=["Formulaire 2058-C"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Tableau de bord"])
app.include_router(export.router, prefix="/api/exercices", tags=["Export PDF"])


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
