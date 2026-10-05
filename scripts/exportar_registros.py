#!/usr/bin/env python3
"""
Exportação de registros de um cofre .vault para um arquivo JSON em texto puro.

O JSON gerado é 100% compatível com scripts/importar_registros.py (Formato B:
{"registros": [...]}), permitindo round-trip (reimportar em outro cofre).

Uso:
    python scripts/exportar_registros.py [SAIDA.json] [-f]

O caminho do cofre e a senha mestra são sempre solicitados interativamente no
terminal; o Secret ID é lido do cabeçalho do próprio .vault. A senha mestra
nunca é ecoada.
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seguranca.encriptacao import decriptar_cofre, ler_secret_id_do_arquivo
from servicos.exportacao_json import (
    escrever_json_atomico,
    montar_payload,
    registros_invalidos_para_import,
)


def confirmar_sobrescrita(caminho: str, force: bool) -> bool:
    """True se pode gravar. Se o arquivo existir e não houver --force, pergunta."""
    if force or not os.path.exists(caminho):
        return True
    resposta = input(f"O arquivo {caminho} já existe. Sobrescrever? [s/N]: ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def imprimir_relatorio(caminho_cofre, caminho_json, total, exportados, invalidos):
    print()
    print("=== Exportação — Cofre de Senhas ===")
    print()
    print(f"Cofre ........: {caminho_cofre}")
    print(f"Arquivo JSON .: {caminho_json}")
    print(f"Registros ....: {total}")
    print(f"Exportados ...: {exportados}")
    print()
    print("⚠️  ATENÇÃO: o arquivo contém senhas em TEXTO PURO.")
    print("    Guarde-o com segurança e apague-o após o uso.")

    if invalidos:
        print()
        print("--- Avisos de round-trip (não serão reimportados) ---")
        for indice, motivo in invalidos:
            print(f"[inválido] #{indice}  motivo: {motivo}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="exportar_registros.py",
        description="Exporta os registros de um cofre .vault para um JSON em texto puro.",
    )
    parser.add_argument("saida", nargs="?",
                        help="Caminho do JSON de saída (opcional; se omitido, pergunta).")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Sobrescreve o arquivo de saída sem pedir confirmação.")
    args = parser.parse_args(argv)

    # 1. Caminho do JSON de saída
    caminho_json = args.saida
    if not caminho_json:
        caminho_json = input("Arquivo JSON de saída: ").strip()
    caminho_json = os.path.expanduser(caminho_json)
    if not caminho_json:
        print("Erro: caminho de saída vazio.", file=sys.stderr)
        return 2

    # 2. Caminho do cofre
    print()
    caminho_cofre = os.path.expanduser(input("Caminho do cofre (.vault): ").strip())

    # 3. Cofre existe?
    if not os.path.isfile(caminho_cofre):
        print(f"Erro: cofre não encontrado: {caminho_cofre}", file=sys.stderr)
        return 1

    # 4. Secret ID lido do cabeçalho
    try:
        secret_id = ler_secret_id_do_arquivo(caminho_cofre)
    except (ValueError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    # 5. Senha mestra
    senha_mestra = getpass.getpass("Senha Mestra: ")

    # 6. Decriptar
    try:
        registros = decriptar_cofre(caminho_cofre, secret_id, senha_mestra)
    except (ValueError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    # 7. Montar payload e avisos de round-trip
    payload = montar_payload(registros)
    invalidos = registros_invalidos_para_import(payload)

    # 8. Confirmação de sobrescrita
    if not confirmar_sobrescrita(caminho_json, args.force):
        print("Operação cancelada. Nenhuma alteração foi feita.")
        return 130

    # 9. Gravar
    try:
        destino = escrever_json_atomico(caminho_json, payload)
    except OSError as e:
        print(f"Erro ao gravar o JSON de saída: {e}", file=sys.stderr)
        return 2

    # 10. Relatório final
    imprimir_relatorio(caminho_cofre, destino, len(registros), len(payload["registros"]), invalidos)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("Operação cancelada pelo usuário. Nenhuma alteração foi feita.")
        sys.exit(130)
