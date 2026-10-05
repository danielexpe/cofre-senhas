# 🔐 Cofre de Senhas 1.4

Gerenciador de senhas local, seguro e open-source, com criptografia forte
(AES + SHA512 + PBKDF2) e interface gráfica moderna. Seus dados nunca saem da
sua máquina.

---

## ✨ Novidades desta versão

- **Correção da rolagem por roda do mouse na lista de registros** — a roda do
  mouse voltou a funcionar junto com a barra de rolagem na tela principal
  (lista de senhas) do cofre. A regressão havia sido introduzida na
  virtualização da lista (v1.3): o handler era ativado/desativado por
  `<Enter>`/`<Leave>`, que o Tk dispara como `NotifyInferior` assim que o
  ponteiro passa do container para o canvas, desligando a rolagem.
- **Rolagem também na lista de cofres recentes** — a tela inicial passou a usar
  o mesmo mecanismo robusto de rolagem.
- **Suporte de roda multiplataforma** — o handler agora cobre
  `<Button-4>`/`<Button-5>` (Linux) e `<MouseWheel>` (Windows/macOS), com
  detecção do widget sob o ponteiro pela cadeia de `master` (mesmo padrão do
  CustomTkinter).

---

## 📦 Artefatos

| Arquivo | Descrição |
|---|---|
| `CofreDeSenhas-1.4-x86_64.AppImage` | Aplicativo para Linux (x86_64), portátil, sem instalação |
| `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| `SHA256SUMS.asc` | Assinatura GPG (destacada) dos checksums |
| `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

---

## ✅ Verificação de integridade e assinatura

Fingerprint GPG do autor:
`D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`

```bash
# Ajuste o nome do arquivo baixado, se necessário
APP="CofreDeSenhas-1.4-x86_64.AppImage"

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
chmod +x CofreDeSenhas-1.4-x86_64.AppImage
./CofreDeSenhas-1.4-x86_64.AppImage
```

Ou simplesmente **dois cliques** no arquivo. Sem instalação e sem dependências.

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
