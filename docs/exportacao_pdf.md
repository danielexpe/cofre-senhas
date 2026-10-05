# Especificação — Exportação em PDF (Relatório de Credenciais)

> Ferramenta de linha de comando para gerar, a partir de um cofre `.vault`, um
> **relatório em PDF elegante e pronto para impressão**, com um card por registro.
> O PDF é **cifrado** quando o usuário informa uma senha de abertura.

Versão do documento: 0.1
Autor: Daniel
Status: **Aprovada e implementada** (`scripts/exportar_pdf.py`)

Documentos relacionados:
- [Exportação em PDF — Exemplos](./exportacao_pdf_exemplos.md)
- [Guia do script de PDF](../scripts/README_exportar_pdf.md)
- [Exportação de registros (JSON)](./exportacao_registros.md)

---

## 1. Objetivo

Permitir que o usuário gere um relatório impresso de todas as credenciais de um
cofre, sem passar pela interface gráfica. O documento deve ter aparência de
relatório profissional (capa, cabeçalho, rodapé com numeração, cards bem
organizados) e ser gerado inteiramente offline.

O script reaproveita a camada de criptografia (`seguranca/encriptacao.py`) e o
modelo de dados (`dados/armazenamento.py`) já existentes.

## 2. Fora de escopo

- Integração com a GUI (botão na tela principal) — especificada em
  [integracao_gui.md](./integracao_gui.md).
- Exportação parcial / filtros (por busca, tag ou seleção de registros).
- Impressão direta (o usuário abre/imprime o PDF).
- Assinatura digital do PDF.
- Outros formatos de relatório (HTML, DOCX, XLSX).
- Exportação das senhas **mascaradas** (decisão: sempre em texto puro).

---

## 3. Decisões de projeto

| Tema | Decisão |
|------|---------|
| Biblioteca | **ReportLab** (5.x) + **Pillow** (para ler o PNG da capa) |
| Tamanho/orientação | **A4 retrato** |
| Fonte | **DejaVu Sans / DejaVu Sans Bold / DejaVu Sans Mono**, embutidas em `assets/fonts/` |
| Emoji | **Removidos** (a fonte embutida não renderiza emoji colorido) |
| Tema | **Claro com detalhes de cor**, pensado para impressão |
| Layout | **Cards/blocos**, um por registro |
| Capa | **Sim**, com `assets/icone.png`, título, arquivo do cofre, data e total |
| Cabeçalho/rodapé | **Sim**: cabeçalho com o nome do cofre; rodapé com `Página X de Y` |
| Ordem | **Alfabética por `nome`** (case-insensitive e sem acento) |
| Senhas | **Sempre exibidas em texto puro** (fonte monoespaçada) |
| Cifra do PDF | **Pergunta sempre a senha do PDF**; **vazia → sem cifra (com aviso)**; não vazia → **AES** |
| Credenciais do cofre | Caminho por prompt; **Secret ID** lido do cabeçalho; **senha mestra** via `getpass` |
| Caminho de saída | **Argumento posicional opcional**; se omitido, pergunta |
| Arquivo existente | **Confirmar** (s/N); `--force` sobrescreve sem perguntar |
| Escrita | **Atômica** (arquivo temporário + `os.replace`), UTF-8, permissão **`0600`** |
| Cofre vazio | Gera o PDF com a capa e a mensagem "Nenhum registro encontrado." (código `0`) |
| Cofre alterado | **Nunca** — operação somente leitura no `.vault` |
| Local do script | **Definido:** `scripts/exportar_pdf.py` |

---

## 4. Dependências

Novas dependências do projeto (adicionar a `requirements.txt` e ao build
PyInstaller/AppImage):

| Pacote | Versão atual | Uso |
|--------|--------------|-----|
| `reportlab` | 5.0.1 | Geração do PDF (Platypus, fontes TTF, cifra) |
| `pillow` | 12.3.0 | Leitura do `assets/icone.png` para a capa |

Observações:

- O script é uma ferramenta de linha de comando (como o de JSON) e **não** faz
  parte do AppImage da GUI; `reportlab`/`pillow` são necessários para rodá-lo a
  partir do código-fonte (`pip install -r requirements.txt`).
- As fontes DejaVu são de licença livre (Bitstream Vera / DejaVu); o arquivo de
  licença acompanha `assets/fonts/` (`LICENSE-DejaVu.txt`).

---

## 5. Estrutura do documento

