import sqlite3
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, List
from urllib.error import URLError

import fitz
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from openpyxl import Workbook

from banco import buscar_registros, get_db
from configuracoes import ALLOWED_EXTENSIONS, DB_PATH
from extrator_dados import ExtratorDados
from ocr_utils import executar_ocr, preprocessar_imagem
from renderizacao import (
    escape_html,
    montar_resultado_html,
    montar_tabela_registros,
    renderizar_html,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(db: sqlite3.Connection = Depends(get_db)) -> str:
    tabela = montar_tabela_registros(buscar_registros(db))
    return renderizar_html("", tabela)


@router.post("/processar", response_class=HTMLResponse)
async def processar(
    arquivo: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db),
) -> HTMLResponse:
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo inválido.")

    ext = Path(arquivo.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Envie PNG, JPG, JPEG ou PDF.",
        )

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    try:
        imagens = preprocessar_imagem(conteudo, ext)
    except ValueError as exc:
        resultado = f'<div class="resultado erro">Erro: {escape_html(str(exc))}</div>'
        tabela = montar_tabela_registros(buscar_registros(db))
        return HTMLResponse(renderizar_html(resultado, tabela), status_code=400)
    except fitz.FileDataError as exc:
        resultado = f'<div class="resultado erro">PDF inválido: {escape_html(str(exc))}</div>'
        tabela = montar_tabela_registros(buscar_registros(db))
        return HTMLResponse(renderizar_html(resultado, tabela), status_code=400)

    try:
        texto_bruto = await executar_ocr(imagens)
    except (RuntimeError, ValueError, OSError, URLError) as exc:
        resultado = f'<div class="resultado erro">Falha ao executar OCR: {escape_html(str(exc))}</div>'
        tabela = montar_tabela_registros(buscar_registros(db))
        return HTMLResponse(renderizar_html(resultado, tabela), status_code=500)

    linhas = texto_bruto.splitlines()
    nome = ExtratorDados.extrair_nome(linhas)
    cpf = ExtratorDados.extrair_cpf(texto_bruto)
    data_nasc = ExtratorDados.extrair_data_nascimento(texto_bruto)

    cursor = db.execute(
        """
        INSERT INTO documentos
        (nome_arquivo, nome, data_nascimento, cpf, texto_bruto, criado_em)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            arquivo.filename,
            nome,
            data_nasc,
            cpf,
            texto_bruto,
            datetime.now().isoformat(),
        ),
    )
    db.commit()

    lastrowid = cursor.lastrowid
    if lastrowid is None:
        raise HTTPException(status_code=500, detail="Falha ao obter ID do registro salvo.")

    resultado = montar_resultado_html(
        nome_arquivo=arquivo.filename,
        nome=nome,
        cpf=cpf,
        data_nascimento=data_nasc,
        texto_bruto=texto_bruto,
        registro_id=int(lastrowid),
    )
    tabela = montar_tabela_registros(buscar_registros(db))
    return HTMLResponse(renderizar_html(resultado, tabela))


@router.get("/registros")
def listar_registros(
    db: sqlite3.Connection = Depends(get_db),
) -> List[dict[str, Any]]:
    rows = buscar_registros(db)
    return [dict(row) for row in rows]


@router.get("/exportar-excel")
async def exportar(db: sqlite3.Connection = Depends(get_db)) -> StreamingResponse:
    rows = buscar_registros(db)

    wb = Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet()

    ws.title = "Documentos"
    ws.append(["ID", "Arquivo", "Nome", "Nascimento", "CPF", "Texto OCR", "Data Registro"])

    for r in rows:
        ws.append([
            r["id"],
            r["nome_arquivo"],
            r["nome"],
            r["data_nascimento"],
            r["cpf"],
            r["texto_bruto"],
            r["criado_em"],
        ])

    out = BytesIO()
    wb.save(out)
    out.seek(0)

    return StreamingResponse(
        out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=extracao.xlsx"},
    )


async def http_exception_handler(request: Request, exc: Exception) -> HTMLResponse:
    if isinstance(exc, HTTPException):
        if request.url.path in {"/", "/processar"}:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                tabela = montar_tabela_registros(buscar_registros(conn))
            resultado = f'<div class="resultado erro">Erro: {escape_html(str(exc.detail))}</div>'
            return HTMLResponse(renderizar_html(resultado, tabela), status_code=exc.status_code)

        return HTMLResponse(
            f"Erro: {escape_html(str(exc.detail))}",
            status_code=exc.status_code,
        )

    return HTMLResponse(
        "Erro interno do servidor.",
        status_code=500,
    )
