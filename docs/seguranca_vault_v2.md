# Planejamento — Formato de cofre V2 (sem Secret ID em claro)

Status: **planejado, ainda não implementado**.
Versão de release: **2.0.0** (mudança de formato incompatível com versões antigas).

## 1. Objetivo

Remover o Secret ID em texto claro dos arquivos `.vault` **sem quebrar** a
abertura de cofres existentes e mantendo o layout atual de cabeçalho com
`salt + 32 bytes`.

O cenário que motiva a mudança:

- O `~/.cofre_cache.json` continua guardando o Secret ID. Esse risco é aceito
  conscientemente e **não faz parte deste trabalho**.
- Os arquivos `.vault` podem ser copiados para um drive privado de nuvem.
  Portanto, um `.vault` isolado não deve revelar o Secret ID.

## 2. Decisão de projeto

### 2.1 Abordagens descartadas

**Cifrar o Secret ID no cabeçalho com chave derivada da senha mestra.**
Não traz ganho real: quem testar a senha decifra o Secret ID e abre o cofre.
O Secret ID deixa de ser um fator independente e vira apenas ofuscação.

**Placeholder `"XXXXXX"` com substituição de ida e volta.**
Funciona no papel, mas cria janelas de exposição: o SID real fica no disco
enquanto o cofre está aberto e a cada gravação automática. Crash, kill, queda
de energia ou sync de nuvem podem capturar o arquivo nesse intervalo. Também
exige tratar todos os caminhos de saída e gravações atômicas.

### 2.2 Abordagem adotada

**Nunca escrever o Secret ID no `.vault`.**

- O Secret ID continua sendo usado na derivação da chave (KDF), mas vem da
  interface (cache ou formulário) e nunca é persistido no arquivo.
- Os 32 bytes do cabeçalho passam a ser um **segundo salt público aleatório**
  (`salt2`), sem nenhuma relação com o Secret ID.
- O layout físico permanece com o mesmo tamanho: magic + 16 bytes + 32 bytes +
  payload Fernet.
- A leitura de cofres v1 continua funcionando; a escrita passa a ser sempre v2.

### 2.3 Modelo de ameaça

Em escopo:

- Cópia isolada do `.vault` (backup, vazamento, drive de nuvem).
- Sem o Secret ID, o ataque offline precisa adivinhar 128 bits de SID **e** a
  senha mestra, o que é inviável.

Fora de escopo / risco aceito:

- O cache local contém o Secret ID.
- Comprometimento da máquina, malware, keylogger, acesso à memória do processo.
- Senha mestra fraca.
- Perda do cache sem ter anotado o Secret ID: não há recuperação.

### 2.4 Decisões registradas

- **2026-10-17 — Migração automática no login:** a migração de cofres v1 para
  v2 ocorrerá automaticamente após a autenticação bem-sucedida, assim que o
  cofre for aberto. Não será necessário editar ou salvar o cofre para que a
  migração aconteça. Se a gravação falhar, o v1 permanece intacto e a migração
  será tentada novamente no próximo salvamento.

## 3. Especificação do formato

### 3.1 v1 (legado)

```
[MAGIC_V1 (8 bytes)][salt (16 bytes)][secret_id ASCII (32 bytes)][Fernet]
```

`MAGIC_V1 = b"VAULTv1\x00"`.

### 3.2 v2 (novo)

```
[MAGIC_V2 (8 bytes)][salt (16 bytes)][salt2 (32 bytes)][Fernet]
```

`MAGIC_V2 = b"VAULTv2\x00"`.

| Campo | Tamanho | Geração | Observação |
|---|---|---|---|
| magic | 8 | constante | identifica a versão |
| salt | 16 | `os.urandom(16)` | salt principal |
| salt2 | 32 | `os.urandom(32)` | público, sem relação com o SID |
| payload | variável | Fernet | contém registros + hash de integridade |

