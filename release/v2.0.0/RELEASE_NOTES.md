# Cofre de Senhas 2.0

Gerenciador de senhas local, seguro e open-source, com criptografia forte
(AES/Fernet + SHA512 + PBKDF2) e interface gráfica moderna. Seus dados nunca
saem da sua máquina.

Esta é uma versão **major** por causa da mudança no formato dos cofres.
Cofres v1 continuam abrindo normalmente e são migrados automaticamente, mas
cofres já migrados para v2 **não abrem em versões antigas** do aplicativo.

---

## Novidades desta versão

- **Novo formato de cofre v2** — o Secret ID não é mais gravado em texto claro
  no arquivo `.vault`. O cabeçalho passa a usar `salt + salt2 + payload
  cifrado`, e o Secret ID continua entrando na derivação da chave a partir da
  interface (cache local ou formulário).
- **Migração automática no login** — ao abrir um cofre v1 com o Secret ID e a
  senha corretos, o aplicativo converte o arquivo para v2 na hora, preservando
  todos os registros. Não é necessário editar ou salvar o cofre.
- **Escrita atômica** — os cofres são gravados em arquivo temporário e
  substituídos com `os.replace`, reduzindo o risco de corrupção em caso de
  falha ou queda de energia. Permissão `0600` aplicada em sistemas POSIX.
- **Mensagem de autenticação unificada** — SID ou senha incorretos não revelam
  qual credencial falhou.
- **Exportação JSON/PDF atualizada** — o Secret ID é obtido do cache local pelo
  caminho do cofre; se não estiver no cache, é solicitado no terminal.

### Segurança e compatibilidade

- O Secret ID **nunca** é gravado nos arquivos `.vault`.
- O cache local (`~/.cofre_cache.json`) continua guardando o Secret ID por
  conveniência; esse risco é assumido pelo usuário.
- Cofres v1 são lidos e migrados automaticamente.
- Após a migração para v2, versões anteriores à 2.0 não conseguem abrir o
  cofre. Faça backup do `.vault` e guarde o Secret ID antes de migrar.
- Se você perder o Secret ID, não há recuperação.

---

## Artefatos

| Arquivo | Descrição |
|---|---|
| `CofreDeSenhas-2.0.0-x86_64.AppImage` | Aplicativo para Linux (x86_64), portátil, sem instalação |
| `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| `SHA256SUMS.asc` | Assinatura GPG (destacada) dos checksums |
| `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

---

## Verificação de integridade e assinatura

Fingerprint GPG do autor:
`D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`

```bash
# Ajuste o nome do arquivo baixado, se necessário
APP="CofreDeSenhas-2.0.0-x86_64.AppImage"

# 1) Importar a chave pública do autor
gpg --import DANIEL-PUBKEY.asc

# 2) Verificar a assinatura dos checksums
gpg --verify SHA256SUMS.asc SHA256SUMS

# 3) Conferir o hash do AppImage (deve bater com a linha em SHA256SUMS)
sha256sum "$APP"

# 4) (Opcional) Checar a assinatura PGP embutida no AppImage
./"$APP" --appimage-signature | head -n 20
```

> Aviso: se você esquecer a senha mestra ou o Secret ID, não há como
> recuperá-los. Faça backups dos seus arquivos `.vault` e guarde o Secret ID
> em local seguro.

---

## Como executar (Linux)

```bash
chmod +x CofreDeSenhas-2.0.0-x86_64.AppImage
./CofreDeSenhas-2.0.0-x86_64.AppImage
```

Ou simplesmente dois cliques no arquivo. Sem instalação e sem dependências.

---

## Segurança dos exports

- O JSON exportado contém as senhas em texto puro; o arquivo é gravado com
  permissão `0600` e há aviso na interface.
- O PDF pode ser cifrado com uma senha de abertura (AES); sem senha, é gerado
  com aviso destacado de que está sem proteção.
- A importação cria um backup `.vault.<timestamp>.bak` antes de gravar.
- Ambos os scripts de exportação obtêm o Secret ID do cache local ou pedem no
  terminal; o `.vault` não contém o SID.

---

## Gerar a partir do código-fonte

```bash
git clone https://github.com/danielexpe/cofre-senhas.git
cd cofre-senhas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Links

- Repositório: https://github.com/danielexpe/cofre-senhas
- Releases: https://github.com/danielexpe/cofre-senhas/releases
- Documentação do formato v2: `docs/seguranca_vault_v2.md`
