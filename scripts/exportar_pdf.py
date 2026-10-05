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
import re
import sys
import tempfile
import unicodedata
from datetime import datetime
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seguranca.encriptacao import decriptar_cofre, ler_secret_id_do_arquivo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.pdfencrypt import StandardEncryption
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTES_DIR = os.path.join(ASSETS_DIR, "fonts")
ICONE = os.path.join(ASSETS_DIR, "icone.png")

TITULO_RELATORIO = "Relatório de Credenciais"
MARGEM = 18 * mm
LARGURA_UTIL = A4[0] - 2 * MARGEM

# Paleta (mesma linguagem visual do app)
AZUL = "#2b6cb0"
VERDE = "#16a085"
TEXTO = "#1f2937"
CINZA = "#6b7280"
CARD_BG = "#f3f4f6"
BORDA = "#d1d5db"

FONTE = "Helvetica"
FONTE_BOLD = "Helvetica-Bold"
FONTE_MONO = "Courier"

# Removemos emoji/pictogramas que a fonte embutida não renderiza.
_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"  # pictogramas, emoji, bandeiras
    "\U0000FE00-\U0000FE0F"  # seletores de variação
    "\U0000200D"             # zero-width joiner
    "\U000E0020-\U000E007F"  # tag chars
    "]+",
    flags=re.UNICODE,
)


def registrar_fontes():
    """Registra as fontes DejaVu embutidas; cai para as padrão se ausentes."""
    global FONTE, FONTE_BOLD, FONTE_MONO
    sans = os.path.join(FONTES_DIR, "DejaVuSans.ttf")
    bold = os.path.join(FONTES_DIR, "DejaVuSans-Bold.ttf")
    mono = os.path.join(FONTES_DIR, "DejaVuSansMono.ttf")
    if all(os.path.isfile(p) for p in (sans, bold, mono)):
        pdfmetrics.registerFont(TTFont("DejaVu", sans))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))
        pdfmetrics.registerFont(TTFont("DejaVu-Mono", mono))
        pdfmetrics.registerFontFamily(
            "DejaVu", normal="DejaVu", bold="DejaVu-Bold",
            italic="DejaVu", boldItalic="DejaVu-Bold",
        )
        FONTE, FONTE_BOLD, FONTE_MONO = "DejaVu", "DejaVu-Bold", "DejaVu-Mono"


def limpar_texto(valor) -> str:
    """Normaliza para texto e remove emojis (sem alterar espaços)."""
    if valor is None:
        return ""
    texto = valor if isinstance(valor, str) else str(valor)
    return _EMOJI_RE.sub("", texto)


def _chave_ordenacao(registro: dict) -> str:
    nome = limpar_texto((registro or {}).get("nome", "")).strip()
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", nome) if not unicodedata.combining(c)
    )
    return sem_acento.casefold()


def ordenar_registros(registros: list) -> list:
    return sorted(registros, key=_chave_ordenacao)


def _campo(registro, campo, preservar_espacos=False) -> str:
    """Devolve o valor pronto para o Paragraph (ou '—' se vazio).

    Com preservar_espacos=True, espaços viram '&nbsp;' para não serem
    colapsados pelo ReportLab (necessário para exibir senhas fielmente).
    """
    texto = limpar_texto(registro.get(campo, ""))
    if not texto.strip():
        return "—"
    texto = escape(texto).replace("\n", "<br/>")
    if preservar_espacos:
        texto = texto.replace(" ", "&nbsp;")
    return texto


def _estilos():
    return {
        "titulo": ParagraphStyle(
            "titulo", fontName=FONTE_BOLD, fontSize=26, leading=32,
            textColor=colors.HexColor(AZUL), alignment=TA_CENTER,
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", fontName=FONTE, fontSize=12, leading=18,
            textColor=colors.HexColor(CINZA), alignment=TA_CENTER,
        ),
        "info": ParagraphStyle(
            "info", fontName=FONTE, fontSize=11, leading=17,
            textColor=colors.HexColor(TEXTO), alignment=TA_CENTER,
        ),
        "aviso": ParagraphStyle(
            "aviso", fontName=FONTE, fontSize=9, leading=14,
            textColor=colors.HexColor(CINZA), alignment=TA_CENTER,
        ),
        "card": ParagraphStyle(
            "card", fontName=FONTE, fontSize=9.5, leading=14,
            textColor=colors.HexColor(TEXTO), wordWrap="CJK",
        ),
        "vazio": ParagraphStyle(
            "vazio", fontName=FONTE, fontSize=13, leading=20,
            textColor=colors.HexColor(CINZA), alignment=TA_CENTER,
        ),
    }


