APP_TITLE = "Leitor de RG Pro"
DB_PATH = "documentos.db"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
OCR_CONFIDENCE_MINIMA = 0.35

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leitor de RG Pro</title>
    <style>
        * {
            box-sizing: border-box;
        }

        :root {
            --cor-primaria: #2563eb;
            --cor-primaria-escura: #1d4ed8;
            --cor-secundaria: #0f172a;
            --cor-fundo: linear-gradient(135deg, #eef4ff 0%, #f8fafc 45%, #ecfeff 100%);
            --cor-card: rgba(255, 255, 255, 0.92);
            --cor-borda: #dbeafe;
            --cor-texto: #0f172a;
            --cor-texto-suave: #475569;
            --cor-sucesso: #166534;
            --cor-erro: #b91c1c;
            --sombra-principal: 0 20px 45px rgba(15, 23, 42, 0.12);
            --sombra-suave: 0 10px 25px rgba(37, 99, 235, 0.10);
            --raio-grande: 22px;
            --raio-medio: 16px;
            --raio-pequeno: 12px;
        }

        body {
            font-family: "Segoe UI", Arial, sans-serif;
            background: var(--cor-fundo);
            color: var(--cor-texto);
            margin: 0;
            padding: 32px 18px;
            min-height: 100vh;
        }

        .container {
            max-width: 1180px;
            margin: 0 auto;
            background: var(--cor-card);
            backdrop-filter: blur(10px);
            padding: 32px;
            border-radius: var(--raio-grande);
            box-shadow: var(--sombra-principal);
            border: 1px solid rgba(219, 234, 254, 0.9);
        }

        .topo {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 24px;
            flex-wrap: wrap;
            margin-bottom: 28px;
            padding-bottom: 22px;
            border-bottom: 1px solid #e5e7eb;
        }

        .marca h1 {
            margin: 0 0 10px;
            font-size: 2.2rem;
            color: var(--cor-secundaria);
            letter-spacing: -0.03em;
        }

        .marca p {
            margin: 0;
            color: var(--cor-texto-suave);
            font-size: 1rem;
            max-width: 680px;
            line-height: 1.6;
        }

        .selo {
            background: linear-gradient(135deg, #dbeafe, #eff6ff);
            color: var(--cor-primaria-escura);
            border: 1px solid #bfdbfe;
            padding: 12px 16px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.95rem;
            white-space: nowrap;
            box-shadow: var(--sombra-suave);
        }

        .painel-upload {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(14, 165, 233, 0.08));
            border: 1px solid #cfe1ff;
            border-radius: var(--raio-grande);
            padding: 28px;
            margin-bottom: 24px;
        }

        .painel-upload h2 {
            margin: 0 0 10px;
            font-size: 1.35rem;
            color: var(--cor-secundaria);
        }

        .painel-upload p {
            margin: 0 0 18px;
            color: var(--cor-texto-suave);
            line-height: 1.6;
        }

        form {
            margin: 0;
        }

        .linha-form {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            align-items: center;
        }

        input[type=file] {
            flex: 1;
            min-width: 260px;
            padding: 14px;
            border: 1px dashed #93c5fd;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.95);
            color: var(--cor-texto-suave);
        }

        button, .btn {
            background: linear-gradient(135deg, var(--cor-primaria), var(--cor-primaria-escura));
            color: white;
            border: none;
            padding: 12px 18px;
            border-radius: 12px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.20);
        }

        button:hover, .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 24px rgba(37, 99, 235, 0.26);
            opacity: 0.98;
        }

        .acoes {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        .btn-secundario {
            background: white;
            color: var(--cor-primaria-escura);
            border: 1px solid #bfdbfe;
            box-shadow: none;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin: 26px 0;
        }

        .info-card {
            background: #ffffff;
            border: 1px solid #e5eefc;
            border-radius: var(--raio-medio);
            padding: 18px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
        }

        .info-card strong {
            display: block;
            margin-bottom: 6px;
            color: var(--cor-secundaria);
            font-size: 0.98rem;
        }

        .info-card span {
            color: var(--cor-texto-suave);
            line-height: 1.5;
            font-size: 0.95rem;
        }

        .resultado {
            margin-top: 24px;
            padding: 22px;
            background: #f8fbff;
            border-radius: var(--raio-medio);
            border: 1px solid #dbeafe;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
        }

        .resultado h2 {
            margin-top: 0;
            margin-bottom: 14px;
            color: var(--cor-secundaria);
        }

        .erro {
            color: var(--cor-erro);
            font-weight: 700;
            background: #fef2f2;
            border-color: #fecaca;
        }

        .sucesso {
            color: var(--cor-sucesso);
        }

        .grade {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-top: 14px;
        }

        .card {
            border: 1px solid #dbeafe;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border-radius: 14px;
            padding: 14px;
            color: #111827;
            box-shadow: 0 8px 18px rgba(37, 99, 235, 0.05);
        }

        .texto-ocr {
            margin-top: 16px;
            padding: 16px;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            color: #111827;
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.6;
            max-height: 360px;
            overflow: auto;
        }

        .secao-tabela {
            margin-top: 30px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: var(--raio-grande);
            padding: 22px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
            overflow-x: auto;
        }

        .secao-tabela h2 {
            margin-top: 0;
            color: var(--cor-secundaria);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            overflow: hidden;
            border-radius: 14px;
        }

        th, td {
            border-bottom: 1px solid #e5e7eb;
            padding: 12px 14px;
            text-align: left;
            vertical-align: top;
            font-size: 0.95rem;
        }

        th {
            background: #eff6ff;
            color: #1e3a8a;
            font-weight: 700;
        }

        tr:hover td {
            background: #f8fbff;
        }

        .muted {
            color: #64748b;
        }

        .rodape {
            margin-top: 26px;
            text-align: center;
            color: #64748b;
            font-size: 0.92rem;
        }

        @media (max-width: 768px) {
            body {
                padding: 18px 10px;
            }

            .container {
                padding: 20px;
                border-radius: 18px;
            }

            .marca h1 {
                font-size: 1.8rem;
            }

            .painel-upload,
            .resultado,
            .secao-tabela {
                padding: 18px;
            }

            .linha-form {
                flex-direction: column;
                align-items: stretch;
            }

            button, .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="topo">
            <div class="marca">
                <h1>Leitor de RG Pro</h1>
                <p>Extraia com praticidade informações principais de documentos de identidade, visualize os registros salvos e exporte os dados em Excel de forma organizada.</p>
            </div>
            <div class="selo">OCR + FastAPI</div>
        </div>

        <div class="painel-upload">
            <h2>Enviar documento</h2>
            <p>Selecione um arquivo nos formatos PNG, JPG, JPEG ou PDF para identificar nome, CPF e data de nascimento automaticamente.</p>

            <form action="/processar" method="post" enctype="multipart/form-data">
                <div class="linha-form">
                    <input type="file" name="arquivo" accept=".png,.jpg,.jpeg,.pdf" required>
                    <button type="submit">Processar documento</button>
                </div>
            </form>

            <div class="acoes">
                <a class="btn btn-secundario" href="/exportar-excel">Exportar Excel</a>
            </div>
        </div>

        <div class="info-grid">
            <div class="info-card">
                <strong>Formatos aceitos</strong>
                <span>PNG, JPG, JPEG e PDF com leitura otimizada para documentos.</span>
            </div>
            <div class="info-card">
                <strong>Extração automática</strong>
                <span>Busca nome, CPF, data de nascimento e texto OCR para auditoria.</span>
            </div>
            <div class="info-card">
                <strong>Histórico salvo</strong>
                <span>Todos os processamentos ficam armazenados localmente no banco SQLite.</span>
            </div>
        </div>

        __RESULTADO__

        <div class="secao-tabela">
            __TABELA__
        </div>

        <div class="rodape">
            Leitor de RG Pro • Painel de extração e consulta de documentos
        </div>
    </div>
</body>
</html>
"""
