"""
Módulo de criptografia: PBKDF2 + AES (Fernet) + SHA512 para integridade.

Formato v2 (atual):
  [MAGIC_V2][salt(16)][salt2(32)][payload encriptado Fernet]

O Secret ID nunca é gravado no arquivo. Os 32 bytes de salt2 são públicos e
aleatórios; o Secret ID continua entrando na derivação da chave, mas vem da
interface (cache ou formulário).

Formato v1 (legado, somente leitura):
  [MAGIC_V1][salt(16)][secret_id_hex(32)][payload encriptado Fernet]
"""
import os
import json
import base64
import hashlib
import secrets
import tempfile
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


PBKDF2_ITERATIONS = 200_000
SALT_SIZE = 16
SALT2_SIZE = 32
MAGIC_V1 = b"VAULTv1\x00"
MAGIC_V2 = b"VAULTv2\x00"

_ERRO_INVALIDO = "Arquivo de cofre inválido ou corrompido."
_ERRO_VERSAO = "Este cofre foi criado por uma versão mais nova do aplicativo."
_ERRO_AUTENTICACAO = "Secret ID ou senha mestra incorretos, ou cofre corrompido."


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


def _gravar_atomico(caminho: str, dados: bytes):
    """Grava os dados em um temporário e substitui o destino atomicamente."""
    diretorio = os.path.dirname(os.path.abspath(caminho)) or "."
    fd, temporario = tempfile.mkstemp(prefix=".vault-", suffix=".tmp", dir=diretorio)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(temporario, 0o600)
        except OSError:
            pass
        os.replace(temporario, caminho)
    except BaseException:
        try:
            os.unlink(temporario)
        except OSError:
            pass
        raise


def encriptar_cofre(caminho: str, secret_id: str, senha_mestra: str, registros: list):
    """Salva o cofre no formato v2. O Secret ID não é gravado no arquivo."""
    salt = os.urandom(SALT_SIZE)
    salt2 = os.urandom(SALT2_SIZE)
    chave = derivar_chave(secret_id, senha_mestra, salt + salt2)
    fernet = Fernet(chave)

    payload = {
        "registros": registros,
        "integridade": hash_sha512(json.dumps(registros, sort_keys=True).encode()),
    }
    dados_json = json.dumps(payload).encode("utf-8")
    cifrado = fernet.encrypt(dados_json)

    _gravar_atomico(caminho, MAGIC_V2 + salt + salt2 + cifrado)


def decriptar_cofre(caminho: str, secret_id: str, senha_mestra: str) -> list:
    """
    Abre e decripta um cofre v1 ou v2.
    Retorna a lista de registros ou lança ValueError se falhar.
    """
    with open(caminho, "rb") as f:
        magic = f.read(len(MAGIC_V2))

        if magic == MAGIC_V1:
            salt = f.read(SALT_SIZE)
            sid_legado = f.read(32)
            if len(salt) != SALT_SIZE or len(sid_legado) != 32:
                raise ValueError(_ERRO_INVALIDO)
            salt_kdf = salt
        elif magic == MAGIC_V2:
            salt = f.read(SALT_SIZE)
            salt2 = f.read(SALT2_SIZE)
            if len(salt) != SALT_SIZE or len(salt2) != SALT2_SIZE:
                raise ValueError(_ERRO_INVALIDO)
            salt_kdf = salt + salt2
        elif len(magic) < len(MAGIC_V2):
            raise ValueError(_ERRO_INVALIDO)
        else:
            raise ValueError(_ERRO_VERSAO)

        cifrado = f.read()
        if not cifrado:
            raise ValueError(_ERRO_INVALIDO)

    chave = derivar_chave(secret_id, senha_mestra, salt_kdf)
    fernet = Fernet(chave)

    try:
        dados_json = fernet.decrypt(cifrado)
    except InvalidToken:
        raise ValueError(_ERRO_AUTENTICACAO)

    payload = json.loads(dados_json.decode("utf-8"))
    registros = payload.get("registros", [])

    hash_esperado = payload.get("integridade")
    hash_atual = hash_sha512(json.dumps(registros, sort_keys=True).encode())
    if hash_esperado != hash_atual:
        raise ValueError("Falha na verificação de integridade (SHA512).")

    return registros


def ler_versao_cofre(caminho: str) -> int:
    """Retorna 1 ou 2 conforme o formato do cofre, sem decriptar."""
    with open(caminho, "rb") as f:
        magic = f.read(len(MAGIC_V2))

    if magic == MAGIC_V1:
        return 1
    if magic == MAGIC_V2:
        return 2
    if len(magic) < len(MAGIC_V2):
        raise ValueError(_ERRO_INVALIDO)
    raise ValueError(_ERRO_VERSAO)
