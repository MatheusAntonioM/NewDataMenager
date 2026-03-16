import html
import sqlite3
from typing import List, Optional

from configuracoes import HTML_PAGE


def renderizar_html(resultado: str, tabela: str) -> str:
    return HTML_PAGE.replace("__RESULTADO__", resultado).replace("__TABELA__", tabela)


def escape_html(valor: Optional[str]) -> str:
    return html.escape(valor or "")


def montar_tabela_registros(rows: List[sqlite3.Row]) -> str:
    if not rows:
        return '<p class="muted">Nenhum registro salvo ainda.</p>'

    linhas_html = []
    for row in rows:
        linhas_html.append(
            "<tr>"
            f"<td>{row['id']}</td>"
            f"<td>{escape_html(row['nome_arquivo'])}</td>"
            f"<td>{escape_html(row['nome'])}</td>"
            f"<td>{escape_html(row['data_nascimento'])}</td>"
            f"<td>{escape_html(row['cpf'])}</td>"
            f"<td>{escape_html(row['criado_em'])}</td>"
            "</tr>"
        )

    return (
        "<h2>Registros salvos</h2>"
        "<table>"
        "<thead><tr><th>ID</th><th>Arquivo</th><th>Nome</th><th>Data de nascimento</th><th>CPF</th><th>Criado em</th></tr></thead>"
        f"<tbody>{''.join(linhas_html)}</tbody>"
        "</table>"
    )


def montar_resultado_html(
    nome_arquivo: str,
    nome: Optional[str],
    cpf: Optional[str],
    data_nascimento: Optional[str],
    texto_bruto: str,
    registro_id: int,
) -> str:
    texto_ocr_html = escape_html(texto_bruto).replace("\n", "<br>")
    return f"""
    <div class="resultado sucesso">
        <h2>Resultado da extração</h2>
        <div class="grade">
            <div class="card"><strong>ID salvo:</strong><br>{registro_id}</div>
            <div class="card"><strong>Arquivo:</strong><br>{escape_html(nome_arquivo)}</div>
            <div class="card"><strong>Nome:</strong><br>{escape_html(nome) or 'Não identificado'}</div>
            <div class="card"><strong>CPF:</strong><br>{escape_html(cpf) or 'Não identificado'}</div>
            <div class="card"><strong>Data de nascimento:</strong><br>{escape_html(data_nascimento) or 'Não identificada'}</div>
        </div>
        <div class="texto-ocr"><strong>Texto OCR:</strong><br>{texto_ocr_html or 'Nenhum texto detectado.'}</div>
    </div>
    """
