"""
Painel Streamlit para ler NFSe (ABRASF 1.00/2.02), visualizar e baixar XLSX.
Execute: streamlit run app_streamlit.py
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from relatorio_nfse import (
    COLUNAS,
    TITULOS_PT,
    extrair_linha,
    extrair_linha_de_bytes,
    xlsx_em_bytes,
)

BASE_DIR = Path(__file__).resolve().parent


def _eh_servidor_cloud() -> bool:
    """Railway (e similares): sem disco local nem diálogo de pasta; só upload no navegador."""
    e = os.environ
    if e.get("RAILWAY_ENVIRONMENT") or e.get("RAILWAY_PROJECT_ID"):
        return True
    return e.get("XMLLITE_CLOUD", "").strip().lower() in ("1", "true", "yes")


def _ask_directory_macos() -> str | None:
    """
    Seletor nativo do macOS (AppleScript). Não usa Tkinter no mesmo processo do Streamlit,
    o que evita crash (SIGABRT) comum ao misturar Tk + Streamlit no Mac.
    """
    r = subprocess.run(
        [
            "osascript",
            "-e",
            'POSIX path of (choose folder with prompt "Selecione a pasta com os arquivos XML")',
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode != 0:
        return None
    path = (r.stdout or "").strip()
    if path.endswith("/") and len(path) > 1:
        path = path.rstrip("/")
    return path or None


def _ask_directory_tk_subprocess(initialdir: str) -> str | None:
    """Tkinter em processo filho — mais seguro que abrir Tk na mesma sessão do Streamlit."""
    inicial = initialdir.strip() if initialdir.strip() else str(Path.home())
    if not Path(inicial).is_dir():
        inicial = str(Path.home())
    code = f"""import sys
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    sys.exit(2)
r = tk.Tk()
r.withdraw()
try:
    r.attributes("-topmost", True)
except Exception:
    pass
p = filedialog.askdirectory(initialdir={inicial!r}, title="Selecione a pasta com os XML")
r.destroy()
sys.stdout.write(p or "")
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        return None
    out = proc.stdout.strip()
    return out if out else None


def _ask_directory(initialdir: str) -> str | None:
    """Seletor de pasta: no Mac usa diálogo nativo; nos demais, Tk em subprocesso."""
    if platform.system() == "Darwin":
        return _ask_directory_macos()
    return _ask_directory_tk_subprocess(initialdir)


def _formatar_valor_exibicao(v: object) -> object:
    if isinstance(v, float):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return v


def _emissao_como_date(linha: dict) -> date | None:
    de = linha.get("data_emissao")
    if isinstance(de, datetime):
        return de.date()
    if isinstance(de, date):
        return de
    return None


def _esta_cancelada(linha: dict) -> bool:
    dc = linha.get("data_cancelamento")
    return bool(dc) and isinstance(dc, (datetime, date))


def _valor_bruto_num(linha: dict) -> float:
    v = linha.get("valor_bruto")
    if isinstance(v, bool):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    return 0.0


def _formatar_moeda_br(valor: float) -> str:
    s = f"{valor:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _periodo_emissao_padrao(linhas: list[dict]) -> tuple[date, date]:
    datas = [_emissao_como_date(r) for r in linhas]
    datas = [d for d in datas if d is not None]
    if not datas:
        hoje = date.today()
        return hoje, hoje
    return min(datas), max(datas)


def _linha_para_exibicao(linha: dict) -> dict:
    out: dict = {}
    for k in COLUNAS:
        label = TITULOS_PT[k]
        val = linha.get(k, "")
        if k in ("data_emissao", "data_cancelamento", "competencia"):
            if isinstance(val, datetime):
                out[label] = val.strftime("%d/%m/%Y")
            elif isinstance(val, date):
                out[label] = val.strftime("%d/%m/%Y")
            else:
                out[label] = val if val else ""
        elif k == "valor_bruto":
            out[label] = _formatar_valor_exibicao(val) if val != "" else ""
        else:
            out[label] = val if val != "" else ""
    return out


