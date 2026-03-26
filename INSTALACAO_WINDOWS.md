# Instalação no Windows — XMLLite (Relatório NFSe)

Passo a passo para rodar o projeto em um PC com Windows 10 ou 11.

---

## Modo rápido (arquivos .bat)

Depois de instalar o **Python** com a opção **Add to PATH** (passo 1 abaixo):

1. Copie ou clone o projeto para uma pasta no Windows (por exemplo `Documentos\XMLLite`).
2. **Duplo clique em `instalar.bat`** — cria a pasta `venv`, atualiza o `pip` e instala o `requirements.txt` (só precisa rodar de novo se mudar dependências).
3. Coloque seus arquivos `.xml` na pasta **`XMLs`** (crie a pasta se não existir).
4. **Duplo clique em `executar.bat`** — abre o painel Streamlit no navegador (`http://localhost:8501`).

Arquivos opcionais:

| Arquivo | Função |
|--------|--------|
| `executar.bat` | Painel web (Streamlit) |
| `gerar_planilha.bat` | Gera `relatorio_nfse.xlsx` com os XML da pasta `XMLs` (sem abrir o navegador) |

**Observação:** `.bat` não é um `.exe`; o Windows executa assim mesmo com duplo clique. Se o antivírus perguntar, confirme que é o seu projeto.

---

## 1. Instalar o Python

1. Acesse [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) e baixe o instalador **Python 3.10 ou mais novo** (recomendado: 3.11 ou 3.12).
2. Execute o instalador.
3. **Marque a opção “Add python.exe to PATH”** (Adicionar Python ao PATH).
4. Clique em **Install Now** e conclua a instalação.

### Conferir se deu certo

Abra o **Prompt de Comando** ou o **PowerShell** e rode:

```text
python --version
```

Deve aparecer algo como `Python 3.12.x`. Se o comando não for encontrado, feche e abra de novo o terminal ou reinstale o Python com a opção do PATH marcada.

---

## 2. Obter o código do projeto

### Opção A — Clonar do GitHub (se tiver Git instalado)

1. Instale o Git: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Abra o PowerShell na pasta onde quer guardar o projeto (por exemplo `Documentos`):

   ```powershell
   cd $env:USERPROFILE\Documents
   git clone https://github.com/GilvanMarques/XMLLite.git
   cd XMLLite
   ```

### Opção B — ZIP do GitHub

1. Abra [https://github.com/GilvanMarques/XMLLite](https://github.com/GilvanMarques/XMLLite)
2. Clique em **Code** → **Download ZIP**
3. Extraia o ZIP para uma pasta, por exemplo `C:\Users\SeuNome\Documents\XMLLite`
4. No PowerShell:

   ```powershell
   cd C:\Users\SeuNome\Documents\XMLLite
   ```
   (ajuste o caminho para onde você extraiu)

---

## 3. Criar ambiente virtual (recomendado)

Na pasta do projeto (onde estão `requirements.txt`, `app_streamlit.py` e `relatorio_nfse.py`):

```powershell
python -m venv venv
```

Ativar o ambiente **nesta janela do terminal**:

```powershell
.\venv\Scripts\Activate.ps1
```

Se aparecer erro de política de execução no PowerShell, use uma vez (como administrador, se necessário):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois tente de novo `.\venv\Scripts\Activate.ps1`.

No **Prompt de Comando (cmd)** a ativação é:

```text
venv\Scripts\activate.bat
```

Quando estiver ativo, o prompt costuma mostrar `(venv)` no início da linha.

---

## 4. Instalar as dependências

Com o `venv` ativado e estando na pasta do projeto:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Isso instala, entre outros, `streamlit`, `pandas` e `openpyxl`.

---

## 5. Colocar os arquivos XML

1. Crie a pasta `XMLs` dentro do projeto (se ainda não existir).
2. Copie para `XMLs` os arquivos `.xml` das NFSe que quiser processar.

O repositório no GitHub não inclui os XMLs (por privacidade); eles ficam só na sua máquina.

---

## 6. Executar o painel web (Streamlit)

Na pasta do projeto, com o `venv` ativado:

```powershell
streamlit run app_streamlit.py
```

O navegador deve abrir em **http://localhost:8501**. Se não abrir, acesse esse endereço manualmente.

- **Pasta no computador:** informe o caminho completo da pasta dos XMLs, por exemplo `C:\Users\SeuNome\Documents\XMLLite\XMLs`, ou use o botão de selecionar pasta (quando disponível no Windows).
- **Enviar arquivos:** você pode enviar um ou vários `.xml` pela interface.

Para parar o servidor, volte ao terminal e pressione **Ctrl+C**.

---

## 7. Gerar a planilha pela linha de comando (opcional)

Com o `venv` ativado:

```powershell
python relatorio_nfse.py
```

Por padrão o script lê os `.xml` da pasta `XMLs` ao lado do script e gera `relatorio_nfse.xlsx` na mesma pasta.

Outras pastas ou nome de saída:

```powershell
python relatorio_nfse.py --pasta "D:\Notas\XML" --saida "D:\Relatorios\notas.xlsx"
```

---

## Resumo rápido (copiar e colar)

Depois de instalar o Python e colocar o projeto em `C:\Projetos\XMLLite` (ajuste o caminho):

```powershell
cd C:\Projetos\XMLLite
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app_streamlit.py
```

---

## Problemas comuns

| Problema | O que fazer |
|----------|-------------|
| `python` não é reconhecido | Reinstale o Python marcando **Add to PATH**, ou use `py` em vez de `python` (`py -m venv venv`, etc.). |
| Erro ao ativar `venv` no PowerShell | Rode `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` e tente de novo, ou use **cmd** com `venv\Scripts\activate.bat`. |
| `pip install` falha | Verifique internet e firewall; tente `python -m pip install -r requirements.txt`. |
| Porta 8501 em uso | `streamlit run app_streamlit.py --server.port 8502` |

---

## Atualizar o projeto depois (se clonou com Git)

```powershell
cd C:\caminho\para\XMLLite
git pull
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
