from __future__ import annotations

import difflib
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st

from src.carregar_mapa import MapaMunicipios, carregar_mapa
from src.exportar_mapa import exportar_figura
from src.normalizar_nomes import normalizar_nome
from src.plotar_mapa import criar_figura_mapa
from src.processar_entrada import extrair_municipios_json_bytes, extrair_municipios_texto


APP_TITULO = "Pintor de Municípios do Ceará"
COR_PADRAO_SELECIONADOS = "#0057A8"
COR_PADRAO_MUNICIPIOS = "#E6E8EB"
COR_PADRAO_CONTORNOS = "#8A8F98"
COR_PADRAO_TEXTO = "#1F2933"

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GEOJSON = BASE_DIR / "data" / "municipios_ceara.geojson"
OUTPUTS_DIR = BASE_DIR / "outputs"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PMCE = ASSETS_DIR / "logo_PMCE.png"
LOGO_CPRAIO = ASSETS_DIR / "logo_CPRAIO.jpg"

KEY_MULTI = "municipios_selecionados"


@st.cache_data(show_spinner=False)
def carregar_mapa_cache(path_str: str) -> MapaMunicipios:
    return carregar_mapa(Path(path_str))


@st.cache_data(show_spinner=False)
def carregar_mapa_upload_cache(geojson_bytes: bytes) -> MapaMunicipios:
    # GeoPandas lê melhor a partir de caminho; usamos um arquivo temporário em /tmp.
    with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as f:
        f.write(geojson_bytes)
        tmp_path = Path(f.name)
    try:
        return carregar_mapa(tmp_path)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def sugerir_municipios(nome_norm: str, universo_norm: list[str], n: int = 3) -> list[str]:
    return difflib.get_close_matches(nome_norm, universo_norm, n=n, cutoff=0.6)


def _init_state() -> None:
    st.session_state.setdefault(KEY_MULTI, [])
    st.session_state.setdefault("exports_key", None)
    st.session_state.setdefault("exports_bytes", None)
    st.session_state.setdefault("nao_encontrados", None)


def _reset_exports_if_needed(key) -> None:
    if st.session_state.get("exports_key") != key:
        st.session_state["exports_key"] = key
        st.session_state["exports_bytes"] = None


