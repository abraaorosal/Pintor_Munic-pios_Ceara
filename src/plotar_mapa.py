from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt


def criar_figura_mapa(
    gdf,
    selecionados_norm: set[str],
    cor_selecionados: str,
    titulo: str | None = None,
    subtitulo: str | None = None,
    cor_padrao: str = "#E6E8EB",
    cor_contorno: str = "#8A8F98",
    cor_texto: str = "#1F2933",
) -> plt.Figure:
    """
    Renderização estática (Matplotlib) do mapa de municípios.

    Espera que o GeoDataFrame contenha:
    - geometry
    - __nome_norm__
    """
    fig, ax = plt.subplots(figsize=(9, 9))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    if "__nome_norm__" not in gdf.columns:
        raise ValueError("GeoDataFrame precisa ter a coluna '__nome_norm__'.")

    cores = [
        (cor_selecionados if nome_norm in selecionados_norm else cor_padrao)
        for nome_norm in gdf["__nome_norm__"].tolist()
    ]

    gdf.plot(
        ax=ax,
        color=cores,
        edgecolor=cor_contorno,
        linewidth=0.55,
    )

    ax.set_axis_off()
    ax.set_aspect("equal")

    titulo = (titulo or "").strip()
    subtitulo = (subtitulo or "").strip()

    # Reserva espaço no topo para título/subtítulo
    topo = 0.98
    if titulo or subtitulo:
        topo = 0.90
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=topo)

    if titulo:
        fig.suptitle(
            titulo,
            x=0.5,
            y=0.98,
            ha="center",
            va="top",
            fontsize=18,
            fontweight="bold",
            color=cor_texto,
        )

    if subtitulo:
        y = 0.945 if titulo else 0.98
        fig.text(
            0.5,
            y,
            subtitulo,
            ha="center",
            va="top",
            fontsize=12,
            color=cor_texto,
        )

    return fig

