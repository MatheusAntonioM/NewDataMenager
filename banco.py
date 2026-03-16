import sqlite3
from typing import Iterator, List

from configuracoes import DB_PATH


def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def inicializar_banco() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_arquivo TEXT NOT NULL,
                nome TEXT,
                data_nascimento TEXT,
                cpf TEXT,
                texto_bruto TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )
        conn.commit()


def buscar_registros(db: sqlite3.Connection) -> List[sqlite3.Row]:
    cursor = db.execute("SELECT * FROM documentos ORDER BY id DESC")
    return cursor.fetchall()
