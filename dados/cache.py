"""
Gerencia o cache local de cofres recentes na pasta do usuário.
Armazena APENAS: caminho do arquivo .vault + Secret ID + timestamp.
NUNCA armazena senhas mestras ou conteúdo dos cofres.
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path


CACHE_FILENAME = ".cofre_cache.json"
MAX_RECENTES = 10


def _caminho_cache() -> Path:
    """Retorna o caminho do arquivo de cache na pasta do usuário."""
    return Path.home() / CACHE_FILENAME


def _ocultar_no_windows(caminho: Path):
    """Aplica atributo 'hidden' no Windows (no Linux já fica oculto pelo ponto)."""
    if sys.platform == "win32":
        try:
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(caminho), FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            pass  # falha silenciosa, o arquivo continua funcionando


def carregar_cache() -> list:
    """
    Carrega a lista de cofres recentes.
    Retorna lista vazia se o arquivo não existir ou estiver corrompido.
    Remove automaticamente entradas cujo arquivo .vault não existe mais.
    """
    caminho = _caminho_cache()
    if not caminho.exists():
        return []

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        recentes = dados.get("recentes", [])
    except (json.JSONDecodeError, OSError):
        return []

    # Filtra apenas os que ainda existem no disco
    validos = [r for r in recentes if os.path.isfile(r.get("caminho", ""))]

    # Se houve mudança, regrava o cache limpo
    if len(validos) != len(recentes):
        _gravar(validos)

    return validos


def adicionar_ou_atualizar(caminho_vault: str, secret_id: str):
    """
    Adiciona ou atualiza um cofre no cache.
    Se já existir (mesmo caminho), atualiza o timestamp e move para o topo.
    """
    recentes = carregar_cache()

    # Remove entrada antiga do mesmo caminho (se existir)
    recentes = [r for r in recentes if r.get("caminho") != caminho_vault]

    # Adiciona no topo
    nova_entrada = {
        "caminho": caminho_vault,
        "secret_id": secret_id,
        "ultimo_acesso": datetime.now().isoformat(timespec="seconds"),
    }
    recentes.insert(0, nova_entrada)

    # Limita ao máximo
    recentes = recentes[:MAX_RECENTES]

    _gravar(recentes)


def remover(caminho_vault: str):
    """Remove uma entrada específica do cache."""
    recentes = carregar_cache()
    recentes = [r for r in recentes if r.get("caminho") != caminho_vault]
    _gravar(recentes)


def limpar_tudo():
    """Apaga todo o histórico de cofres recentes."""
    _gravar([])


def _gravar(recentes: list):
    """Grava a lista no arquivo de cache (operação interna)."""
    caminho = _caminho_cache()
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump({"recentes": recentes}, f, indent=2, ensure_ascii=False)
        _ocultar_no_windows(caminho)
    except OSError:
        pass  # se não conseguir gravar, segue sem cache (não crítico)

