# 🔐 Cofre de Senhas 1.4.1

Gerenciador de senhas local, seguro e open-source, com criptografia forte
(AES + SHA512 + PBKDF2) e interface gráfica moderna. Seus dados nunca saem da
sua máquina.

---

## ✨ Novidades desta versão

Esta é uma **atualização de segurança** das dependências. Não há mudanças de
interface nem de formato de arquivo — os cofres `.vault` da versão 1.4 continuam
abrindo normalmente.

- **`cryptography` 48.0.0 → 50.0.2** — resolve os alertas do Dependabot:
  - `GHSA-537c-gmf6-5ccf` — OpenSSL vulnerável embutido nos wheels (out-of-bounds read)
  - `CVE-2026-69247` — oráculo Bleichenbacher no decripto de PKCS#7 `EnvelopedData`
  - `CVE-2026-69248` — verificador aceitava wildcard DNS escapando de `permittedSubtrees`
  - `CVE-2026-69249` — DoS por blowup exponencial ao montar cadeia com intermediários duplicados
- **`setuptools` 82.0.1 → 84.0.0** — resolve `CVE-2026-59890` (bypass de exclusão do
  `MANIFEST.in` via normalização Unicode ao gerar sdist).

> Nota: as falhas de X.509/PKCS#7 (CVE-2026-69247/48/49) não eram acionáveis por
> esta aplicação, que usa apenas `Fernet`/`PBKDF2`. Ainda assim, as dependências
> foram atualizadas para manter a base limpa.

Verificação realizada: `pip-audit -r requirements.txt` → **No known vulnerabilities found**,
além de testes de criptografia (round-trip, senha/Secret ID incorretos, corrupção)
e de retrocompatibilidade (cofre gerado com `cryptography` 48 abre na 50).

---

## 📦 Artefatos

| Arquivo | Descrição |
|---|---|
| `CofreDeSenhas-1.4.1-x86_64.AppImage` | Aplicativo para Linux (x86_64), portátil, sem instalação |
| `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| `SHA256SUMS.asc` | Assinatura GPG (destacada) dos checksums |
| `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

---

## ✅ Verificação de integridade e assinatura

Fingerprint GPG do autor:
`D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`

```bash
# Ajuste o nome do arquivo baixado, se necessário
APP="CofreDeSenhas-1.4.1-x86_64.AppImage"

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
chmod +x CofreDeSenhas-1.4.1-x86_64.AppImage
./CofreDeSenhas-1.4.1-x86_64.AppImage
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
