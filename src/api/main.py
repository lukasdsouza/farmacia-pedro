import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import auth, chat, customers, dashboard, orders, products, reports, users

app = FastAPI(
    title="Farmacia Pedro - API",
    description="API do sistema de gestão farmacêutica",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

_ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:3001",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(chat.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(customers.router)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "farmacia-pedro-api"}


@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Rota nao encontrada"})


@app.exception_handler(500)
async def server_error(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor"})
