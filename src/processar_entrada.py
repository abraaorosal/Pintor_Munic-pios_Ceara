from __future__ import annotations

import json
import re
from typing import Any, Iterable


_RE_SPLIT = re.compile(r"[,\n;]+")


def extrair_municipios_texto(texto: str | None) -> list[str]:
    """Extrai municípios digitados manualmente (por linha, vírgula ou ;)."""
    if not texto:
        return []
    partes = [p.strip() for p in _RE_SPLIT.split(texto) if p.strip()]
    return partes


def _as_lista_str(it: Iterable[Any]) -> list[str]:
    return [str(x).strip() for x in it if str(x).strip()]


def extrair_municipios_json_bytes(conteudo: bytes) -> list[str]:
    """Lê bytes de JSON e extrai nomes nos formatos suportados."""
    try:
        obj = json.loads(conteudo.decode("utf-8"))
    except UnicodeDecodeError:
        obj = json.loads(conteudo.decode("latin-1"))

    return extrair_municipios_json_obj(obj)


def extrair_municipios_json_obj(obj: Any) -> list[str]:
    """
    Aceita formatos:
    1) {"municipios": [...]}
    2) {"municipios_pintar": [...]}
    3) ["Fortaleza", ...]
    4) [{"municipio": "Fortaleza"}, ...]
    """
    if isinstance(obj, dict):
        for chave in ("municipios", "municipios_pintar"):
            if chave in obj and isinstance(obj[chave], list):
                return _extrair_de_lista(obj[chave])
        chaves = ", ".join(sorted(obj.keys()))
        raise ValueError(
            "JSON no formato dicionário deve conter uma lista em "
            '"municipios" ou "municipios_pintar". '
            f"Chaves encontradas: {chaves or '(nenhuma)'}"
        )

    if isinstance(obj, list):
        return _extrair_de_lista(obj)

    raise ValueError("JSON inválido: esperado lista ou dicionário.")


def _extrair_de_lista(lista: list[Any]) -> list[str]:
    if not lista:
        return []

    # Formato 3: lista de strings
    if all(isinstance(x, str) for x in lista):
        return _as_lista_str(lista)

    # Formato 4: lista de objetos
    if all(isinstance(x, dict) for x in lista):
        nomes: list[str] = []
        for item in lista:
            for chave in ("municipio", "nome", "name"):
                if chave in item and item[chave] is not None:
                    nomes.append(str(item[chave]).strip())
                    break
        return _as_lista_str(nomes)

    # Lista mista: tolerante (strings + dicts)
    nomes_mistos: list[str] = []
    for item in lista:
        if isinstance(item, str):
            nomes_mistos.append(item)
            continue
        if isinstance(item, dict):
            for chave in ("municipio", "nome", "name"):
                if chave in item and item[chave] is not None:
                    nomes_mistos.append(str(item[chave]))
                    break
    if nomes_mistos:
        return _as_lista_str(nomes_mistos)

    raise ValueError("Não foi possível extrair municípios do JSON enviado.")

