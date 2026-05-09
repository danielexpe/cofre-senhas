"""
Módulo de criptografia: PBKDF2 + AES (Fernet) + SHA512 para integridade.
"""
import os
import json
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


PBKDF2_ITERATIONS = 200_000
SALT_SIZE = 16
MAGIC_HEADER = b"VAULTv1\x00"


def gerar_secret_id() -> str:
    """Gera um Secret ID aleatório de 32 caracteres hexadecimais."""
    return secrets.token_hex(16)


def derivar_chave(secret_id: str, senha_mestra: str, salt: bytes) -> bytes:
    """Deriva uma chave Fernet (32 bytes base64) a partir de Secret ID + Senha Mestra."""
    material = (secret_id + ":" + senha_mestra).encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    chave = kdf.derive(material)
    return base64.urlsafe_b64encode(chave)


def hash_sha512(dados: bytes) -> str:
    """Retorna hash SHA512 hexadecimal dos dados."""
    return hashlib.sha512(dados).hexdigest()


def encriptar_cofre(caminho: str, secret_id: str, senha_mestra: str, registros: list):
    """
    Salva o cofre encriptado.
    Estrutura do arquivo:
      [MAGIC_HEADER][salt(16)][secret_id_hex(32)][payload encriptado Fernet]
    """
    salt = os.urandom(SALT_SIZE)
    chave = derivar_chave(secret_id, senha_mestra, salt)
    fernet = Fernet(chave)

    payload = {
        "registros": registros,
        "integridade": hash_sha512(json.dumps(registros, sort_keys=True).encode()),
    }
    dados_json = json.dumps(payload).encode("utf-8")
    cifrado = fernet.encrypt(dados_json)

    with open(caminho, "wb") as f:
        f.write(MAGIC_HEADER)
        f.write(salt)
        f.write(secret_id.encode("utf-8"))
        f.write(cifrado)


def decriptar_cofre(caminho: str, secret_id: str, senha_mestra: str) -> list:
    """
    Abre e decripta o cofre.
    Retorna a lista de registros ou lança ValueError se falhar.
    """
    with open(caminho, "rb") as f:
        header = f.read(len(MAGIC_HEADER))
        if header != MAGIC_HEADER:
            raise ValueError("Arquivo de cofre inválido ou corrompido.")
        salt = f.read(SALT_SIZE)
        secret_id_arquivo = f.read(32).decode("utf-8")
        cifrado = f.read()

    if secret_id_arquivo != secret_id:
        raise ValueError("Secret ID não corresponde ao do arquivo.")

    chave = derivar_chave(secret_id, senha_mestra, salt)
    fernet = Fernet(chave)

    try:
        dados_json = fernet.decrypt(cifrado)
    except InvalidToken:
        raise ValueError("Senha mestra incorreta ou cofre corrompido.")

    payload = json.loads(dados_json.decode("utf-8"))
    registros = payload.get("registros", [])

    # Verifica integridade SHA512
    hash_esperado = payload.get("integridade")
    hash_atual = hash_sha512(json.dumps(registros, sort_keys=True).encode())
    if hash_esperado != hash_atual:
        raise ValueError("Falha na verificação de integridade (SHA512).")

    return registros


def ler_secret_id_do_arquivo(caminho: str) -> str:
    """Lê apenas o Secret ID do cabeçalho (sem decriptar)."""
    with open(caminho, "rb") as f:
        header = f.read(len(MAGIC_HEADER))
        if header != MAGIC_HEADER:
            raise ValueError("Arquivo de cofre inválido.")
        f.read(SALT_SIZE)
        return f.read(32).decode("utf-8")