```
┌─────────────────────────────────────────────┐
│  CAPA                                        │
│   [logo]                                     │
│   Relatório de Credenciais                   │
│   Cofre: meu_cofre.vault                     │
│   Gerado em: 05/10/2026 01:30                │
│   Registros: 42                              │
│   (aviso de conteúdo sensível)               │
├─────────────────────────────────────────────┤
│  Cabeçalho (a partir da 2ª página):          │
│   meu_cofre.vault · Relatório de Credenciais │
│  ──────────────────────────────────────────  │
│   Card 01                                    │
│   🏷 Nome            Login: ...              │
│                     Senha: ...               │
│                     URL:   ...               │
│                     Obs.:  ...               │
│   Card 02 ...                                │
│  ──────────────────────────────────────────  │
│  Rodapé:                        Página 2 de 5│
└─────────────────────────────────────────────┘
```

### 5.1 Capa

- Logo do projeto (`assets/icone.png`), centralizado no topo.
- Título: **Relatório de Credenciais**.
- Nome do arquivo do cofre (basename).
- Data/hora de geração (formato `dd/mm/aaaa HH:MM`).
- Total de registros.
- Aviso: "⚠ Documento confidencial. Contém credenciais de acesso."
- Se o PDF **não** estiver cifrado: aviso destacado de que está **sem proteção**.

### 5.2 Cabeçalho e rodapé

- Cabeçalho (exceto na capa): nome do cofre à esquerda e "Relatório de
  Credenciais" à direita, separados por uma linha fina.
- Rodapé: data de geração à esquerda e `Página X de Y` à direita.
- A contagem total de páginas exige o padrão *NumberedCanvas* do ReportLab
  (buffering em `save()` para saber o total).

### 5.3 Corpo

- Cards numerados (`Card 01`, `Card 02`, …) em ordem alfabética.
- Cada card é mantido inteiro na mesma página (`KeepTogether`); se não couber,
  vai para a próxima.
- Se um único card for maior que a página (observações gigantes), ele pode ser
  dividido, com o cabeçalho do card repetido.

---

## 6. Layout visual (design tokens)

| Token | Valor |
|-------|-------|
| Cor primária | `#2b6cb0` (azul, igual ao app) |
| Cor de destaque da senha | `#16a085` (verde) |
| Texto principal | `#1f2937` |
| Texto secundário/rótulos | `#6b7280` |
| Fundo do card | `#f3f4f6` |
| Borda do card | `#d1d5db` |
| Fundo da página | `#ffffff` |
| Margens | ~18 mm |
| Rótulo/campo | Rótulos em negrito; campos em fonte regular |

Anatomia de um card:

- Cartão retangular com borda fina, fundo claro (`#f3f4f6`) e uma **barra de
  acento** azul (`#2b6cb0`) à esquerda.
- Linha de título: número do card + `nome` em negrito e corpo maior.
- Linhas `Rótulo: valor`:
  - `Login` — texto normal.
  - `Senha` — **fonte monoespaçada** para leitura fácil.
  - `URL` — texto em azul.
  - `Observações` — texto secundário; `—` quando vazio.
- Valores longos quebram em várias linhas; palavras sem espaço (URLs/senhas
  longas) são quebradas para não estourar a largura.

---

## 7. Conteúdo dos campos

| Campo | Exibição |
|-------|----------|
| `nome` | Título do card (negrito) |
| `login` | Linha `Login:` |
| `senha` | Linha `Senha:` em **monoespaçada** (texto puro) |
| `url` | Linha `URL:`; `—` se vazio |
| `observacoes` | Bloco `Observações:`; `—` se vazio |

Normalização:

- Todos os valores são lidos com fallback para `""` e convertidos para texto,
  como em `scripts/exportar_registros.py` (`_texto`).
- Acentos são preservados; **emojis e símbolos não suportados são removidos**
  antes de compor o texto (ver §7.1).
- Ordenação alfabética por `nome`, comparando sem diferenciar maiúsculas e
  **ignorando acentos** (chave normalizada NFD sem marcas combinantes).

### 7.1 Tratamento de emoji

- Remove faixas de emoji (ex.: `U+1F300–U+1FAFF`), selectors de variação
  (`U+FE0F`), *zero-width joiner* (`U+200D`) e o último resquício de `U+200B`.
- Não tenta substituir por texto; apenas limpa, pois a fonte embutida não
  renderiza emoji colorido.
- Acentos e caracteres latinos (inclusive `ç`, `ã`, `á`) são mantidos.

---

## 8. Cifra do PDF

