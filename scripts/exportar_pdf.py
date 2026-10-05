#!/usr/bin/env python3
"""
Exportação de um cofre .vault para um relatório PDF pronto para impressão.

Gera um documento A4 com capa, cabeçalho/rodapé numerados e um card por
registro. O PDF pode ser cifrado com uma senha de abertura (AES). As senhas dos
registros são sempre exibidas em texto puro.

Uso:
    python scripts/exportar_pdf.py [SAIDA.pdf] [-f]

O caminho do cofre, a senha mestra e a senha de abertura do PDF são sempre
solicitados interativamente no terminal. O Secret ID é lido do cabeçalho do
próprio .vault. As senhas nunca são ecoadas.
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seguranca.encriptacao import decriptar_cofre, ler_secret_id_do_arquivo
from servicos.exportacao_pdf import gerar_pdf, ordenar_registros


def confirmar_sobrescrita(caminho: str, force: bool) -> bool:
    if force or not os.path.exists(caminho):
        return True
    resposta = input(f"O arquivo {caminho} já existe. Sobrescrever? [s/N]: ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def imprimir_relatorio(caminho_cofre, caminho_pdf, total, cifrado):
    print()
    print("=== Exportação PDF — Cofre de Senhas ===")
    print()
    print(f"Cofre ........: {caminho_cofre}")
    print(f"Arquivo PDF ..: {caminho_pdf}")
    print(f"Registros ....: {total}")
    print(f"Cifrado ......: {'sim (AES)' if cifrado else 'NÃO'}")
    print()
    if cifrado:
        print("⚠️  O PDF contém senhas em TEXTO PURO. A proteção é a senha de abertura.")
        print("    Guarde o arquivo e a senha com cuidado. Não há recuperação da senha.")
    else:
        print("⚠️  ATENÇÃO: PDF SEM CIFRA, contendo senhas em TEXTO PURO.")
        print("    Guarde-o com segurança e apague-o após o uso.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="exportar_pdf.py",
        description="Gera um relatório PDF (A4) com os registros de um cofre .vault.",
    )
    parser.add_argument("saida", nargs="?",
                        help="Caminho do PDF de saída (opcional; se omitido, pergunta).")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Sobrescreve o arquivo de saída sem pedir confirmação.")
    args = parser.parse_args(argv)

    caminho_pdf = args.saida
    if not caminho_pdf:
        caminho_pdf = input("Arquivo PDF de saída: ").strip()
    caminho_pdf = os.path.expanduser(caminho_pdf)
    if not caminho_pdf:
        print("Erro: caminho de saída vazio.", file=sys.stderr)
        return 2

    print()
    caminho_cofre = os.path.expanduser(input("Caminho do cofre (.vault): ").strip())
    if not os.path.isfile(caminho_cofre):
        print(f"Erro: cofre não encontrado: {caminho_cofre}", file=sys.stderr)
        return 1

    try:
        secret_id = ler_secret_id_do_arquivo(caminho_cofre)
    except (ValueError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    senha_mestra = getpass.getpass("Senha Mestra: ")
    try:
        registros = decriptar_cofre(caminho_cofre, secret_id, senha_mestra)
    except (ValueError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    senha_pdf = getpass.getpass("Senha de abertura do PDF (vazio = sem cifra): ")
    cifrado = bool(senha_pdf)

    if not confirmar_sobrescrita(caminho_pdf, args.force):
        print("Operação cancelada. Nenhuma alteração foi feita.")
        return 130

    try:
        destino = gerar_pdf(
            caminho_pdf, ordenar_registros(registros),
            os.path.basename(caminho_cofre), senha_pdf,
        )
    except Exception as e:
        print(f"Erro ao gerar o PDF: {e}", file=sys.stderr)
        return 2

    imprimir_relatorio(caminho_cofre, destino, len(registros), cifrado)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("Operação cancelada pelo usuário. Nenhuma alteração foi feita.")
        sys.exit(130)
