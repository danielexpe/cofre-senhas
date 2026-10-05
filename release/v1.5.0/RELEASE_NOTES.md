# 🔐 Cofre de Senhas 1.5

Gerenciador de senhas local, seguro e open-source, com criptografia forte
(AES + SHA512 + PBKDF2) e interface gráfica moderna. Seus dados nunca saem da
sua máquina.

---

## ✨ Novidades desta versão

- **Exportação e importação JSON pela interface gráfica** — botões
  **⬆️ Exportar JSON** e **⬇️ Importar JSON** no cabeçalho da tela do cofre.
  A importação mescla com deduplicação (`nome` + `login`), mostra um resumo
  para confirmação e cria **backup automático** do `.vault` antes de gravar.
- **Relatório PDF pela interface gráfica** — botão **📄 Exportar PDF** gerando o
  mesmo relatório A4 (capa, cards, cabeçalho/rodapé numerado) do CLI, com
  opção de senha de abertura para cifrar o PDF.
- **Diálogos na GUI** — seleção de arquivo, senha do PDF, resumo de importação,
  relatório final e indicador de progresso.
- **Operações em segundo plano** — exportar/importar rodam em thread de fundo,
  mantendo a interface responsiva; a entrega do resultado é feita com segurança
  na thread da interface.

### Por baixo do capô

- Novo pacote **`servicos/`** com o núcleo compartilhado (importação,
  exportação JSON, geração de PDF e backup). Os scripts de linha de comando
  continuam idênticos — viraram wrappers finos sobre `servicos/`, então os
  **formatos de arquivo continuam 100% compatíveis** entre GUI e CLI.
- O relatório PDF usa **ReportLab** com as fontes **DejaVu** embutidas.

---

## 📦 Artefatos

| Arquivo | Descrição |
|---|---|
| `CofreDeSenhas-1.5.0-x86_64.AppImage` | Aplicativo para Linux (x86_64), portátil, sem instalação |
| `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| `SHA256SUMS.asc` | Assinatura GPG (destacada) dos checksums |
| `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

---

## ✅ Verificação de integridade e assinatura

Fingerprint GPG do autor:
`D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`

```bash
# Ajuste o nome do arquivo baixado, se necessário
APP="CofreDeSenhas-1.5.0-x86_64.AppImage"

# 1) Importar a chave pública do autor
gpg --import DANIEL-PUBKEY.asc

# 2) Verificar a assinatura dos checksums
gpg --verify SHA256SUMS.asc SHA256SUMS

# 3) Conferir o hash do AppImage (deve bater com a linha em SHA256SUMS)
sha256sum "$APP"

# 4) (Opcional) Checar a assinatura PGP embutida no AppImage
./"$APP" --appimage-signature | head -n 20
```

> ⚠️ Se você esquecer sua senha mestra, não há como recuperá-la. Faça backups
> dos seus arquivos `.vault`.

---

## 🚀 Como executar (Linux)

```bash
chmod +x CofreDeSenhas-1.5.0-x86_64.AppImage
./CofreDeSenhas-1.5.0-x86_64.AppImage
```

Ou simplesmente **dois cliques** no arquivo. Sem instalação e sem dependências.

---

## 🔒 Segurança dos exports

- O **JSON** exportado contém as senhas em texto puro; o arquivo é gravado com
  permissão `0600` e há aviso na interface.
- O **PDF** pode ser cifrado com uma senha de abertura (AES); sem senha, é
  gerado com aviso destacado de que está sem proteção.
- A importação cria um backup `.vault.<timestamp>.bak` antes de gravar.

---

## 🛠️ Gerar a partir do código-fonte

```bash
git clone https://github.com/danielexpe/cofre-senhas.git
cd cofre-senhas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 🔗 Links

- Repositório: https://github.com/danielexpe/cofre-senhas
- Releases: https://github.com/danielexpe/cofre-senhas/releases
