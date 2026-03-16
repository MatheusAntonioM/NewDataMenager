from fastapi import FastAPI, HTTPException

from banco import inicializar_banco
from configuracoes import APP_TITLE
from rotas import http_exception_handler, router

app = FastAPI(title=APP_TITLE)

app.include_router(router)
app.add_exception_handler(HTTPException, http_exception_handler)


@app.on_event("startup")
def startup_db() -> None:
    inicializar_banco()
