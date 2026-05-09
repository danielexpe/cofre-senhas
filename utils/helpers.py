"""
Funções auxiliares: gerador de senha, força, clipboard.
"""
import secrets
import string


def gerar_senha_aleatoria(tamanho: int = 16, simbolos: bool = True) -> str:
    alfabeto = string.ascii_letters + string.digits
    if simbolos:
        alfabeto += "!@#$%&*()-_=+[]{}"
    return "".join(secrets.choice(alfabeto) for _ in range(tamanho))


def forca_senha(senha: str) -> tuple:
    """Retorna (nivel, cor, texto)."""
    pontos = 0
    if len(senha) >= 8: pontos += 1
    if len(senha) >= 12: pontos += 1
    if any(c.islower() for c in senha): pontos += 1
    if any(c.isupper() for c in senha): pontos += 1
    if any(c.isdigit() for c in senha): pontos += 1
    if any(not c.isalnum() for c in senha): pontos += 1

    if pontos <= 2:
        return (pontos, "#e74c3c", "Fraca")
    elif pontos <= 4:
        return (pontos, "#f39c12", "Média")
    else:
        return (pontos, "#27ae60", "Forte")


def copiar_clipboard(root, texto: str):
    """Copia para a área de transferência usando o Tk."""
    root.clipboard_clear()
    root.clipboard_append(texto)
    root.update()