- KDF v2: `PBKDF2-HMAC-SHA512(secret_id + ":" + senha_mestra, salt + salt2, 200_000, 32)`.
- KDF v1: permanece `salt` (16 bytes) apenas.
- `salt2` não é segredo. Seu papel é manter o layout de 32 bytes, garantir
  unicidade por arquivo e evitar que qualquer leitor legado interprete esses
  bytes como Secret ID.
- Nenhum campo do cabeçalho contém informação derivada do Secret ID.

## 4. Compatibilidade

| Situação | Resultado |
|---|---|
| App novo abre cofre v1 | Sim (caminho legado preservado) |
| App novo abre cofre v2 | Sim |
| App novo grava | Sempre v2 |
| App antigo abre cofre v1 | Sim |
| App antigo abre cofre v2 | Não (magic desconhecido) |

Consequências:

- A compatibilidade é **retroativa**, não futura. Depois que um cofre for
  gravado em v2, versões antigas do aplicativo não conseguirão abri-lo.
- Antes da primeira migração, o usuário deve manter um backup do `.vault` v1
  ou a versão antiga do aplicativo disponível.
- A mensagem de erro para magic desconhecido deve ser clara:
  `"Este cofre foi criado por uma versão mais nova do aplicativo."`

## 5. Mudanças no código

### 5.1 `seguranca/encriptacao.py`

Constantes:

```python
MAGIC_V1 = b"VAULTv1\x00"
MAGIC_V2 = b"VAULTv2\x00"
SALT_SIZE = 16
SALT2_SIZE = 32
```

`encriptar_cofre(caminho, secret_id, senha_mestra, registros)`:

- Assinatura mantida (o `secret_id` continua necessário para a KDF).
- Gera `salt = os.urandom(SALT_SIZE)` e `salt2 = os.urandom(SALT2_SIZE)`.
- Deriva a chave com `salt + salt2`.
- Monta o arquivo em memória: `MAGIC_V2 + salt + salt2 + fernet.encrypt(...)`.
- Grava com escrita atômica (ver 5.2).
- Nunca escreve `secret_id` no arquivo.

`decriptar_cofre(caminho, secret_id, senha_mestra)`:

- Lê 8 bytes de magic.
- `MAGIC_V1`: lê `salt` (16), lê e **descarta** os 32 bytes legados, lê o
  payload e deriva com `salt`.
- `MAGIC_V2`: lê `salt` (16), lê `salt2` (32), lê o payload e deriva com
  `salt + salt2`.
- Magic desconhecido: erro explícito de versão.
- Remove a comparação `secret_id_arquivo != secret_id`; o SID errado já falha
  no `fernet.decrypt` (`InvalidToken`).
- Mensagem unificada para falha de autenticação:
  `"Secret ID ou senha mestra incorretos, ou cofre corrompido."`
- Validar tamanhos lidos (salt, salt2, payload não vazio) para não mascarar
  arquivo truncado como senha errada.

`ler_secret_id_do_arquivo`:

- **Remover**. Não há mais Secret ID para ler.
- Se algum código externo importar a função, o erro será imediato e explícito.
- Adicionar, se necessário para a migração, `ler_versao_cofre(caminho) -> int`
  que lê apenas o magic.

### 5.2 Escrita atômica

Hoje `encriptar_cofre` abre o destino com `"wb"` e escreve direto. Um crash no
meio da gravação corrompe o cofre. Implementar um helper:

```python
def _gravar_atomico(caminho: str, dados: bytes):
    diretorio = os.path.dirname(os.path.abspath(caminho)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".vault-", suffix=".tmp", dir=diretorio)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        os.replace(tmp, caminho)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
```

- O temporário já é escrito no formato v2, portanto nunca contém o SID.
- Em caso de falha, o arquivo original permanece intacto.
- O temporário é removido em caso de erro.
- Em Windows, `os.replace` é atômico para o mesmo volume.
- Observação: se `caminho` for um symlink, `os.replace` substitui o link.
  Resolver com `os.path.realpath` antes de gravar, se isso for relevante.

### 5.3 Migração v1 → v2

