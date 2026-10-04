# 🔐 Cofre de Senhas 1.3

Gerenciador de senhas local, seguro e open-source, com criptografia forte
(AES + SHA512 + PBKDF2) e interface gráfica moderna. Seus dados nunca saem da
sua máquina.

---

## ✨ Novidades desta versão

- **Importação massiva pela linha de comando** — novo script
  `scripts/importar_registros.py` para importar um lote de credenciais de um
  arquivo JSON para um cofre `.vault` já existente, com validação,
  deduplicação (`nome` + `login`), backup automático antes de gravar e
  relatório final detalhado. Veja `scripts/README_importar_registros.md`.
- **Lista de registros muito mais rápida** — a tela principal agora
  virtualiza os cards (apenas os visíveis são criados/desenhados) e a busca
  tem debounce. O app deixa de travar com muitos registros — testado com
  milhares de entradas.

---

## 📦 Artefatos

| Arquivo | Descrição |
|---|---|
| `CofreDeSenhas-1.3-x86_64.AppImage` | Aplicativo para Linux (x86_64), portátil, sem instalação |
| `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| `SHA256SUMS.asc` | Assinatura GPG (destacada) dos checksums |
| `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

---

## ✅ Verificação de integridade e assinatura

Fingerprint GPG do autor:
`D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`

```bash
# Ajuste o nome do arquivo baixado, se necessário
APP="CofreDeSenhas-1.3-x86_64.AppImage"

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
chmod +x CofreDeSenhas-1.3-x86_64.AppImage
./CofreDeSenhas-1.3-x86_64.AppImage
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
