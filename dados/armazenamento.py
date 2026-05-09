"""
Modelo de registro e operações em memória sobre a lista de registros.
"""
import secrets
from datetime import datetime


def novo_registro(nome: str, login: str, senha: str, url: str = "", observacoes: str = "") -> dict:
    return {
        "id": secrets.token_hex(8),
        "nome": nome,
        "login": login,
        "senha": senha,
        "url": url,
        "observacoes": observacoes,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "atualizado_em": datetime.now().isoformat(timespec="seconds"),
    }


def atualizar_registro(registro: dict, dados: dict) -> dict:
    registro.update(dados)
    registro["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
    return registro


def buscar_registros(registros: list, termo: str) -> list:
    if not termo:
        return registros
    termo = termo.lower()
    return [
        r for r in registros
        if termo in r.get("nome", "").lower()
        or termo in r.get("login", "").lower()
        or termo in r.get("url", "").lower()
    ]

