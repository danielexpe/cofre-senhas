# 🔐 Cofre de Senhas 1.6

Gerenciador de senhas local, seguro e open-source, com criptografia forte
(AES + SHA512 + PBKDF2) e interface gráfica moderna. Seus dados nunca saem da
sua máquina.

---

## ✨ Novidades desta versão

- **Tela inicial redesenhada** — cabeçalho compacto em uma linha, cards de
  cofres recentes com hover e textos truncados, e melhor aproveitamento do
  espaço em janelas menores.
- **Barra de rolagem condicional** — exibida apenas quando há mais de 5 cofres
  recentes, mantendo a lista limpa em telas com poucos itens.
- **Tela de secrets reformulada** — lista virtualizada (canvas + pool de cards)
  para manter o desempenho mesmo com muitos registros, cards de 2 linhas com
  hover e espaçamento aprimorado.
- **Ações com rótulos e tooltips** — botões de copiar, editar e excluir com
  rótulos claros na tela de secrets; botões de ícone recebem descrição ao passar
  o mouse.
- **Janela mais compacta** — tamanho padrão de 700x600 (mínimo 700x450),
  melhorando o uso em telas pequenas e notebooks.

### Por baixo do capô

- Novo módulo **`ui/tooltip.py`** para tooltips reutilizáveis.
- **CustomTkinter 6.0** e dependências de build atualizadas.
- Documentação de desenvolvimento (**`AGENTS.md`**) e especificações de layout
  das telas inicial e de secrets adicionadas ao repositório.

---

## 📦 Artefatos

| Arquivo | Descrição |
|---|---|
| `CofreDeSenhas-1.6.0-x86_64.AppImage` | Aplicativo para Linux (x86_64), portátil, sem instalação |
| `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| `SHA256SUMS.asc` | Assinatura GPG (destacada) dos checksums |
| `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

---

## ✅ Verificação de integridade e assinatura

Fingerprint GPG do autor:
`D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`

```bash
# Ajuste o nome do arquivo baixado, se necessário
APP="CofreDeSenhas-1.6.0-x86_64.AppImage"

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
chmod +x CofreDeSenhas-1.6.0-x86_64.AppImage
./CofreDeSenhas-1.6.0-x86_64.AppImage
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