Decisão registrada em 2026-10-17: migrar automaticamente **após o login
bem-sucedido**, em `ui/tela_autenticacao.py`, logo depois de `decriptar_cofre`:

1. Detectar a versão com `ler_versao_cofre(caminho)`.
2. Se for v1, chamar `encriptar_cofre(caminho, sid, senha, registros)`.
3. Como a gravação é atômica, uma falha não destrói o arquivo.
4. Se a gravação falhar (disco cheio, arquivo somente leitura, permissão),
   continuar a sessão normalmente e informar de forma não bloqueante que a
   migração ocorrerá no próximo salvamento.
5. Não exibir diálogo desnecessário no caminho feliz; no máximo, uma nota.

A migração não depende de edição: abrir o cofre já é suficiente para converter
um v1 em v2. O salvamento normal (`ui/tela_principal.py:472` e `:617`) funciona
apenas como nova tentativa caso a conversão no login tenha falhado.

### 5.4 Scripts de exportação

`scripts/exportar_registros.py` e `scripts/exportar_pdf.py` hoje importam
`ler_secret_id_do_arquivo` (linhas 22/88 e 23/77). Ajustes:

- Remover o import e a leitura do cabeçalho.
- Buscar o SID no cache pelo caminho do cofre; se não encontrar, perguntar:

```python
from dados.cache import buscar_secret_id

secret_id = buscar_secret_id(caminho_cofre)
if not secret_id:
    secret_id = input("Secret ID: ").strip()
```

- Atualizar os docstrings: o SID vem do cache local ou do terminal, não do
  cabeçalho do `.vault`.
- `scripts/importar_registros.py` já pede o SID (linha 86) e passará a gravar
  v2 automaticamente via `encriptar_cofre`; não precisa de mudança de lógica.

### 5.5 `dados/cache.py`

Adicionar um helper de consulta, sem alterar o formato de armazenamento:

```python
def buscar_secret_id(caminho_vault: str):
    alvo = os.path.abspath(os.path.expanduser(caminho_vault))
    for entrada in carregar_cache():
        atual = os.path.abspath(os.path.expanduser(entrada.get("caminho", "")))
        if atual == alvo:
            return entrada.get("secret_id")
    return None
```

- Normalizar caminhos é importante porque a GUI grava caminho absoluto e os
  scripts podem receber caminho relativo ou com `~`.
- O cache continua guardando o SID (risco aceito). Não remover.

### 5.6 Interface

- `ui/tela_autenticacao.py`: nenhuma mudança de fluxo além da migração
  automática e da nova mensagem unificada de erro.
- `ui/tela_principal.py` e `ui/tela_novo_cofre.py`: assinaturas de
  `encriptar_cofre`/`decriptar_cofre` não mudam; nenhuma alteração estrutural.
- `ui/tela_inicial.py`: continua pré-preenchendo o SID a partir do cache
  (linha 282), sem mudanças.

### 5.7 Documentação

- `README.md`:
  - atualizar a seção "Como funciona a criptografia" para deixar claro que o
    Secret ID **não** é gravado no `.vault`;
  - corrigir a linha 40, que chama o Secret ID de "metadado não-sensível";
  - documentar a incompatibilidade de cofres v2 com versões antigas do app.
- `AGENTS.md`: atualizar a descrição do formato/segurança, se necessário.
- Docstrings de `seguranca/encriptacao.py` e dos scripts de exportação.
- Bump de versão para 2.0.0 e nota de release.

## 6. Pseudocódigo de referência