def montar_capa(nome_cofre, data_str, total, cifrado):
    est = _estilos()
    story = [Spacer(1, 42 * mm)]
    if os.path.isfile(ICONE):
        try:
            img = Image(ICONE, width=38 * mm, height=38 * mm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 14 * mm))
        except Exception:
            pass
    story.append(Paragraph(TITULO_RELATORIO, est["titulo"]))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(f"Cofre: <b>{escape(nome_cofre)}</b>", est["info"]))
    story.append(Paragraph(f"Gerado em: {escape(data_str)}", est["info"]))
    story.append(Paragraph(f"Registros: {total}", est["info"]))
    story.append(Spacer(1, 16 * mm))
    story.append(Paragraph("―" * 30, est["subtitulo"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "⚠  Documento confidencial.<br/>Contém credenciais de acesso.", est["aviso"]
    ))
    story.append(Spacer(1, 2 * mm))
    if cifrado:
        story.append(Paragraph("Protegido por senha (AES).", est["aviso"]))
    else:
        story.append(Paragraph(
            "<font color='#c0392b'><b>SEM PROTEÇÃO — conteúdo em texto puro.</b></font>",
            est["aviso"],
        ))
    return story


def montar_card(registro, indice):
    est = _estilos()
    nome = _campo(registro, "nome")
    login = _campo(registro, "login")
    senha = _campo(registro, "senha", preservar_espacos=True)
    url = _campo(registro, "url")
    observacoes = _campo(registro, "observacoes")

    linhas = [
        f'<font size="8" color="{CINZA}">CARD {indice:02d}</font>',
        f'<font size="13" color="{TEXTO}"><b>{nome}</b></font>',
        f'<b>Login:</b> {login}',
        f'<b>Senha:</b> <font name="{FONTE_MONO}" color="{VERDE}">{senha}</font>',
        f'<b>URL:</b> <font color="{AZUL}">{url}</font>',
        f'<b>Obs.:</b> <font color="{CINZA}">{observacoes}</font>',
    ]
    paragrafo = Paragraph("<br/>".join(linhas), est["card"])

    card = Table([["", paragrafo]], colWidths=[3.5, LARGURA_UTIL - 3.5])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(AZUL)),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor(CARD_BG)),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDA)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 9),
        ("RIGHTPADDING", (1, 0), (1, 0), 9),
        ("TOPPADDING", (1, 0), (1, 0), 7),
        ("BOTTOMPADDING", (1, 0), (1, 0), 7),
    ]))
    return card


class _NumberedCanvas(rl_canvas.Canvas):
    """Canvas que sabe o total de páginas para desenhar 'Página X de Y'."""

    contexto = {"cofre": "", "data": ""}

    def __init__(self, *args, **kwargs):
        rl_canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._desenhar_cabecalho_rodape(total)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _desenhar_cabecalho_rodape(self, total):
        if self._pageNumber <= 1:
            return
        largura, altura = A4
        self.saveState()
        self.setStrokeColor(colors.HexColor(BORDA))
        self.setLineWidth(0.4)
        self.setFont(FONTE, 8)
        self.setFillColor(colors.HexColor(CINZA))
        self.drawString(MARGEM, altura - 11 * mm, self.contexto["cofre"])
        self.drawRightString(largura - MARGEM, altura - 11 * mm, TITULO_RELATORIO)
        self.line(MARGEM, altura - 13 * mm, largura - MARGEM, altura - 13 * mm)

        self.line(MARGEM, 13 * mm, largura - MARGEM, 13 * mm)
        self.drawString(MARGEM, 9 * mm, self.contexto["data"])
        self.drawRightString(
            largura - MARGEM, 9 * mm, f"Página {self._pageNumber} de {total}"
        )
        self.restoreState()


def montar_documento(caminho, registros, nome_cofre, data_str, senha_pdf):
    est = _estilos()
    cifrado = bool(senha_pdf)
    cifra = None
    if cifrado:
        cifra = StandardEncryption(
            senha_pdf, senha_pdf,
            canPrint=1, canModify=0, canCopy=0, canAnnotate=0, strength=128,
        )
    doc = BaseDocTemplate(
        caminho, pagesize=A4,
        leftMargin=MARGEM, rightMargin=MARGEM,
        topMargin=MARGEM, bottomMargin=MARGEM,
        title=f"{TITULO_RELATORIO} — {nome_cofre}",
        author="Cofre de Senhas",
        subject="Relatório de credenciais",
        encrypt=cifra,
    )

    frame_capa = Frame(MARGEM, MARGEM, LARGURA_UTIL, A4[1] - 2 * MARGEM, id="capa")
    frame_corpo = Frame(MARGEM, MARGEM, LARGURA_UTIL, A4[1] - 2 * MARGEM, id="corpo")
    doc.addPageTemplates([
        PageTemplate(id="capa", frames=[frame_capa]),
        PageTemplate(id="corpo", frames=[frame_corpo]),
    ])

    story = montar_capa(nome_cofre, data_str, len(registros), cifrado)
    story.append(NextPageTemplate("corpo"))
    story.append(PageBreak())

    if registros:
        for indice, registro in enumerate(registros, start=1):
            story.append(KeepTogether(montar_card(registro, indice)))
            story.append(Spacer(1, 4 * mm))
    else:
        story.append(Spacer(1, 30 * mm))
        story.append(Paragraph("Nenhum registro encontrado.", est["vazio"]))

    _NumberedCanvas.contexto = {"cofre": nome_cofre, "data": data_str}
    doc.build(story, canvasmaker=_NumberedCanvas)


def confirmar_sobrescrita(caminho: str, force: bool) -> bool:
    if force or not os.path.exists(caminho):
        return True
    resposta = input(f"O arquivo {caminho} já existe. Sobrescrever? [s/N]: ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def gerar_pdf(caminho, registros, nome_cofre, senha_pdf):
    destino = os.path.abspath(os.path.expanduser(caminho))
    diretorio = os.path.dirname(destino) or "."
    fd, tmp = tempfile.mkstemp(prefix=".exportar_pdf_", suffix=".pdf", dir=diretorio)
    os.close(fd)
    try:
        montar_documento(tmp, registros, nome_cofre, _agora_str(), senha_pdf)
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        os.replace(tmp, destino)
        tmp = None
        try:
            os.chmod(destino, 0o600)
        except OSError:
            pass
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
    return destino


def _agora_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


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

    registrar_fontes()
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
