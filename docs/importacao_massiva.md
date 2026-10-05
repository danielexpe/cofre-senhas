# Especificação — Importação Massiva de Registros

> Ferramenta de linha de comando para inserir vários registros de uma só vez em um
> cofre `.vault` já existente, a partir de um arquivo JSON.

Versão do documento: 0.1 (rascunho para avaliação)
Autor: Daniel
Status: **Aprovada — pronta para implementação**

---

## 1. Objetivo

Permitir que o usuário importe um lote de credenciais para um cofre existente sem
passar pela interface gráfica. O script reaproveita a camada de criptografia já
existente (`seguranca/encriptacao.py`) e o modelo de dados (`dados/armazenamento.py`).

## 2. Fora de escopo

- Integração com a GUI (botão na tela principal) — especificada em
  [integracao_gui.md](./integracao_gui.md).
- Exportação de registros — especificada em
  [exportacao_registros.md](./exportacao_registros.md).
- Edição/remoção massiva (apenas inclusão).
- Sincronização em nuvem ou rede.

---

## 3. Decisões de projeto

| Tema | Decisão |
|------|---------|
| Credenciais | **Prompt interativo** no terminal, perguntando **caminho do cofre, Secret ID e senha mestra** |
| Secret ID | Lido por `input()` no prompt (não é argumento de linha de comando) |
| Senha mestra | Também solicitada no prompt, lida com `getpass` — **nunca** via argumento nem ecoada na tela |
| Formato JSON | Aceita **lista pura** `[{...}]` **ou** objeto `{"registros": [...]}` |
| Campos `id` e datas | **Sempre gerados automaticamente** pelo script (`novo_registro`) |
| Duplicados | **Pular e reportar** (não sobrescreve) |
| Registros inválidos | **Pular, importar os válidos e reportar** os rejeitados |
| Backup | **Automático** antes de gravar o cofre |
| Dry-run | Fora do escopo desta versão (ver §11) |
| Local do script | **Definido:** `scripts/importar_registros.py` |

---

## 4. Formato do arquivo JSON de entrada

Os campos são exatamente os usados pelo projeto:

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `nome` | ✅ | Nome/identificação do registro |
| `login` | ✅ | Login ou e-mail |
| `senha` | ✅ | Senha |
| `url` | ❌ | Endereço do site (default `""`) |
| `observacoes` | ❌ | Texto livre (default `""`) |
| `id` | ❌ | **Ignorado** — o script gera um novo |
| `criado_em` | ❌ | **Ignorado** — o script gera |
| `atualizado_em` | ❌ | **Ignorado** — o script gera |

### 4.1 Formatos aceitos

**Formato A — lista pura:**

```json
[
  {
    "nome": "GitHub",
    "login": "daniel",
    "senha": "s3nha-forte",
    "url": "https://github.com",
    "observacoes": "conta pessoal"
  },
  {
    "nome": "E-mail",
    "login": "daniel@exemplo.com",
    "senha": "outra-senha"
  }
]
```

**Formato B — objeto com chave `registros`:**

```json
{
  "registros": [
    { "nome": "GitHub", "login": "daniel", "senha": "s3nha-forte" }
  ]
}
```

Detecção automática: se o JSON raiz for `list` → formato A; se for `dict` com chave
`registros` → formato B. Qualquer outro caso é erro de formato.

Campos desconhecidos são **ignorados**, mas geram um aviso no relatório final.

---

## 5. Regras de validação

Um item é considerado **válido** quando:

1. É um objeto JSON (`dict`).
2. `nome`, `login` e `senha` são strings **não vazias** após `strip()`.
3. `url` e `observacoes`, se presentes, são strings (convertidas com `str()` se não forem).

Um item é **inválido** (e por isso rejeitado) quando:

- Não é um objeto (ex.: número, string, `null`).
- Falta `nome`, `login` ou `senha`, ou estão vazios.
- Os campos têm tipo incompatível e não podem ser convertidos.

Itens inválidos **não interrompem** o lote: são contados e listados com o motivo.

---

## 6. Regras de duplicidade

Chave de duplicidade: **`nome` + `login`**, comparados de forma
**case-insensitive** e sem espaços nas pontas.

- **Contra o cofre existente:** se a chave já existir no cofre, o item é pulado.
- **Dentro do próprio lote:** se a chave repetir no mesmo arquivo, só o primeiro é
  importado; os demais são pulados.

> Como o `id` é sempre gerado pelo script, ele **não** é usado para detectar duplicados.
> Se no futuro decidirmos preservar `id`, esta regra deve ser revista.

Itens pulados por duplicidade são reportados separadamente de itens inválidos.

---

## 7. Fluxo de execução

```
1. Obter o caminho do JSON (argumento posicional ou prompt).
2. Ler e parsear o JSON (formatos A/B).
3. Prompt: caminho do cofre (.vault), Secret ID e Senha Mestra (getpass).
4. Verificar se o arquivo do cofre existe.
5. Decriptar o cofre (autentica Secret ID + senha mestra).
6. Normalizar/validar itens → separar válidos / inválidos / duplicados.
7. Exibir resumo do que será feito.
8. Pedir confirmação (s/N).
9. Fazer backup do .vault com timestamp.
10. Acrescentar os válidos e re-encriptar o cofre.
11. Exibir relatório final.
```

---

