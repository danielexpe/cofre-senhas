# Exportar Registros — Guia de Uso

Script de linha de comando para exportar **todos** os registros de um cofre
`.vault` para um arquivo `.json` em texto puro, no **mesmo formato aceito pelo
script de importação massiva**.

- Arquivo: `scripts/exportar_registros.py`
- Requer o ambiente virtual ativo com as dependências do projeto
  (`cryptography`).

> Especificação completa: [`docs/exportacao_registros.md`](../docs/exportacao_registros.md)
> Exemplos: [`docs/exportacao_registros_exemplos.md`](../docs/exportacao_registros_exemplos.md)

---

## 1. Uso básico

A partir da **raiz do projeto**, com o venv ativo:

```bash
python scripts/exportar_registros.py saida.json
```

Se você não informar o arquivo de saída, o script pergunta:

```bash
python scripts/exportar_registros.py
Arquivo JSON de saída: saida.json
```

O script então pergunta o caminho do cofre e a senha mestra:

```
Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Senha Mestra: (a digitação não aparece)
```

O **Secret ID** é lido automaticamente do cabeçalho do `.vault` — não é pedido.

---

## 2. Parâmetros

```
Uso:
    python scripts/exportar_registros.py [SAIDA.json] [-f]

Argumentos posicionais:
    SAIDA.json      Caminho do JSON de saída.
                    Opcional: se omitido, o script pergunta no terminal.
                    Aceita caminhos com "~" (ex.: ~/backup.json).

Opções:
    -h, --help      Mostra a ajuda e encerra.
    -f, --force     Sobrescreve o arquivo de saída sem pedir confirmação.
                    Útil para automação. A senha mestra continua sendo pedida.
```

> As credenciais (**caminho do cofre** e **senha mestra**) **nunca** são
> argumentos de linha de comando — são sempre solicitadas no terminal, e a senha
> mestra não aparece na tela.

---

## 3. Perguntas interativas

| Ordem | Prompt | Observação |
|-------|--------|------------|
| 1 | `Arquivo JSON de saída:` | Só aparece se a saída **não** foi passada como argumento. |
| 2 | `Caminho do cofre (.vault):` | Aceita `~`. |
| 3 | `Senha Mestra:` | Lida com `getpass` — a digitação **não** aparece na tela. |
| 4 | `O arquivo ... já existe. Sobrescrever? [s/N]:` | Só aparece se a saída já existir e **sem** `--force`. |

O Secret ID **não** é pedido: é lido do cabeçalho do arquivo `.vault`.

Exemplo de sessão:

```
$ python scripts/exportar_registros.py ~/migracao.json

Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Senha Mestra:          (a digitação não aparece)

=== Exportação — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo JSON .: /home/daniel/migracao.json
Registros ....: 60
Exportados ...: 60

⚠️  ATENÇÃO: o arquivo contém senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.
```

---

## 4. Formato do arquivo de saída

O topo é um objeto com a chave `registros` (lista na ordem do cofre). Cada item
tem **exatamente** os 5 campos efetivos, sempre presentes:

| Campo | Sempre presente | Descrição |
|-------|:---------------:|-----------|
| `nome` | ✅ | Nome/identificação do registro |
| `login` | ✅ | Login ou e-mail |
| `senha` | ✅ | Senha (texto puro) |
| `url` | ✅ | Endereço do site (`""` se vazio) |
| `observacoes` | ✅ | Texto livre (`""` se vazio) |

```json
{
  "registros": [
    {
      "nome": "GitHub",
      "login": "daniel",
      "senha": "s3nha-forte",
      "url": "https://github.com",
      "observacoes": "conta pessoal"
    }
  ]
}
```

Codificação: **UTF-8**, `indent=2`, `ensure_ascii=False` (acentos e emoji
legíveis), com quebra de linha final.

Cofre vazio gera:

```json
{
  "registros": []
}
```

---

## 5. Compatibilidade com a importação

O arquivo gerado é **100% compatível** com
[`scripts/importar_registros.py`](./README_importar_registros.md):

- É o **Formato B** (`{"registros": [...]}`) aceito pelo import.
- Os campos emitidos são todos conhecidos → **sem** aviso de campos extras.
- `id`, `criado_em` e `atualizado_em` **não** são exportados; o import os gera
  novamente. O round-trip preserva `nome`, `login`, `senha`, `url` e
  `observacoes`.

### Round-trip (exportar → importar em outro cofre)

```bash
python scripts/exportar_registros.py /tmp/migracao.json
python scripts/importar_registros.py /tmp/migracao.json
```

Ao importar num cofre que já tenha o mesmo `nome + login`, o item é **pulado**
(não sobrescreve).

---

## 6. Segurança

> ⚠️ **O JSON exportado contém as senhas em texto puro.** Trate-o como uma senha.

- O script imprime um aviso claro ao final da execução.
- O arquivo é gravado com permissão **`0600`** (somente o dono lê; best-effort no
  Windows).
- A escrita é **atômica** (temporário no mesmo diretório + `os.replace`): em caso
  de erro não há arquivo parcial, e um arquivo existente permanece intacto.
- A senha mestra é mantida apenas em memória e nunca é gravada.
- O `.vault` **não** é modificado — nenhum backup é necessário.
- Apague o JSON após o uso (`shred -u arquivo.json` quando disponível).

---

## 7. Relatório final

```
=== Exportação — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo JSON .: /home/daniel/migracao.json
Registros ....: 60
Exportados ...: 60

⚠️  ATENÇÃO: o arquivo contém senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.
```

Se houver registros que **não** sobreviveriam ao round-trip (campo obrigatório
vazio no cofre), eles são listados:

```
--- Avisos de round-trip (não serão reimportados) ---
[inválido] #12  motivo: 'senha' vazio
[inválido] #27  motivo: 'nome' vazio
```

---

## 8. Códigos de saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso (inclusive cofre vazio) |
| `1` | Erro de autenticação ou de leitura do cofre (não existe, senha incorreta, corrompido) |
| `2` | Erro ao escrever o JSON de saída (caminho inválido, sem permissão) |
| `130` | Cancelado pelo usuário (recusa em sobrescrever ou Ctrl+C) |

---

## 9. Exemplo completo

```bash
# 1) Exportar com confirmação de sobrescrita
python scripts/exportar_registros.py ~/migracao.json

# 2) Exportar em automação (sobrescreve direto)
python scripts/exportar_registros.py ~/migracao.json --force

# 3) Reimportar em outro cofre
python scripts/importar_registros.py ~/migracao.json --yes
```

---

## 10. Dicas

- Faça o primeiro teste de round-trip em um **cofre de destino vazio**.
- Para backups duráveis e seguros, prefira manter o próprio `.vault` cifrado —
  o JSON é apenas para migração/inspeção.
- Apague o JSON após a migração; ele não é cifrado.
- Registros com `nome`, `login` ou `senha` vazios no cofre são exportados, mas
  avisados no relatório (o import os rejeitaria).