```python
def encriptar_cofre(caminho, secret_id, senha_mestra, registros):
    salt = os.urandom(SALT_SIZE)
    salt2 = os.urandom(SALT2_SIZE)
    chave = derivar_chave(secret_id, senha_mestra, salt + salt2)
    fernet = Fernet(chave)

    payload = {
        "registros": registros,
        "integridade": hash_sha512(json.dumps(registros, sort_keys=True).encode()),
    }
    cifrado = fernet.encrypt(json.dumps(payload).encode("utf-8"))

    _gravar_atomico(caminho, MAGIC_V2 + salt + salt2 + cifrado)


def decriptar_cofre(caminho, secret_id, senha_mestra):
    with open(caminho, "rb") as f:
        magic = f.read(len(MAGIC_V2))
        if magic == MAGIC_V1:
            salt = f.read(SALT_SIZE)
            f.read(32)                      # descarta o SID legado
            salt_kdf = salt
        elif magic == MAGIC_V2:
            salt = f.read(SALT_SIZE)
            salt2 = f.read(SALT2_SIZE)
            salt_kdf = salt + salt2
        elif len(magic) < len(MAGIC_V2):
            raise ValueError("Arquivo de cofre inválido ou truncado.")
        else:
            raise ValueError("Cofre criado por uma versão mais nova do aplicativo.")

        if len(salt) != SALT_SIZE:
            raise ValueError("Arquivo de cofre inválido ou truncado.")
        if magic == MAGIC_V2 and len(salt2) != SALT2_SIZE:
            raise ValueError("Arquivo de cofre inválido ou truncado.")

        cifrado = f.read()
        if not cifrado:
            raise ValueError("Arquivo de cofre inválido ou truncado.")

    chave = derivar_chave(secret_id, senha_mestra, salt_kdf)
    try:
        dados_json = Fernet(chave).decrypt(cifrado)
    except InvalidToken:
        raise ValueError("Secret ID ou senha mestra incorretos, ou cofre corrompido.")

    payload = json.loads(dados_json.decode("utf-8"))
    registros = payload.get("registros", [])

    hash_esperado = payload.get("integridade")
    hash_atual = hash_sha512(json.dumps(registros, sort_keys=True).encode())
    if hash_esperado != hash_atual:
        raise ValueError("Falha na verificação de integridade (SHA512).")

    return registros
```

## 7. Casos de borda e tratamento

| Caso | Comportamento esperado |
|---|---|
| Arquivo menor que o magic | "inválido ou truncado" |
| Magic desconhecido | "versão mais nova do aplicativo" |
| Salt/salt2 incompletos | "inválido ou truncado" |
| Payload vazio | "inválido ou truncado" |
| Secret ID errado | erro unificado, sem revelar qual campo falhou |
| Senha errada | erro unificado |
| v1 com SID errado | falha no Fernet, erro unificado |
| Falha ao gravar migração | sessão continua; v1 permanece; erro não bloqueante |
| Disco cheio / sem permissão | arquivo original intacto; temporário removido |
| Duas instâncias abertas | última gravação vence; sem corrupção por escrita atômica |
| Sync de nuvem | temporário é v2; mesmo que seja capturado, não contém SID |
| Symlink no caminho | decidir entre seguir o alvo (`realpath`) ou substituir o link |

Concorrência entre instâncias não é resolvida por este plano (fora de escopo).

## 8. Plano de testes

Não existe suíte automatizada no projeto. Validação proposta:

### 8.1 Antes da mudança

Gerar um cofre v1 de teste com o código atual, usando SID, senha e registros
fictícios, e guardá-lo em `/tmp` (nunca no repositório). Exemplo:

```python
from seguranca.encriptacao import encriptar_cofre
encriptar_cofre("/tmp/cofre_v1.vault", "a" * 32, "senha-teste", [
    {"id": "1", "nome": "Teste", "login": "user", "senha": "123", "url": ""}
])
```

### 8.2 Casos

1. Criar cofre novo: primeiros 8 bytes são `VAULTv2\0`.
2. Confirmar que o SID não aparece no arquivo:
   `strings /tmp/cofre_v2.vault | grep "a\{32\}"` não deve retornar nada.
3. Abrir cofre v2 com SID + senha corretos.
4. Abrir cofre v2 com SID errado: erro unificado.
5. Abrir cofre v2 com senha errada: erro unificado.
6. Abrir cofre v1: funciona e migra para v2.
7. Após a migração, reabrir: continua funcionando.
8. Verificar que o v2 migrado também não contém o SID.
9. Magic inválido: mensagem de versão.
10. Arquivo truncado em cada seção do cabeçalho: mensagem de truncado.
11. Simular falha de escrita (diretório somente leitura): original intacto,
    temporário inexistente.
