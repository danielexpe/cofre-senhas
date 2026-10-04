#!/usr/bin/env python3
"""
Importação massiva de registros para um cofre .vault existente, a partir de JSON.

Uso:
    python scripts/importar_registros.py [ARQUIVO.json] [-y]

As credenciais (caminho do cofre, Secret ID e senha mestra) são sempre
solicitadas interativamente no terminal; a senha mestra nunca é ecoada.
"""
import argparse
import getpass
import json
import os
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seguranca.encriptacao import decriptar_cofre, encriptar_cofre
from dados.armazenamento import novo_registro


CAMPOS_CONHECIDOS = {
    "id", "nome", "login", "senha", "url", "observacoes",
    "criado_em", "atualizado_em",
}


class ErroJson(Exception):
    """Erro de leitura/formatação do arquivo JSON de entrada."""


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


def fazer_backup(caminho: str, timestamp: str) -> str:
    """Copia o .vault (já cifrado) com timestamp. Retorna o caminho do backup."""
    destino = f"{caminho}.{timestamp}.bak"
    shutil.copy2(caminho, destino)
    return destino


def imprimir_relatorio(caminho_cofre, caminho_json, total_lidos, importaveis,
                       duplicados, repetidos, invalidos, backup, total_cofre,
                       campos_extras):
    print()
    print("=== Importação Massiva — Cofre de Senhas ===")
    print()
    print(f"Cofre ........: {caminho_cofre}")
    print(f"Arquivo JSON .: {caminho_json}")
    print(f"Itens lidos ..: {total_lidos}")
    print()
    print(f"  ✓ Importados ........: {len(importaveis)}")
    print(f"  ↷ Pulados (existente): {len(duplicados)}")
    print(f"  ↷ Pulados (repetido) : {len(repetidos)}")
    print(f"  ✗ Inválidos ..........: {len(invalidos)}")
    print()
    if backup:
        print(f"Backup .......: {backup}")
    print(f"Total no cofre: {total_cofre} registro(s)")

    if campos_extras:
        print()
        print(f"Aviso: campos desconhecidos ignorados: {', '.join(sorted(campos_extras))}")

    nao_importados = (
        [("inválido", i, m) for i, m in invalidos]
        + [("duplicado", i, m) for i, m in duplicados]
        + [("repetido", i, m) for i, m in repetidos]
    )
    if nao_importados:
        print()
        print("--- Itens não importados ---")
        for tipo, indice, motivo in sorted(nao_importados, key=lambda x: x[1]):
            print(f"[{tipo}] #{indice}  motivo: {motivo}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="importar_registros.py",
        description="Importa registros para um cofre .vault a partir de um arquivo JSON.",
    )
    parser.add_argument("arquivo", nargs="?",
                        help="Caminho do JSON de entrada (opcional; se omitido, pergunta).")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Não pede confirmação antes de gravar (assume 'sim').")
    args = parser.parse_args(argv)

    # 1. Caminho do JSON
    caminho_json = args.arquivo
    if not caminho_json:
        caminho_json = input("Arquivo JSON de entrada: ").strip()
    caminho_json = os.path.expanduser(caminho_json)

    # 2. Ler e parsear
    try:
        itens = carregar_json(caminho_json)
    except ErroJson as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 2

    # 3. Credenciais
    print()
    caminho_cofre = os.path.expanduser(input("Caminho do cofre (.vault): ").strip())
    secret_id = input("Secret ID: ").strip()
    senha_mestra = getpass.getpass("Senha Mestra: ")

    # 4. Cofre existe?
    if not os.path.isfile(caminho_cofre):
        print(f"Erro: cofre não encontrado: {caminho_cofre}", file=sys.stderr)
        return 1

    # 5. Decriptar
    try:
        existentes = decriptar_cofre(caminho_cofre, secret_id, senha_mestra)
    except (ValueError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    # 6. Normalizar / validar / separar
    chaves_existentes = {chave_duplicidade(r) for r in existentes}
    chaves_lote = set()
    importaveis = []
    invalidos = []
    duplicados = []
    repetidos = []
    campos_extras = set()

    for indice, item in enumerate(itens, start=1):
        if isinstance(item, dict):
            campos_extras |= set(item.keys()) - CAMPOS_CONHECIDOS

        registro, motivo = normalizar(item)
        if registro is None:
            invalidos.append((indice, motivo))
            continue

        chave = chave_duplicidade(registro)
        if chave in chaves_existentes:
            duplicados.append(
                (indice, f'já existe no cofre (nome+login: "{registro["nome"]}" / "{registro["login"]}")')
            )
            continue
        if chave in chaves_lote:
            repetidos.append(
                (indice, f'repetido no próprio arquivo (nome+login: "{registro["nome"]}" / "{registro["login"]}")')
            )
            continue

        chaves_lote.add(chave)
        importaveis.append(registro)

    total_cofre = len(existentes) + len(importaveis)

    # 7/8. Resumo e confirmação
    if not importaveis:
        imprimir_relatorio(caminho_cofre, caminho_json, len(itens), importaveis,
                           duplicados, repetidos, invalidos, None, total_cofre,
                           campos_extras)
        print()
        print("Nada a importar. Nenhuma alteração foi feita.")
        return 0

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_proposto = f"{caminho_cofre}.{timestamp}.bak"

    print()
    print("Resumo:")
    print(f"  Serão importados : {len(importaveis)}")
    print(f"  Pulados          : {len(duplicados) + len(repetidos)}")
    print(f"  Inválidos        : {len(invalidos)}")
    print(f"  Backup será salvo em: {backup_proposto}")
    print()

    if not args.yes:
        resposta = input("Deseja gravar as alterações no cofre? [s/N]: ").strip().lower()
        if resposta not in ("s", "sim", "y", "yes"):
            print("Operação cancelada. Nenhuma alteração foi feita.")
            return 130

    # 9. Backup
    try:
        backup = fazer_backup(caminho_cofre, timestamp)
    except OSError as e:
        print(f"Erro ao criar backup: {e}", file=sys.stderr)
        return 1

    # 10. Acrescentar e re-encriptar
    try:
        encriptar_cofre(caminho_cofre, secret_id, senha_mestra, existentes + importaveis)
    except OSError as e:
        print(f"Erro ao gravar o cofre: {e}", file=sys.stderr)
        return 1

    # 11. Relatório final
    imprimir_relatorio(caminho_cofre, caminho_json, len(itens), importaveis,
                       duplicados, repetidos, invalidos, backup, total_cofre,
                       campos_extras)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("Operação cancelada pelo usuário. Nenhuma alteração foi feita.")
        sys.exit(130)