def main() -> None:
    st.set_page_config(
        page_title="Relatório NFSe",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Relatório NFSe")
    st.caption("Leitura de XML ABRASF 1.00 e 2.02 — emissão, cancelamento, cliente, valor bruto e competência.")

    pasta_padrao = str(BASE_DIR / "XMLs")
    if "caminho_pasta_xml" not in st.session_state:
        st.session_state["caminho_pasta_xml"] = pasta_padrao

    cloud = _eh_servidor_cloud()

    with st.sidebar:
        st.header("Fonte dos XMLs")

        uploaded = None
        modo = "Enviar arquivos"

        if cloud:
            st.info(
                "**Instância na nuvem:** envie um ou vários arquivos `.xml` abaixo. "
                "Não há acesso ao disco do servidor."
            )
            uploaded = st.file_uploader(
                "Arquivos XML",
                type=["xml"],
                accept_multiple_files=True,
            )
        else:
            modo = st.radio(
                "Como carregar?",
                ("Pasta no computador", "Enviar arquivos"),
                help="Use a pasta onde estão os .xml ou envie um ou vários arquivos de uma vez.",
            )

            if modo == "Pasta no computador":
                if st.button(
                    "📁 Selecionar pasta…",
                    use_container_width=True,
                    help="Abre a janela do sistema para escolher a pasta dos XMLs.",
                ):
                    sel = _ask_directory(st.session_state["caminho_pasta_xml"])
                    if sel:
                        st.session_state["caminho_pasta_xml"] = sel

                st.text_input(
                    "Caminho da pasta (ajuste manual se precisar)",
                    key="caminho_pasta_xml",
                    placeholder="/caminho/para/XMLs",
                    help="Atualizado automaticamente ao usar “Selecionar pasta”; você pode colar ou editar aqui.",
                )

            if modo == "Enviar arquivos":
                uploaded = st.file_uploader(
                    "Arquivos XML",
                    type=["xml"],
                    accept_multiple_files=True,
                )

        processar = st.button("Processar", type="primary", use_container_width=True)

    linhas: list[dict] | None = st.session_state.get("linhas_nfse")

    if processar:
        linhas_novas: list[dict] = []
        if modo == "Pasta no computador":
            p = Path(st.session_state["caminho_pasta_xml"].strip()).expanduser().resolve()
            if not p.is_dir():
                st.error(f"Pasta não encontrada: {p}")
            else:
                arquivos = sorted(p.glob("*.xml"))
                if not arquivos:
                    st.warning("Nenhum arquivo .xml nessa pasta.")
                else:
                    with st.spinner(f"Lendo {len(arquivos)} arquivo(s)…"):
                        linhas_novas = [extrair_linha(f) for f in arquivos]
                    st.success(f"{len(linhas_novas)} nota(s) processada(s).")
        else:
            if not uploaded:
                st.warning("Selecione ao menos um arquivo XML.")
            else:
                with st.spinner(f"Lendo {len(uploaded)} arquivo(s)…"):
                    linhas_novas = [
                        extrair_linha_de_bytes(f.name, f.getvalue()) for f in uploaded
                    ]
                st.success(f"{len(linhas_novas)} nota(s) processada(s).")

        if linhas_novas:
            st.session_state["linhas_nfse"] = linhas_novas
            linhas = linhas_novas

    if not linhas:
        if cloud:
            st.info(
                "Envie os arquivos XML na barra lateral e clique em **Processar**."
            )
        else:
            st.info(
                "Escolha uma pasta com XMLs ou envie arquivos na barra lateral e clique em **Processar**."
            )
        return

    st.subheader("Filtros")
    d_ini_pad, d_fim_pad = _periodo_emissao_padrao(linhas)

    f1, f2, f3 = st.columns(3)
    with f1:
        apenas_erro = st.checkbox("Mostrar apenas linhas com erro", value=False)
        filtro_cancelado = st.radio(
            "Cancelado",
            ("Todos", "Sim", "Não"),
            horizontal=True,
            help="Sim: com data de cancelamento. Não: sem cancelamento registrado.",
        )
    with f2:
        filtro_cliente = st.text_input("Filtrar por nome do cliente", "")
    with f3:
        st.caption("Período pela **data de emissão** (inclusive).")
        periodo_raw = st.date_input(
            "Emissão — de / até",
            value=(d_ini_pad, d_fim_pad),
            min_value=date(2000, 1, 1),
            max_value=date(2100, 12, 31),
            format="DD/MM/YYYY",
        )

    if isinstance(periodo_raw, (tuple, list)) and len(periodo_raw) == 2:
        di, df = periodo_raw[0], periodo_raw[1]
    elif isinstance(periodo_raw, date):
        di = df = periodo_raw
    else:
        di, df = d_ini_pad, d_fim_pad
    if di > df:
        di, df = df, di

    filtradas = list(linhas)
    if apenas_erro:
        filtradas = [r for r in filtradas if r.get("erro")]
    if filtro_cliente.strip():
        q = filtro_cliente.strip().lower()
        filtradas = [
            r
            for r in filtradas
            if q in str(r.get("nome_cliente", "")).lower()
        ]
    if filtro_cancelado == "Sim":
        filtradas = [r for r in filtradas if _esta_cancelada(r)]
    elif filtro_cancelado == "Não":
        filtradas = [r for r in filtradas if not _esta_cancelada(r)]

    def _dentro_periodo_emissao(r: dict) -> bool:
        ed = _emissao_como_date(r)
        if ed is None:
            return False
        return di <= ed <= df

    filtradas = [r for r in filtradas if _dentro_periodo_emissao(r)]

    erros_f = sum(1 for r in filtradas if r.get("erro"))
    total_bruto = sum(_valor_bruto_num(r) for r in filtradas)

    st.subheader("Resumo (conforme filtros)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de linhas", len(filtradas))
    c2.metric("Com alerta / erro", erros_f)
    c3.metric("OK", len(filtradas) - erros_f)
    c4.metric("Total bruto", f"R$ {_formatar_moeda_br(total_bruto)}")

    rows = [_linha_para_exibicao(r) for r in filtradas]
    df = pd.DataFrame(rows)

    st.subheader("Dados")
    st.dataframe(df, use_container_width=True, hide_index=True, height=420)

    xlsx_bytes = xlsx_em_bytes(filtradas)
    st.download_button(
        label="Baixar planilha (XLSX) — visão filtrada",
        data=xlsx_bytes,
        file_name="relatorio_nfse.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    with st.expander("Exportar também o conjunto completo (sem filtro de tela)"):
        st.download_button(
            label="Baixar XLSX — todas as notas carregadas",
            data=xlsx_em_bytes(linhas),
            file_name="relatorio_nfse_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
