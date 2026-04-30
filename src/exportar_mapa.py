from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt


def exportar_figura(
    fig: plt.Figure,
    outputs_dir: Path,
    basename: str = "mapa_ceara_personalizado",
    salvar_em_disco: bool = True,
    dpi_png: int = 300,
) -> dict[str, bytes]:
    """
    Exporta a figura em PNG (300 DPI), SVG e PDF.
    Também grava os arquivos na pasta outputs/ (útil para histórico/uso externo).
    """
    outputs_dir.mkdir(parents=True, exist_ok=True)

    saidas: dict[str, bytes] = {}

    # PNG (raster)
    buf_png = BytesIO()
    fig.savefig(
        buf_png,
        format="png",
        dpi=dpi_png,
        bbox_inches="tight",
        facecolor="white",
    )
    saidas["png"] = buf_png.getvalue()
    if salvar_em_disco:
        (outputs_dir / f"{basename}.png").write_bytes(saidas["png"])

    # SVG (vetorial)
    buf_svg = BytesIO()
    fig.savefig(
        buf_svg,
        format="svg",
        bbox_inches="tight",
        facecolor="white",
    )
    saidas["svg"] = buf_svg.getvalue()
    if salvar_em_disco:
        (outputs_dir / f"{basename}.svg").write_bytes(saidas["svg"])

    # PDF (vetorial)
    buf_pdf = BytesIO()
    fig.savefig(
        buf_pdf,
        format="pdf",
        bbox_inches="tight",
        facecolor="white",
    )
    saidas["pdf"] = buf_pdf.getvalue()
    if salvar_em_disco:
        (outputs_dir / f"{basename}.pdf").write_bytes(saidas["pdf"])

    return saidas

