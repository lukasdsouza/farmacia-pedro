"""
Inicia o servidor FastAPI (API REST + autenticação).

Uso:
    python scripts/api_server.py
    # ou com variáveis:
    PORT=8080 RELOAD=1 python scripts/api_server.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    reload = os.getenv("RELOAD", "0") in ("1", "true", "yes")
    host = os.getenv("HOST", "0.0.0.0")

    print(f"API iniciando em http://{host}:{port}")
    print(f"Docs: http://localhost:{port}/api/docs")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
