from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import geopandas as gpd

from .normalizar_nomes import normalizar_nome


_CANDIDATAS_COLUNAS_NOME = (
    "NM_MUN",
    "NM_MUNICIP",
    "NM_MUNICIPIO",
    "nome",
    "municipio",
    "Município",
    "MUNICIPIO",
    "name",
)


@dataclass(frozen=True)
class MapaMunicipios:
    gdf: gpd.GeoDataFrame
    coluna_nome: str
    nomes_norm_disponiveis: list[str]


def _normalizar_coluna(col: str) -> str:
    # Normaliza mantendo separadores úteis para colunas.
    return normalizar_nome(col).replace(" ", "_")


def identificar_coluna_nome(colunas: Iterable[str]) -> str | None:
    colunas_list = list(colunas)
    if not colunas_list:
        return None

    alvo = {_normalizar_coluna(c) for c in _CANDIDATAS_COLUNAS_NOME}
    for col in colunas_list:
        if _normalizar_coluna(col) in alvo:
            return col
    return None


def carregar_mapa(geojson_path: Path) -> MapaMunicipios:
    if not geojson_path.exists():
        raise FileNotFoundError(f"GeoJSON não encontrado em: {geojson_path}")

    gdf = gpd.read_file(geojson_path)

    if gdf.empty:
        raise ValueError("GeoJSON carregado, mas não há feições (features).")

    if "geometry" not in gdf.columns:
        raise ValueError("GeoJSON inválido: coluna 'geometry' não encontrada.")

    gdf = gdf[gdf.geometry.notna()].copy()
    if gdf.empty:
        raise ValueError("GeoJSON não contém geometrias válidas (todas nulas).")

    # Tenta corrigir geometrias inválidas (quando disponível), preservando o GeoDataFrame.
    try:
        gdf["geometry"] = gdf.geometry.make_valid()
    except Exception:
        pass

    coluna_nome = identificar_coluna_nome(gdf.columns)
    if not coluna_nome:
        cols = ", ".join(map(str, gdf.columns))
        raise ValueError(
            "Não consegui identificar automaticamente a coluna do nome do município. "
            f"Colunas disponíveis: {cols}"
        )

    # Se CRS estiver ausente, GeoJSON normalmente é WGS84; assumimos para evitar plot quebrado.
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)

    gdf["__nome__"] = gdf[coluna_nome].astype(str)
    gdf["__nome_norm__"] = gdf["__nome__"].map(normalizar_nome)
    nomes_norm = sorted({n for n in gdf["__nome_norm__"].tolist() if n})

    return MapaMunicipios(gdf=gdf, coluna_nome=coluna_nome, nomes_norm_disponiveis=nomes_norm)
