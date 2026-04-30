from __future__ import annotations

import re
from typing import Any

from unidecode import unidecode


_RE_SPACES = re.compile(r"\s+")
_RE_KEEP_BASIC = re.compile(r"[^A-Z0-9 \-_/]")


def normalizar_nome(valor: Any) -> str:
    """
    Normaliza nomes para comparação robusta (municípios, colunas etc.).

    Regras:
    - remove acentos (unidecode);
    - transforma em maiúsculas;
    - remove espaços extras;
    - remove caracteres estranhos, preservando letras/números e alguns separadores.
    """
    if valor is None:
        return ""

    texto = str(valor)
    texto = unidecode(texto)
    texto = texto.upper()
    texto = texto.strip()
    texto = _RE_SPACES.sub(" ", texto)
    texto = _RE_KEEP_BASIC.sub("", texto)
    texto = _RE_SPACES.sub(" ", texto).strip()
    return texto

