# Importação Massiva — Exemplos e Modelos

Documento complementar à [especificação](./importacao_massiva.md).

---

## 1. Exemplo mínimo (formato lista)

`registros_minimo.json`:

```json
[
  { "nome": "GitHub", "login": "daniel", "senha": "minhaSenha123!" },
  { "nome": "E-mail", "login": "daniel@exemplo.com", "senha": "outraSenha#45" }
]
```

---

## 2. Exemplo com todos os campos (formato objeto)

`registros_completo.json`:

```json
{
  "registros": [
    {
      "nome": "GitHub",
      "login": "daniel",
      "senha": "minhaSenha123!",
      "url": "https://github.com",
      "observacoes": "conta pessoal, 2FA ativo"
    },
    {
      "nome": "AWS Console",
      "login": "daniel@empresa.com",
      "senha": "C0mpl3x@Senha",
      "url": "https://console.aws.amazon.com",
      "observacoes": "conta da empresa"
    }
  ]
}
```

> Campos `id`, `criado_em` e `atualizado_em`, mesmo que presentes, são **ignorados**
> e recriados automaticamente pelo script.

---

## 3. Modelo de execução

```bash
# A partir da raiz do projeto, com o venv ativo
python scripts/importar_registros.py registros_completo.json
```

O script pergunta interativamente:

```
Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Secret ID: abc123...
Senha Mestra: (a digitação não aparece)
```

---

## 4. Exemplo de arquivo com itens problemáticos

`registros_problematicos.json`:

```json
[
  { "nome": "Válido", "login": "ok", "senha": "123456" },
  { "nome": "Sem senha", "login": "user" },
  { "nome": "Sem login", "senha": "abc" },
  { "nome": "", "login": "vazio", "senha": "abc" },
  42,
  { "nome": "Válido", "login": "ok", "senha": "123456" }
]
```

Resultado esperado (assumindo cofre vazio):

```
Itens lidos ..: 6
  ✓ Importados ........: 1   ("Válido" / "ok")
  ↷ Pulados (existente): 0
  ↷ Pulados (repetido) : 1   (#6, mesmo nome+login do #1)
  ✗ Inválidos ..........: 4   (#2 sem senha, #3 sem login, #4 nome vazio, #5 não-objeto)
```

---

## 5. Prompt de confirmação (exemplo)

```
Resumo:
  Serão importados : 35
  Pulados          : 4
  Inválidos        : 3
  Backup será salvo em: /home/daniel/meu_cofre.vault.2026-10-03_141530.bak

Deseja gravar as alterações no cofre? [s/N]:
```

Use `--yes` para pular essa confirmação em automações.

---

## 6. Uso com `--yes` (automação)

```bash
python scripts/importar_registros.py lote.json --yes
```

As credenciais continuam sendo pedidas interativamente; apenas a confirmação final
é dispensada.

---

## 7. Dicas

- Sempre confira o backup gerado antes de migrações em massa.
- Para lotes grandes, rode primeiro em um **cofre de teste**.
- Senhas duplicadas de serviço não são deduplicadas por segurança — a chave de
  duplicidade é apenas `nome` + `login`.
- Evite colocar `id`/datas no JSON: serão descartados.
