"""Exportação de registros para JSON em texto puro (compatível com o import)."""
import json
import os
import tempfile


CAMPOS_EXPORTADOS = ("nome", "login", "senha", "url", "observacoes")
CAMPOS_OBRIGATORIOS = ("nome", "login", "senha")


def _texto(valor) -> str:
    """Normaliza um valor do cofre para texto (None vira '', demais viram str)."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    return str(valor)


def montar_payload(registros: list) -> dict:
    """Monta o objeto de saída {'registros': [...]} com os 5 campos efetivos."""
    itens = []
    for reg in registros:
        reg = reg if isinstance(reg, dict) else {}
        itens.append({campo: _texto(reg.get(campo, "")) for campo in CAMPOS_EXPORTADOS})
    return {"registros": itens}


def registros_invalidos_para_import(payload: dict) -> list:
    """Lista (indice, motivo) dos registros que o import rejeitaria."""
    invalidos = []
    for indice, reg in enumerate(payload.get("registros", []), start=1):
        for campo in CAMPOS_OBRIGATORIOS:
            if not reg.get(campo, "").strip():
                invalidos.append((indice, f"'{campo}' vazio"))
    return invalidos


def escrever_json_atomico(caminho: str, payload: dict) -> str:
    """Grava o JSON (UTF-8, indent=2) de forma atômica e com permissão 0600."""
    destino = os.path.abspath(os.path.expanduser(caminho))
    diretorio = os.path.dirname(destino) or "."
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=".exportar_", suffix=".tmp", dir=diretorio, text=True
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        try:
            os.chmod(tmp_path, 0o600)
        except OSError:
            pass
        os.replace(tmp_path, destino)
        tmp_path = None
        try:
            os.chmod(destino, 0o600)
        except OSError:
            pass
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    return destino