def main() -> None:
    page_icon = None
    try:
        if LOGO_CPRAIO.exists():
            page_icon = Image.open(str(LOGO_CPRAIO))
    except Exception:
        page_icon = None

    st.set_page_config(page_title=APP_TITULO, layout="wide", page_icon=page_icon)
    _init_state()

    # Cabeçalho com logos
    h1, h2, h3 = st.columns([1, 4, 1])
    with h1:
        if LOGO_PMCE.exists():
            st.image(str(LOGO_PMCE), use_container_width=True)
    with h2:
        st.title(APP_TITULO)
        st.caption("Selecione municípios, personalize cor e exporte em PNG, SVG e PDF.")
    with h3:
        if LOGO_CPRAIO.exists():
            st.image(str(LOGO_CPRAIO), use_container_width=True)

    # Sidebar (parte 1): fonte de dados
    with st.sidebar:
        st.header("Configurações")
        geojson_upload = st.file_uploader(
            "GeoJSON dos municípios",
            type=["geojson", "json"],
            help="Se não enviar, usa o arquivo padrão do projeto.",
        )

    # Carrega mapa (após escolher a fonte)
    try:
        if geojson_upload is not None:
            mapa = carregar_mapa_upload_cache(geojson_upload.getvalue())
        else:
            mapa = carregar_mapa_cache(str(DEFAULT_GEOJSON))
    except Exception as e:
        st.error(f"Erro ao carregar o GeoJSON: {e}")
        st.stop()

    # Universo (sem duplicatas por normalização)
    base_nomes = (
        mapa.gdf[["__nome__", "__nome_norm__"]]
        .dropna()
        .drop_duplicates("__nome_norm__")
        .copy()
    )
    base_nomes["__nome__"] = base_nomes["__nome__"].astype(str)
    nomes_opcoes = sorted(base_nomes["__nome__"].tolist())
    nome_to_norm = dict(zip(base_nomes["__nome__"].tolist(), base_nomes["__nome_norm__"].tolist()))
    norm_to_nome = dict(zip(base_nomes["__nome_norm__"].tolist(), base_nomes["__nome__"].tolist()))

    # Sanitiza seleção atual caso o GeoJSON seja trocado
    st.session_state[KEY_MULTI] = [n for n in st.session_state[KEY_MULTI] if n in nomes_opcoes]

    # Sidebar (parte 2): seleção + estilo
    with st.sidebar:
        st.divider()
        st.subheader("Seleção")
        st.caption("Digite para buscar e selecione. O mapa atualiza automaticamente.")

        tab_sel, tab_import = st.tabs(["Lista", "Colar/JSON"])

        with tab_sel:
            st.multiselect(
                "Municípios do Ceará",
                options=nomes_opcoes,
                key=KEY_MULTI,
                help="Digite para buscar e selecione múltiplos municípios.",
            )

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                selecionar_todos = st.button("Selecionar todos", use_container_width=True)
            with col_s2:
                selecionar_nenhum = st.button("Selecionar nenhum", use_container_width=True)

        with tab_import:
            municipios_upload = st.file_uploader(
                "JSON de municípios",
                type=["json"],
                help="Aceita vários formatos (ver README).",
            )
            municipios_texto = st.text_area(
                "Colar municípios",
                placeholder="Fortaleza\nCaucaia\nSobral\nJuazeiro do Norte",
                height=120,
            )

            col_i1, col_i2 = st.columns(2)
            with col_i1:
                substituir = st.checkbox("Substituir seleção", value=False)
            with col_i2:
                aplicar_entrada = st.button("Aplicar entrada", use_container_width=True)

        st.divider()
        st.subheader("Estilo")
        cor = st.color_picker("Cor institucional (destaque)", value=COR_PADRAO_SELECIONADOS)
        titulo_mapa = st.text_input("Título (opcional)", value="")
        subtitulo_mapa = st.text_input("Subtítulo (opcional)", value="")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            btn_limpar = st.button("Limpar seleção", use_container_width=True)
        with col_b2:
            preparar_downloads = st.button("Preparar downloads", type="primary", use_container_width=True)

    # Ações do sidebar
    if selecionar_todos:
        st.session_state[KEY_MULTI] = nomes_opcoes
        st.rerun()
    if selecionar_nenhum:
        st.session_state[KEY_MULTI] = []
        st.rerun()

    if btn_limpar:
        st.session_state[KEY_MULTI] = []
        st.session_state["nao_encontrados"] = None
        st.rerun()

    if aplicar_entrada:
        municipios: list[str] = []
        municipios += extrair_municipios_texto(municipios_texto)
        if municipios_upload is not None:
            try:
                municipios += extrair_municipios_json_bytes(municipios_upload.getvalue())
            except Exception as e:
                st.error(f"Erro ao ler JSON de municípios: {e}")
                st.stop()

        municipios = [m for m in (m.strip() for m in municipios) if m]
        pares = [(m, normalizar_nome(m)) for m in municipios]
        pares = [(orig, norm) for (orig, norm) in pares if norm]

        universo = set(mapa.nomes_norm_disponiveis)
        encontrados_norm = {norm for (_, norm) in pares if norm in universo}
        nao_encontrados = [(orig, norm) for (orig, norm) in pares if norm not in universo]

        encontrados_nomes = sorted({norm_to_nome.get(n, n) for n in encontrados_norm})
        if substituir:
            st.session_state[KEY_MULTI] = encontrados_nomes
        else:
            atual = set(st.session_state.get(KEY_MULTI, []))
            st.session_state[KEY_MULTI] = sorted(atual.union(encontrados_nomes))

        if nao_encontrados:
            itens = []
            for orig, norm in nao_encontrados:
                sugestoes_norm = sugerir_municipios(norm, mapa.nomes_norm_disponiveis, n=3)
                sugestoes = [norm_to_nome.get(s, s) for s in sugestoes_norm]
                itens.append({"entrada": orig, "sugestoes": sugestoes})
            st.session_state["nao_encontrados"] = itens
        else:
            st.session_state["nao_encontrados"] = None

        st.rerun()

    selecionados_nomes = st.session_state.get(KEY_MULTI, [])
    selecionados_norm = {nome_to_norm[n] for n in selecionados_nomes if n in nome_to_norm}

    st.caption(
        f"Municípios carregados: {len(mapa.gdf)} | Selecionados: {len(selecionados_norm)} | "
        f"Coluna de nome: `{mapa.coluna_nome}`"
    )

    nao_encontrados = st.session_state.get("nao_encontrados")
    if nao_encontrados:
        st.warning("Municípios não encontrados no GeoJSON.")
        linhas = []
        for item in nao_encontrados:
            entrada = item["entrada"]
            sugestoes = item.get("sugestoes") or []
            if sugestoes:
                linhas.append(f"- {entrada} | Sugestões: {', '.join(sugestoes)}")
            else:
                linhas.append(f"- {entrada}")
        st.text("Lista:\n" + "\n".join(linhas))

    # Mantém exports consistentes com o estado atual
    exports_key = (tuple(sorted(selecionados_norm)), cor, (titulo_mapa or "").strip(), (subtitulo_mapa or "").strip())
    _reset_exports_if_needed(exports_key)

    st.subheader("Mapa")
    try:
        fig = criar_figura_mapa(
            mapa.gdf,
            selecionados_norm=selecionados_norm,
            cor_selecionados=cor,
            titulo=titulo_mapa,
            subtitulo=subtitulo_mapa,
            cor_padrao=COR_PADRAO_MUNICIPIOS,
            cor_contorno=COR_PADRAO_CONTORNOS,
            cor_texto=COR_PADRAO_TEXTO,
        )
    except Exception as e:
        st.error(f"Erro ao gerar o mapa: {e}")
        st.stop()

    st.pyplot(fig, use_container_width=True)

    st.subheader("Downloads")
    with st.expander("Exportar PNG / SVG / PDF", expanded=True):
        salvar_outputs = st.checkbox("Salvar também em outputs/", value=True)
        st.caption(f"Pasta: `{OUTPUTS_DIR}` | PNG com 300 DPI | SVG/PDF vetoriais.")

        if preparar_downloads:
            try:
                st.session_state["exports_bytes"] = exportar_figura(
                    fig,
                    OUTPUTS_DIR,
                    salvar_em_disco=salvar_outputs,
                    dpi_png=300,
                )
            except Exception as e:
                st.error(f"Erro ao exportar o mapa: {e}")
                plt.close(fig)
                st.stop()

        arquivos = st.session_state.get("exports_bytes")
        if not arquivos:
            st.info("Clique em “Preparar downloads” para gerar os arquivos com o estado atual do mapa.")
        else:
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            with col_dl1:
                st.download_button(
                    "Baixar PNG (300 DPI)",
                    data=arquivos["png"],
                    file_name="mapa_ceara_personalizado.png",
                    mime="image/png",
                    use_container_width=True,
                )
            with col_dl2:
                st.download_button(
                    "Baixar SVG",
                    data=arquivos["svg"],
                    file_name="mapa_ceara_personalizado.svg",
                    mime="image/svg+xml",
                    use_container_width=True,
                )
            with col_dl3:
                st.download_button(
                    "Baixar PDF",
                    data=arquivos["pdf"],
                    file_name="mapa_ceara_personalizado.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    plt.close(fig)


if __name__ == "__main__":
    main()
