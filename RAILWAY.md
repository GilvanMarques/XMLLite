# Publicar no Railway (XMLLite)

## O que **não** é necessário na versão publicada (nuvem Linux)

| Item | Motivo |
|------|--------|
| `instalar.bat`, `executar.bat`, `gerar_planilha.bat` | São só para Windows local; o Railway **não executa** `.bat`. Podem permanecer no repositório para quem usa PC Windows. |
| `INSTALACAO_WINDOWS.md` | Documentação local; **não** entra no processo de build. Opcional manter no mesmo repo. |
| Seletor de **pasta no disco** (macOS/Windows) no app | No servidor não existe “sua pasta” acessível ao usuário. O app em ambiente Railway usa **apenas envio de arquivos** (upload). |
| `osascript` / Tkinter no fluxo web | Só eram usados para escolher pasta no desktop; na nuvem essa opção fica oculta. |
| Pasta `XMLs` com notas no Git | Continua ignorada pelo `.gitignore` (`XMLs/*.xml`); cada usuário envia os XML pelo navegador. |
| Instalação manual de dependências no Railway | O build instala automaticamente o `requirements.txt`. |

## O que **é** necessário para o deploy

| Item | Função |
|------|--------|
| `app_streamlit.py` | Aplicação web. |
| `relatorio_nfse.py` | Lógica de leitura dos XML e geração do XLSX (importado pelo Streamlit). |
| `requirements.txt` | Dependências Python. |
| `Procfile` | Comando `web:` com porta e host corretos para o Railway. |
| `runtime.txt` (opcional) | Versão do Python para o build (Nixpacks). |

Arquivos auxiliares: `.streamlit/config.toml` (comportamento do servidor Streamlit).

---

## Passo a passo no Railway

1. Crie um projeto em [railway.app](https://railway.app) e **New service** → **Deploy from GitHub** (repositório `XMLLite` ou o seu fork).
2. O Railway detecta **Python** e o **`Procfile`**; o build roda `pip install -r requirements.txt`.
3. Em **Settings → Networking**, gere um **domínio público** (ou use o URL que o Railway mostrar).
4. Variáveis de ambiente **opcionais**:
   - Nada obrigatório. O app detecta Railway por `RAILWAY_ENVIRONMENT` / `RAILWAY_PROJECT_ID` (definidos automaticamente) e mostra só **upload de XML**.
5. Para forçar modo “somente nuvem” em outro provedor, defina: `XMLLITE_CLOUD=1`.

---

## Limitações na nuvem

- **Sem disco persistente** entre reinícios: o que não foi baixado (ex.: XLSX) some se o container reiniciar. Use o botão de download quando precisar guardar o relatório.
- **Volume**: arquivos muito grandes ou muitos XMLs podem estourar memória/timeout do plano gratuito; processe lotes menores se necessário.

---

## Remover arquivos só-Windows do repositório (opcional)

Se quiser um repo “minimalista” só para nuvem, pode apagar os `.bat` e o `INSTALACAO_WINDOWS.md` em um branch ou repositório separado. **Não é obrigatório**: mantê-los não atrapalha o Railway.