12. Verificar permissões do `.vault` em Linux (`0o600`).
13. Exportação JSON e PDF: SID obtido do cache; sem cache, prompt funciona.
14. Importação JSON: grava v2 e continua abrindo.
15. Smoke test headless das telas principais.
16. `grep` final para garantir que não restou `ler_secret_id_do_arquivo`
    nem `f.read(32)` associado a SID fora do caminho legado.

### 8.3 Comandos de validação

```bash
source .venv/bin/activate
python -m py_compile main.py ui/*.py seguranca/*.py dados/*.py scripts/*.py servicos/*.py utils/*.py
python main.py
```

Smoke test headless (exemplo):

```python
import customtkinter as ctk
app = ctk.CTk()
from ui.tela_inicial import TelaInicial
TelaInicial(app)
app.update()
app.destroy()
```

### 8.4 Critérios de aceite

- Nenhum `.vault` gerado pelo app novo contém o Secret ID em claro.
- Cofres v1 abrem e migram sem perda de registros.
- Cofres v2 abrem em qualquer máquina, desde que o usuário informe o SID.
- Exportação/importação continuam funcionando.
- Falha de gravação nunca corrompe o cofre original.
- Nenhuma referência restante a `ler_secret_id_do_arquivo`.

## 9. Rollout e rollback

- Antes de migrar, fazer backup do `.vault` v1.
- Comunicar que, após a migração para v2, versões antigas do aplicativo não
  abrem mais o cofre.
- Rollback: manter o AppImage/binário antigo e o backup v1. Não há plano de
  escrever v1 a partir do app novo (isso reintroduziria o SID em claro).
- A migração no login é decisão firmada (ver 2.4 e 5.3). O próximo salvamento
  serve apenas como fallback caso a conversão no login não tenha conseguido
  gravar.

## 10. Checklist de implementação

Implementação concluída em 2026-10-17 (detalhes em
`docs/seguranca_vault_v2_progresso.md`).

- [x] Criar `MAGIC_V1`, `MAGIC_V2`, `SALT2_SIZE` em `seguranca/encriptacao.py`.
- [x] Implementar `_gravar_atomico`.
- [x] Reescrever `encriptar_cofre` para gravar v2 com `salt + salt2`.
- [x] Reescrever `decriptar_cofre` com dispatch v1/v2 e mensagens unificadas.
- [x] Remover `ler_secret_id_do_arquivo`.
- [x] Adicionar `ler_versao_cofre` (se necessário para a migração).
- [x] Implementar migração automática no login em `ui/tela_autenticacao.py`.
- [x] Adicionar `buscar_secret_id` em `dados/cache.py`.
- [x] Ajustar `scripts/exportar_registros.py`.
- [x] Ajustar `scripts/exportar_pdf.py`.
- [x] Atualizar docstrings e `README.md` (criptografia e aviso de downgrade).
- [x] Atualizar `AGENTS.md`, se a descrição do formato mudar.
- [x] Gerar fixture v1 e executar todos os testes da seção 8.
- [x] Verificar com `strings` que nenhum SID aparece nos artefatos v2.
- [x] Rodar `python -m py_compile` em todos os módulos.
- [x] Fazer smoke test headless.
- [x] Bump de versão para 2.0.0 e nota de release em `release/v2.0.0/`.

## 11. Fora de escopo

- Cifrar ou remover o Secret ID do cache local (`~/.cofre_cache.json`).
- Usar keyring/keychain do sistema operacional.
- Remover o hash SHA512 interno (o Fernet já autentica o payload).
- Validar formato hexadecimal do Secret ID.
- Lock entre múltiplas instâncias do aplicativo.
- Zerar segredos da memória (zeroization).
- Alterar iterações do PBKDF2 ou o algoritmo de criptografia.
