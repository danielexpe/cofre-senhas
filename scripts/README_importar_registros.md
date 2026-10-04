# Importar Registros — Guia de Uso

Script de linha de comando para inserir vários registros de uma só vez em um cofre
`.vault` já existente, a partir de um arquivo JSON.

- Arquivo: `scripts/importar_registros.py`
- Requer o ambiente virtual ativo com as dependências do projeto (`cryptography`).

---

## 1. Uso básico

A partir da **raiz do projeto**, com o venv ativo:

```bash
python scripts/importar_registros.py registros.json
```

Se você não informar o arquivo JSON, o script pergunta:

```bash
python scripts/importar_registros.py
Arquivo JSON de entrada: registros.json
```

---

## 2. Parâmetros

```
Uso:
    python scripts/importar_registros.py [ARQUIVO.json] [-y]

Argumentos posicionais:
    ARQUIVO.json    Caminho do JSON de entrada.
                    Opcional: se omitido, o script pergunta no terminal.
                    Aceita caminhos com "~" (ex.: ~/lote.json).

Opções:
    -h, --help      Mostra a ajuda e encerra.
    -y, --yes       Não pede confirmação antes de gravar (assume "sim").
                    Útil para automação. As credenciais continuam sendo
                    pedidas interativamente.
```

> As credenciais (**caminho do cofre, Secret ID e senha mestra**) **nunca** são
> argumentos de linha de comando — são sempre solicitadas no terminal, e a senha
> mestra não aparece na tela.

---

## 3. Perguntas interativas

Na execução, o script faz estas perguntas, nesta ordem:

| Ordem | Prompt | Observação |
|-------|--------|------------|
| 1 | `Arquivo JSON de entrada:` | Só aparece se o arquivo **não** foi passado como argumento. |
| 2 | `Caminho do cofre (.vault):` | Caminho do cofre existente. Aceita `~`. |
| 3 | `Secret ID:` | O mesmo Secret ID usado na criação do cofre. |
| 4 | `Senha Mestra:` | Lida com `getpass` — a digitação **não** aparece na tela. |
| 5 | `Deseja gravar as alterações no cofre? [s/N]:` | Só aparece sem `--yes`. Responda `s`/`sim`/`y`/`yes` para gravar; qualquer outra coisa cancela. |

Exemplo de sessão:

```
$ python scripts/importar_registros.py registros.json

Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Secret ID: 3f2a9c...  (seu Secret ID)
Senha Mestra:          (a digitação não aparece)

Resumo:
  Serão importados : 35
  Pulados          : 4
  Inválidos        : 3
  Backup será salvo em: /home/daniel/meu_cofre.vault.2026-10-03_141530.bak

Deseja gravar as alterações no cofre? [s/N]: s
```

---

## 4. Formato do arquivo de entrada

O JSON pode estar em **dois formatos**, detectados automaticamente.

### 4.1 Formato A — lista pura

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

### 4.2 Formato B — objeto com a chave `registros`

```json
{
  "registros": [
    {
      "nome": "GitHub",
      "login": "daniel",
      "senha": "s3nha-forte",
      "url": "https://github.com",
      "observacoes": "conta pessoal, 2FA ativo"
    }
  ]
}
```

### 4.3 Campos aceitos

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `nome` | Sim | Nome/identificação do registro (texto não vazio). |
| `login` | Sim | Login ou e-mail (texto não vazio). |
| `senha` | Sim | Senha (texto não vazio). |
| `url` | Não | Endereço do site. Default: `""`. |
| `observacoes` | Não | Texto livre. Default: `""`. |
| `id` | Não | **Ignorado** — o script gera um novo. |
| `criado_em` | Não | **Ignorado** — o script gera. |
| `atualizado_em` | Não | **Ignorado** — o script gera. |

Campos desconhecidos são **ignorados**, mas geram um aviso no relatório final.

---

## 5. Regras de validação e duplicidade

Um item é **importado** quando é um objeto JSON e `nome`, `login` e `senha` são
textos não vazios.

Um item é **inválido** (e pulado) quando:

- não é um objeto (ex.: número, texto, `null`);
- falta `nome`, `login` ou `senha`, ou estão vazios;
- os campos obrigatórios não são texto.

A **chave de duplicidade** é `nome + login`, comparada sem diferenciar
maiúsculas/minúsculas e ignorando espaços nas pontas.

- Se já existir no cofre → **pulado (existente)**.
- Se repetir dentro do próprio arquivo → só o primeiro é importado; os demais são
  **pulados (repetido)**.

Itens inválidos ou pulados **não interrompem** o lote: são listados no relatório.

---

## 6. Backup

Antes de gravar, o script cria uma cópia do próprio `.vault` **já cifrado**:

```
<cofre>.vault.<AAAA-MM-DD_HHMMSS>.bak
```

Exemplo: `meu_cofre.vault.2026-10-03_141530.bak`

O backup **não** contém dados em texto puro e pode ser aberto normalmente com o
cofre. Ele só é criado quando há registros a importar.

---

## 7. Relatório final

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

Aviso: campos desconhecidos ignorados: extra, foo

--- Itens não importados ---
[inválido]  #12  motivo: campo obrigatório ausente: 'senha'
[inválido]  #27  motivo: item não é um objeto JSON
[inválido]  #31  motivo: 'login' vazio
[duplicado] #5   motivo: já existe no cofre (nome+login: "GitHub" / "daniel")
[repetido]  #9   motivo: repetido no próprio arquivo (nome+login: "GitHub" / "daniel")
```

---

## 8. Códigos de saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso (mesmo que alguns itens tenham sido pulados ou nada tenha sido importado). |
| `1` | Erro de autenticação, cofre inexistente ou falha ao criar backup/gravar. |
| `2` | Erro no arquivo JSON (não encontrado, JSON inválido, formato desconhecido). |
| `130` | Cancelado pelo usuário (Ctrl+C ou resposta diferente de "sim"). |

---

## 9. Exemplo completo

Arquivo `lote.json`:

```json
{
  "registros": [
    { "nome": "GitHub", "login": "daniel", "senha": "minhaSenha123!" },
    { "nome": "AWS Console", "login": "daniel@empresa.com", "senha": "C0mpl3x@Senha",
      "url": "https://console.aws.amazon.com", "observacoes": "conta da empresa" }
  ]
}
```

Execução sem confirmação (automação):

```bash
python scripts/importar_registros.py lote.json --yes
```

As credenciais continuam sendo pedidas interativamente; apenas a confirmação
final é dispensada.

---

## 10. Dicas

- Sempre confira o backup gerado antes de migrações em massa.
- Para lotes grandes, rode primeiro contra um **cofre de teste**.
- Evite colocar `id`/datas no JSON: serão descartados.
- Senhas iguais de serviços diferentes **não** são deduplicadas — a chave é apenas
  `nome` + `login`.
