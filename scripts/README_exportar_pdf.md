# Exportar PDF — Guia de Uso

Script de linha de comando para gerar um **relatório em PDF** com todos os
registros de um cofre `.vault`, pronto para impressão (A4), com capa, um card por
registro e rodapé com numeração.

- Arquivo: `scripts/exportar_pdf.py`
- Requer o ambiente virtual ativo com as dependências do projeto
  (`cryptography`, `reportlab`, `pillow`).

> Especificação completa: [`docs/exportacao_pdf.md`](../docs/exportacao_pdf.md)
> Exemplos: [`docs/exportacao_pdf_exemplos.md`](../docs/exportacao_pdf_exemplos.md)

---

## 1. Uso básico

A partir da **raiz do projeto**, com o venv ativo:

```bash
python scripts/exportar_pdf.py meu_cofre.pdf
```

Se você não informar o arquivo de saída, o script pergunta:

```bash
python scripts/exportar_pdf.py
Arquivo PDF de saída: meu_cofre.pdf
```

Em seguida, o script pergunta o caminho do cofre, a senha mestra e a senha de
abertura do PDF:

```
Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Senha Mestra: (a digitação não aparece)
Senha de abertura do PDF (vazio = sem cifra): (a digitação não aparece)
```

O **Secret ID** é lido automaticamente do cabeçalho do `.vault` — não é pedido.

---

## 2. Parâmetros

```
Uso:
    python scripts/exportar_pdf.py [SAIDA.pdf] [-f]

Argumentos posicionais:
    SAIDA.pdf       Caminho do PDF de saída.
                    Opcional: se omitido, o script pergunta no terminal.
                    Aceita caminhos com "~" (ex.: ~/relatorio.pdf).

Opções:
    -h, --help      Mostra a ajuda e encerra.
    -f, --force     Sobrescreve o arquivo de saída sem pedir confirmação.
```

> O caminho do cofre, a senha mestra e a senha do PDF **nunca** são argumentos de
> linha de comando — são sempre solicitados no terminal, e as senhas não aparecem
> na tela.

---

## 3. Perguntas interativas

| Ordem | Prompt | Observação |
|-------|--------|------------|
| 1 | `Arquivo PDF de saída:` | Só aparece se a saída **não** foi passada como argumento. |
| 2 | `Caminho do cofre (.vault):` | Aceita `~`. |
| 3 | `Senha Mestra:` | `getpass` — não aparece na tela. |
| 4 | `Senha de abertura do PDF (vazio = sem cifra):` | `getpass`; **Enter** gera sem cifra. |
| 5 | `O arquivo ... já existe. Sobrescrever? [s/N]:` | Só se a saída existir e **sem** `--force`. |

O Secret ID **não** é pedido: é lido do cabeçalho do `.vault`.

---

## 4. O que é gerado

Um PDF **A4 retrato** com:

- **Capa**: logo, título "Relatório de Credenciais", nome do cofre, data/hora de
  geração, total de registros e aviso de confidencialidade.
- **Cabeçalho/rodapé**: nome do cofre e `Página X de Y`.
- **Cards**: um por registro, em **ordem alfabética por nome**, com:
  - `nome` (título),
  - `Login`,
  - `Senha` (texto puro, fonte monoespaçada),
  - `URL` (`—` se vazio),
  - `Observações` (`—` se vazio).

Cofre vazio gera o PDF com a mensagem "Nenhum registro encontrado." (código `0`).

Acentos são preservados; **emojis são removidos** (a fonte embutida não renderiza
emoji colorido).

---

## 5. Cifra do PDF

- **Senha informada** → PDF **cifrado com AES** (abre com a senha; impressão
  permitida, cópia/alteração bloqueadas quando o leitor respeita as permissões).
- **Senha vazia (Enter)** → PDF **sem cifra**, com **aviso destacado** de que
  contém senhas em texto puro sem proteção.

> Não há recuperação da senha do PDF. Guarde-a com cuidado.

---

## 6. Segurança

> ⚠️ **O PDF contém as senhas em texto puro.** Trate-o como uma senha.

- O arquivo é gravado com permissão **`0600`** (somente o dono lê; best-effort no
  Windows).
- A escrita é **atômica** (temporário no mesmo diretório + `os.replace`): em erro
  não há arquivo parcial, e um arquivo existente permanece intacto.
- Senha mestra e senha do PDF são mantidas apenas em memória e nunca gravadas.
- O `.vault` **não** é modificado — nenhum backup é necessário.
- Apague o PDF após o uso, ou guarde-o cifrado. Ao imprimir, recolha/descarte o
  papel com segurança.

---

## 7. Relatório final

```
=== Exportação PDF — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo PDF ..: /home/daniel/meu_cofre.pdf
Registros ....: 42
Cifrado ......: sim (AES)

⚠️  O PDF contém senhas em TEXTO PURO. A proteção é a senha de abertura.
    Guarde o arquivo e a senha com cuidado. Não há recuperação da senha.
```

Quando o PDF sai sem cifra, o bloco de aviso muda para destacar o risco.

---

## 8. Códigos de saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso (inclusive cofre vazio) |
| `1` | Erro de autenticação ou de leitura do cofre (não existe, senha incorreta, corrompido) |
| `2` | Erro ao gerar/gravar o PDF (caminho inválido, sem permissão, falha do ReportLab) |
| `130` | Cancelado pelo usuário (recusa em sobrescrever ou Ctrl+C) |

---

## 9. Exemplo completo

```bash
# 1) Gerar com confirmação de sobrescrita (senhas pedidas no terminal)
python scripts/exportar_pdf.py ~/meu_cofre.pdf

# 2) Automação: sobrescreve direto
python scripts/exportar_pdf.py ~/meu_cofre.pdf --force
```

---

## 10. Dicas

- Faça um teste abrindo o PDF em um leitor e **imprimindo uma página** para
  conferir o layout antes de tiragens grandes.
- Guarde o PDF sempre cifrado; use uma senha diferente da senha mestra.
- Para migrar dados entre cofres, prefira o
  [export em JSON](./README_exportar_registros.md); o PDF é para leitura/impressão.