Fluxo da senha de abertura do PDF (independente da senha mestra do cofre):

1. Prompt `Senha de abertura do PDF (vazio = sem cifra):` com `getpass`.
2. Se **vazia** → gera o PDF **sem cifra**, imprimindo um **aviso destacado** de
   que o arquivo contém credenciais em texto puro e não está protegido.
3. Se **não vazia** → aplica cifra **AES** via
   `reportlab.lib.pdfencrypt.StandardEncryption`, com:
   - `userPassword` = senha informada (abre/descriptografa);
   - `ownerPassword` = senha informada (sem senha de dono separada);
   - `canPrint = 1` (impressão permitida — é o propósito do documento);
   - `canModify = 0`, `canCopy = 0`, `canAnnotate = 0` (best-effort).
   - `strength = 128` (usar **256** se a versão do ReportLab suportar).
4. Confirmar no relatório final se o PDF ficou cifrado ou não.

> Se o usuário esquecer a senha do PDF, **não há recuperação** — o mesmo princípio
> da senha mestra. Documentar isso no aviso final.

---

## 9. Fluxo de execução

```
1. Obter o caminho do PDF de saída (argumento posicional ou prompt).
2. Prompt: caminho do cofre (.vault).
3. Verificar se o arquivo do cofre existe.
4. Ler o Secret ID do cabeçalho do .vault (ler_secret_id_do_arquivo).
5. Prompt: Senha Mestra (getpass).
6. Decriptar o cofre (decriptar_cofre) → lista de registros.
7. Ordenar alfabeticamente por nome e montar os cards.
8. Prompt: Senha de abertura do PDF (getpass; vazio = sem cifra).
9. Se o arquivo de saída existir e não houver --force: confirmar (s/N).
10. Gerar o PDF em arquivo temporário (mesmo diretório), com ReportLab.
11. Aplicar permissão 0600 e renomear atomicamente (os.replace).
12. Exibir relatório final (caminho, total, cifrado? e avisos).
```

O `.vault` nunca é modificado.

---

## 10. Interface de linha de comando

```
Uso:
    python scripts/exportar_pdf.py [SAIDA.pdf]
    python scripts/exportar_pdf.py [SAIDA.pdf] --force
    python scripts/exportar_pdf.py --help

Argumentos:
    SAIDA.pdf         Caminho do PDF de saída (opcional; se omitido, pergunta).
                      Aceita "~".

Opções:
    -h, --help        Mostra ajuda e encerra.
    -f, --force       Sobrescreve o arquivo de saída sem pedir confirmação.
```

Credenciais e senha do PDF **não** são argumentos de linha de comando:

| Dado | Forma de obtenção |
|------|-------------------|
| Caminho do cofre | Prompt interativo (`input`) |
| Secret ID | Lido do cabeçalho do `.vault` |
| Senha mestra | Prompt (`getpass`) |
| Senha de abertura do PDF | Prompt (`getpass`); vazio = sem cifra |

---

## 11. Segurança

- ⚠️ **O PDF contém as senhas em texto puro.** A única proteção é a senha de
  abertura (opcional) e a permissão do arquivo. Avisar claramente no terminal e
  na capa.
- O arquivo é gravado com permissão **`0600`** (`chmod` best-effort).
- Escrita **atômica**: gera em arquivo temporário no mesmo diretório e só então
  `os.replace`, evitando arquivos parciais; em erro, remove o temporário.
- Senha mestra e senha do PDF lidas com `getpass` e mantidas apenas em memória.
- O script **não** grava senhas em logs ou arquivos temporários além do PDF.
- Metadados do PDF (Título/Autor/Assunto) preenchidos, sem incluir senhas.
- Impressão de credenciais é responsabilidade do usuário; orientar a recolher e
  descartar com segurança.

---

## 12. Relatório final no terminal (exemplo)

Cifrado:

```
=== Exportação PDF — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo PDF ..: /home/daniel/meu_cofre.pdf
Registros ....: 42
Cifrado ......: sim (AES)

⚠️  O PDF contém senhas em TEXTO PURO. A proteção é a senha de abertura.
    Guarde o arquivo e a senha com cuidado. Não há recuperação da senha.
```

Sem cifra (senha vazia):

```
=== Exportação PDF — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo PDF ..: /home/daniel/meu_cofre.pdf
Registros ....: 42
Cifrado ......: NÃO

⚠️  ATENÇÃO: PDF SEM CIFRA, contendo senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.
```

**Códigos de saída:**

