"""Utilitários de arquivo (backup do cofre)."""
import shutil
from datetime import datetime


def fazer_backup(caminho: str, timestamp: str = None) -> str:
    """Copia o `.vault` (já cifrado) com timestamp. Retorna o caminho do backup."""
    ts = timestamp or datetime.now().strftime("%Y-%m-%d_%H%M%S")
    destino = f"{caminho}.{ts}.bak"
    shutil.copy2(caminho, destino)
    return destino
