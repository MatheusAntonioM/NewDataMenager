import asyncio
from typing import Any, List, Optional

import cv2  # pylint: disable=no-member
import easyocr
import fitz
import numpy as np

from configuracoes import OCR_CONFIDENCE_MINIMA


class OCRManager:
    """Gerencia a instância do EasyOCR para evitar recarregamento constante."""

    _reader: Optional[easyocr.Reader] = None

    @classmethod
    def get_reader(cls) -> easyocr.Reader:
        if cls._reader is None:
            cls._reader = easyocr.Reader(["pt"], gpu=False)
        return cls._reader


# pylint: disable=no-member
def preprocessar_imagem(image_bytes: bytes, extension: str) -> List[np.ndarray]:
    if extension == ".pdf":
        doc = fitz.open(stream=image_bytes, filetype="pdf")
        try:
            if doc.page_count == 0:
                raise ValueError("PDF sem páginas")
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, 3))
        finally:
            doc.close()
    else:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Falha ao decodificar a imagem")
        img_array = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    variantes: List[np.ndarray] = [img_array]
    img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    variantes.append(img_gray)
    variantes.append(cv2.equalizeHist(img_gray))
    variantes.append(
        cv2.adaptiveThreshold(
            img_gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15,
        )
    )

    imagens_unicas: List[np.ndarray] = []
    assinaturas: set[bytes] = set()
    for variante in variantes:
        assinatura = variante.tobytes()
        if assinatura not in assinaturas:
            assinaturas.add(assinatura)
            imagens_unicas.append(variante)

    return imagens_unicas


async def executar_ocr(images_np: List[np.ndarray]) -> str:
    """Executa o OCR em thread separada para não bloquear o event loop."""
    loop = asyncio.get_running_loop()
    reader = OCRManager.get_reader()

    resultados_totais: List[Any] = []
    for image_np in images_np:
        resultados = await loop.run_in_executor(None, reader.readtext, image_np)
        resultados_totais.extend(resultados)

    textos: List[str] = []
    vistos: set[str] = set()

    for res in resultados_totais:
        if not isinstance(res, (list, tuple)) or len(res) < 2:
            continue
        texto = str(res[1]).strip()
        if not texto:
            continue
        confianca = float(res[2]) if len(res) > 2 and isinstance(res[2], (int, float)) else 1.0
        if confianca < OCR_CONFIDENCE_MINIMA:
            continue
        chave = texto.upper()
        if chave in vistos:
            continue
        vistos.add(chave)
        textos.append(texto)

    if not textos:
        for res in resultados_totais:
            if not isinstance(res, (list, tuple)) or len(res) < 2:
                continue
            texto = str(res[1]).strip()
            if not texto:
                continue
            chave = texto.upper()
            if chave in vistos:
                continue
            vistos.add(chave)
            textos.append(texto)

    return "\n".join(textos)