| Código | Significado |
|--------|-------------|
| `0` | Sucesso (inclusive cofre vazio) |
| `1` | Erro de autenticação ou de leitura do cofre (não existe, senha incorreta, corrompido) |
| `2` | Erro ao gerar/gravar o PDF (caminho inválido, sem permissão, falha do ReportLab) |
| `130` | Cancelado pelo usuário (recusa em sobrescrever ou Ctrl+C) |

---

## 13. Estrutura de código proposta

```
scripts/
  exportar_pdf.py     # entrypoint CLI
```

Importações principais:

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.pdfencrypt import StandardEncryption
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
```

Funções internas sugeridas:

| Função | Responsabilidade |
|--------|------------------|
| `registrar_fontes()` | Registra as TTF de `assets/fonts/` (Sans, Bold, Mono) |
| `limpar_texto(s) -> str` | Normaliza para texto e remove emojis |
| `ordenar_registros(registros) -> list` | Ordena por nome (sem caixa/acento) |
| `montar_card(registro, indice) -> Flowable` | Monta o card em Platypus |
| `montar_capa(...)`, `montar_cabecalho_rodape(...)` | Capa e template de páginas |
| `decidir_cifra(senha_pdf) -> StandardEncryption \| None` | Cifra opcional |
| `confirmar_sobrescrita(caminho, force) -> bool` | Pergunta se o arquivo existe |
| `gerar_pdf(caminho, registros, senha_pdf, ...) -> str/None` | Gera atomicamente |
| `imprimir_relatorio(...)` | Saída padronizada (§12) |
| `main(argv=None) -> int` | Orquestra o fluxo |

Reaproveita do `exportar_registros.py` o estilo de CLI (`argparse`), de relatório
e de códigos de saída.

---

## 14. Casos de teste previstos

1. Gerar PDF de cofre com 3 registros → arquivo válido (assinatura `%PDF-`),
   contém capa, cabeçalho/rodapé e 3 cards.
2. PDF **com** senha de abertura abre com a senha e **não** abre sem/com senha
   errada (validar com `pypdf`, se disponível, ou visualmente).
3. PDF **sem** senha (vazia) abre sem senha e exibe aviso de "sem cifra".
4. Nomes exibidos em ordem alfabética, ignorando caixa e acento.
5. Acentos preservados; emojis removidos sem quebrar o texto.
6. Senha/URL longas quebram corretamente dentro do card.
7. Registros com `url`/`observacoes` vazios mostram `—`.
8. Cofre vazio → PDF com capa e "Nenhum registro encontrado.", código `0`.
9. Senha mestra errada → código `1`, **nenhum** PDF criado.
10. Cofre inexistente/corrompido → código `1`, nenhum PDF criado.
11. Arquivo de saída existente, sem `--force`, resposta "não" → código `130`,
    arquivo original intacto.
12. Caminho de saída inválido/sem permissão → código `2`.
13. Permissão final do PDF é `0600`.
14. Cofre de origem inalterado (hash idêntico antes/depois).
15. Muitos registros (ex.: 80) → paginação e numeração `Página X de Y` corretas.

---

## 15. Critérios de aceite

- [ ] Gera um PDF válido, imprimível em A4, com capa, cabeçalho e rodapé.
- [ ] Um card por registro, com todos os campos e senha em texto puro.
- [ ] Ordenação alfabética por nome (sem caixa/acento).
- [ ] Acertos de emoji/acentos conforme §7.
- [ ] Cifra AES quando houver senha; sem cifra (com aviso) quando vazia.
- [ ] O `.vault` nunca é modificado.
- [ ] Permissão `0600` e escrita atômica.
- [ ] Relatório final claro e códigos de saída conforme §12.
- [ ] `requirements.txt` e o empacotamento incluem `reportlab` e `pillow`, além
      das fontes em `assets/fonts/`.
- [ ] CRUD da GUI continua funcionando sem regressão.

---

## 16. Pontos em aberto (versões futuras)

1. **Exportação pela GUI** — planejada em
   [integracao_gui.md](./integracao_gui.md) (botão "Exportar PDF" na tela
   principal).
2. **Filtros de exportação** — por busca, seleção de cards ou tags.
3. **Logo/skin configurável** — permitir trocar o ícone ou o título do relatório.
4. **QR code por registro** — ex.: link para o site.
5. **Cifra AES-256** — habilitar se/como a versão do ReportLab permitir.
6. **Modo "senha mascarada"** — opção de ocultar as senhas no PDF.