## 8. Interface de linha de comando

```
Uso:
    python scripts/importar_registros.py [ARQUIVO.json]
    python scripts/importar_registros.py --help

Argumentos:
    ARQUIVO.json      Caminho do JSON de entrada (opcional; se omitido, o
                      script pergunta no terminal).

Opções:
    -h, --help        Mostra ajuda e encerra.
    -y, --yes         Não pede confirmação antes de gravar (assume "sim").
```

As credenciais (caminho do cofre, **Secret ID** e **senha mestra**) **não** são
argumentos — são sempre solicitadas interativamente no prompt. O Secret ID é
digitado normalmente; a senha mestra não aparece na tela.

---

## 9. Segurança

- A senha mestra é lida com `getpass.getpass()` e mantida somente em memória
  durante a execução.
- O script **não** grava a senha mestra, o Secret ID nem o conteúdo do cofre em
  qualquer arquivo temporário/log.
- O backup é uma cópia do `.vault` **já cifrado** — não contém dados em texto puro.
- O cofre é regravado pelo mesmo esquema atual (PBKDF2 + AES/Fernet + SHA512).

---

## 10. Relatório final (exemplo)

```
=== Importação Massiva — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo JSON .: registros.json
Itens lidos ..: 42

  ✓ Importados ........: 35
  ↷ Pulados (existente): 3
  ↷ Pulados (repetido) : 1
  ✗ Inválidos ..........: 3

Backup .......: /home/daniel/meu_cofre.vault.2026-10-03_141530.bak
Total no cofre: 60 registro(s)

--- Itens não importados ---
[inválido]  #12  motivo: campo obrigatório ausente: 'senha'
[inválido]  #27  motivo: item não é um objeto JSON
[inválido]  #31  motivo: 'login' vazio
[duplicado] #5   motivo: já existe no cofre (nome+login: "GitHub" / "daniel")
[repetido]  #9   motivo: repetido no próprio arquivo (nome+login: "GitHub" / "daniel")
```

**Códigos de saída:**

| Código | Significado |
|--------|-------------|
| `0` | Sucesso (mesmo que alguns itens tenham sido pulados) |
| `1` | Erro de autenticação, cofre inexistente ou falha ao gravar |
| `2` | Erro no arquivo JSON (não encontrado, JSON inválido, formato desconhecido) |
| `130` | Cancelado pelo usuário (Ctrl+C ou resposta "não") |

---

## 11. Pontos em aberto (para decisão)

1. **Confirmação antes de gravar:** incluir sempre, ou permitir `--yes`? (proposto: ambos).
2. **Dry-run (`--dry-run`):** não selecionado para esta versão; pode entrar depois.
3. **Atualizar o cache de recentes:** o script deve chamar
   `dados.cache.adicionar_ou_atualizar`? (proposto: **não**, pois é operação de
   manutenção; o cache se atualiza quando o usuário abrir o cofre pela GUI).
4. **Formato de backup:** `arquivo.vault.<timestamp>.bak` (proposto) vs
   `arquivo.vault.bak` fixo. Manter apenas os N backups mais recentes?

> Resolvido: local do script definido como `scripts/importar_registros.py`;
> credenciais (Secret ID e senha mestra) sempre solicitadas no prompt interativo.

---

## 12. Estrutura de código proposta

```
scripts/
  importar_registros.py     # entrypoint CLI
```

O script pode ser implementado como um único arquivo, importando:

```python
from seguranca.encriptacao import decriptar_cofre, encriptar_cofre
from dados.armazenamento import novo_registro, buscar_registros
```

Funções internas sugeridas:

| Função | Responsabilidade |
|--------|------------------|
| `carregar_json(caminho) -> list[dict]` | Lê e normaliza os formatos A/B |
| `normalizar(item) -> dict \| None` | Valida e devolve registro pronto ou `None` |
| `chave_duplicidade(reg) -> str` | `"nome|login"` normalizado |
| `fazer_backup(caminho) -> str` | Copia o `.vault` com timestamp |
| `main()` | Orquestra o fluxo e imprime o relatório |

---

## 13. Casos de teste previstos

1. Importar 3 registros válidos em cofre vazio → 3 importados.
2. JSON no formato B (`{"registros": [...]}`) → funciona igual ao formato A.
3. Registro sem `senha` → inválido, demais importados.
4. Registro com `nome+login` já existente no cofre → pulado.
5. Dois registros iguais dentro do arquivo → o segundo é pulado.
6. Senha mestra errada → erro, nada é gravado, backup **não** é criado.
7. Secret ID errado → erro, nada é gravado.
8. JSON inexistente/inválido → código de saída `2`.
9. Confirmação "não" → nada é gravado, código `130`.
10. Verificar que o backup criado é aberto normalmente com a senha correta.
11. Campos extras no JSON → ignorados com aviso.

---

## 14. Critérios de aceite

- [ ] CRUD da GUI continua funcionando sem regressão.
- [ ] Importa corretamente de ambos os formatos JSON.
- [ ] Nunca sobrescreve registros existentes (regra de pulo).
- [ ] Nunca corrompe o cofre: backup é criado antes de gravar.
- [ ] Senha mestra nunca é exposta no histórico do shell nem em disco.
- [ ] Relatório final claro, com contagens e motivos.
- [ ] Códigos de saída conforme §10.
