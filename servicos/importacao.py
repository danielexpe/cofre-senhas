"""Importação de registros a partir de JSON (parse, validação e dedup)."""
import json
from dataclasses import dataclass, field

from dados.armazenamento import novo_registro


CAMPOS_CONHECIDOS = {
    "id", "nome", "login", "senha", "url", "observacoes",
    "criado_em", "atualizado_em",
}


class ErroJson(Exception):
    """Erro de leitura/formatação do arquivo JSON de entrada."""


@dataclass
class ResultadoImportacao:
    """Separação dos itens de um lote para importação."""

    total_lidos: int = 0
    importaveis: list = field(default_factory=list)
    duplicados: list = field(default_factory=list)   # [(indice, motivo)]
    repetidos: list = field(default_factory=list)    # [(indice, motivo)]
    invalidos: list = field(default_factory=list)    # [(indice, motivo)]
    campos_extras: set = field(default_factory=set)


def carregar_json(caminho: str) -> list:
    """Lê e normaliza os formatos aceitos (lista pura ou objeto com 'registros')."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        raise ErroJson(f"arquivo não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise ErroJson(f"JSON inválido: {e}")

    if isinstance(dados, list):
        return dados
    if isinstance(dados, dict) and "registros" in dados:
        itens = dados["registros"]
        if not isinstance(itens, list):
            raise ErroJson("a chave 'registros' deve conter uma lista")
        return itens
    raise ErroJson("formato desconhecido: esperada uma lista ou um objeto com 'registros'")


def normalizar(item) -> tuple:
    """Valida um item e devolve (registro, None) ou (None, motivo)."""
    if not isinstance(item, dict):
        return None, "item não é um objeto JSON"

    for campo in ("nome", "login", "senha"):
        if campo not in item:
            return None, f"campo obrigatório ausente: '{campo}'"
        valor = item[campo]
        if not isinstance(valor, str):
            return None, f"campo '{campo}' deve ser texto"
        if not valor.strip():
            return None, f"'{campo}' vazio"

    url = item.get("url", "")
    if url is None:
        url = ""
    elif not isinstance(url, str):
        url = str(url)

    observacoes = item.get("observacoes", "")
    if observacoes is None:
        observacoes = ""
    elif not isinstance(observacoes, str):
        observacoes = str(observacoes)

    registro = novo_registro(
        nome=item["nome"],
        login=item["login"],
        senha=item["senha"],
        url=url,
        observacoes=observacoes,
    )
    return registro, None


def chave_duplicidade(registro: dict) -> str:
    """Chave de duplicidade: 'nome|login' normalizado (case-insensitive, sem pontas)."""
    nome = str(registro.get("nome", "")).strip().casefold()
    login = str(registro.get("login", "")).strip().casefold()
    return f"{nome}|{login}"


def planejar_importacao(existentes: list, itens: list) -> ResultadoImportacao:
    """Separa os itens em importáveis / duplicados / repetidos / inválidos."""
    resultado = ResultadoImportacao(total_lidos=len(itens))
    chaves_existentes = {chave_duplicidade(r) for r in existentes}
    chaves_lote = set()

    for indice, item in enumerate(itens, start=1):
        if isinstance(item, dict):
            resultado.campos_extras |= set(item.keys()) - CAMPOS_CONHECIDOS

        registro, motivo = normalizar(item)
        if registro is None:
            resultado.invalidos.append((indice, motivo))
            continue

        chave = chave_duplicidade(registro)
        if chave in chaves_existentes:
            resultado.duplicados.append((
                indice,
                f'já existe no cofre (nome+login: "{registro["nome"]}" / "{registro["login"]}")',
            ))
            continue
        if chave in chaves_lote:
            resultado.repetidos.append((
                indice,
                f'repetido no próprio arquivo (nome+login: "{registro["nome"]}" / "{registro["login"]}")',
            ))
            continue

        chaves_lote.add(chave)
        resultado.importaveis.append(registro)

    return resultado
