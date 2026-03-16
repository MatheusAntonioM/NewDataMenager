import re
from datetime import datetime
from typing import List, Optional


class ExtratorDados:
    HEADER_KEYWORDS = {
        "REPUBLICA",
        "REPÚBLICA",
        "BRASIL",
        "IDENTIDADE",
        "ESTADO",
        "MINAS",
        "GERAIS",
        "POLICIA",
        "POLÍCIA",
        "CIVIL",
        "SECRETARIA",
        "INSTITUTO",
        "CPF",
        "NOME",
        "RG",
        "REGISTRO",
        "CARTEIRA",
        "DOC",
        "FILIACAO",
        "FILIAÇÃO",
    }

    @staticmethod
    def limpar_texto(texto: str) -> str:
        return re.sub(r"\s+", " ", texto).strip()

    @staticmethod
    def apenas_digitos(texto: str) -> str:
        return re.sub(r"\D", "", texto)

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        digitos = ExtratorDados.apenas_digitos(cpf)
        if len(digitos) != 11:
            return False
        if digitos == digitos[0] * 11:
            return False

        soma_1 = sum(int(digitos[i]) * (10 - i) for i in range(9))
        resto_1 = (soma_1 * 10) % 11
        digito_1 = 0 if resto_1 == 10 else resto_1
        if digito_1 != int(digitos[9]):
            return False

        soma_2 = sum(int(digitos[i]) * (11 - i) for i in range(10))
        resto_2 = (soma_2 * 10) % 11
        digito_2 = 0 if resto_2 == 10 else resto_2
        return digito_2 == int(digitos[10])

    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        digitos = ExtratorDados.apenas_digitos(cpf)
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"

    @staticmethod
    def extrair_cpf(texto: str) -> Optional[str]:
        texto_normalizado = (
            texto.upper()
            .replace("O", "0")
            .replace("I", "1")
            .replace("L", "1")
            .replace("S", "5")
        )

        candidatos: List[str] = []

        for match in re.finditer(
            r"CPF\s*[:\-]?\s*([0-9./\-\s]{11,20})",
            texto_normalizado,
        ):
            candidatos.append(match.group(1))

        for match in re.finditer(
            r"\b\d{3}[.\-/]\d{3}[.\-/]\d{3}[.\-/]\d{2}\b",
            texto_normalizado,
        ):
            candidatos.append(match.group())

        for match in re.finditer(r"\d{11}", ExtratorDados.apenas_digitos(texto_normalizado)):
            candidatos.append(match.group())

        candidatos_limpos: List[str] = []
        for candidato in candidatos:
            cpf = ExtratorDados.apenas_digitos(candidato)
            if len(cpf) == 11:
                candidatos_limpos.append(cpf)

        for cpf in candidatos_limpos:
            if ExtratorDados.validar_cpf(cpf):
                return ExtratorDados.formatar_cpf(cpf)

        if candidatos_limpos:
            return ExtratorDados.formatar_cpf(candidatos_limpos[0])

        return None

    @staticmethod
    def data_plausivel(data_texto: str) -> bool:
        try:
            data = datetime.strptime(data_texto.replace("-", "/"), "%d/%m/%Y")
        except ValueError:
            return False
        return 1900 <= data.year <= datetime.now().year

    @staticmethod
    def extrair_data_nascimento(texto: str) -> Optional[str]:
        candidatos: List[str] = []

        for match in re.finditer(
            r"(?:NASCIMENTO|DATA\s+DE\s+NASCIMENTO|DN)\s*[:\-]?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            texto,
            flags=re.IGNORECASE,
        ):
            candidatos.append(match.group(1).replace("-", "/"))

        if not candidatos:
            candidatos = [
                item.replace("-", "/")
                for item in re.findall(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b", texto)
            ]

        for candidato in candidatos:
            if ExtratorDados.data_plausivel(candidato):
                return candidato

        return None

    @staticmethod
    def linha_parece_nome(linha: str) -> bool:
        linha_limpa = ExtratorDados.limpar_texto(linha)
        if not linha_limpa:
            return False
        if re.search(r"\d", linha_limpa):
            return False
        palavras = linha_limpa.split()
        if not 2 <= len(palavras) <= 6:
            return False
        return not any(chave in linha_limpa.upper() for chave in ExtratorDados.HEADER_KEYWORDS)

    @staticmethod
    def extrair_nome(linhas: List[str]) -> Optional[str]:
        linhas_limpas = [
            ExtratorDados.limpar_texto(linha)
            for linha in linhas
            if ExtratorDados.limpar_texto(linha)
        ]

        for indice, linha in enumerate(linhas_limpas):
            linha_upper = linha.upper()
            if linha_upper.startswith("NOME"):
                candidato = re.sub(r"^NOME\s*[:\-]?\s*", "", linha, flags=re.IGNORECASE).strip()
                if ExtratorDados.linha_parece_nome(candidato):
                    return candidato.upper()
                if indice + 1 < len(linhas_limpas):
                    proxima = linhas_limpas[indice + 1]
                    if ExtratorDados.linha_parece_nome(proxima):
                        return proxima.upper()

        candidatos = [linha.upper() for linha in linhas_limpas if ExtratorDados.linha_parece_nome(linha)]
        if candidatos:
            candidatos.sort(key=lambda nome: (len(nome.split()), len(nome)), reverse=True)
            return candidatos[0]

        return None
