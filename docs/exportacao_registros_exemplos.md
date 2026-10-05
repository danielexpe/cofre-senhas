# Exportação de Registros — Exemplos e Modelos

Documento complementar à [especificação](./exportacao_registros.md).

> O JSON de saída é **100% compatível** com `scripts/importar_registros.py`. Os
> exemplos abaixo podem ser usados diretamente em testes de round-trip.

---

## 1. Exemplo de saída (cofre com 2 registros)

`meu_cofre.json`:

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
      "nome": "E-mail",
      "login": "daniel@exemplo.com",
      "senha": "outraSenha#45",
      "url": "",
      "observacoes": ""
    }
  ]
}
```

Note que `url` e `observacoes` aparecem **sempre**, mesmo vazios.

---

## 2. Saída de cofre vazio

```json
{
  "registros": []
}
```

---

## 3. Exemplo com acentos, emoji e caracteres especiais

O export usa UTF-8 e `ensure_ascii=False`, então os textos permanecem legíveis e
são reimportados sem perda.

```json
{
  "registros": [
    {
      "nome": "Banco Ação 🏦",
      "login": "josé.silva@exemplo.com",
      "senha": "S3nh@ \"quotes\" \\barra\\ e\nova linha",
      "url": "https://banco.exemplo.com",
      "observacoes": "chave PIX: josé@exemplo.com — atenção à acentuação"
    }
  ]
}
```

---

## 4. Modelo de execução (exportar)

```bash
# A partir da raiz do projeto, com o venv ativo
python scripts/exportar_registros.py meu_cofre.json
```

O script pergunta interativamente **apenas o caminho do cofre** e a senha mestra
(o Secret ID é lido do próprio arquivo `.vault`):

```
Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Senha Mestra: (a digitação não aparece)
```

---

## 5. Round-trip completo (exportar → importar em outro cofre)

```bash
# 1) Exporta o cofre de origem
python scripts/exportar_registros.py /tmp/migracao.json

# 2) Importa o JSON gerado em um cofre de destino (vazio)
python scripts/importar_registros.py /tmp/migracao.json
```

Na importação:

```
Caminho do cofre (.vault): /home/daniel/cofre_destino.vault
Secret ID: 3f2a9c...
Senha Mestra: (a digitação não aparece)

Resumo:
  Serão importados : 2
  Pulados          : 0
  Inválidos        : 0
```

Resultado esperado: os campos `nome`, `login`, `senha`, `url` e `observacoes`
idênticos aos da origem. Os campos `id`, `criado_em` e `atualizado_em` serão
**novos** no destino (gerados pelo import).

---

## 6. Arquivo de saída já existente

Sem `--force`, o script pergunta:

```
O arquivo /tmp/migracao.json já existe. Sobrescrever? [s/N]:
```

- Responder `s` → sobrescreve.
- Responder qualquer outra coisa → aborta com código `130`, sem tocar no arquivo.

Para automação:

```bash
python scripts/exportar_registros.py /tmp/migracao.json --force
```

---

## 7. Relatório final (exemplo)

```
=== Exportação — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo JSON .: /tmp/migracao.json
Registros ....: 60
Exportados ...: 60

⚠️  ATENÇÃO: o arquivo contém senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.
```

Com registro que não sobrevive ao round-trip (campo obrigatório vazio no cofre):

```
--- Avisos de round-trip (não serão reimportados) ---
[inválido] #12  motivo: 'senha' vazio
```

---

## 8. Uso em automação (script de migração)

```bash
#!/usr/bin/env bash
set -euo pipefail

ORIGEM="/home/daniel/cofre_origem.vault"
DESTINO="/home/daniel/cofre_destino.vault"
TMP="$(mktemp --suffix=.json)"

# Exporta (senha mestra será pedida no terminal)
python scripts/exportar_registros.py "$TMP" --force

# Importa no destino (senha mestra será pedida novamente)
python scripts/importar_registros.py "$TMP" --yes

# Apaga o arquivo em texto puro
shred -u "$TMP" 2>/dev/null || rm -f "$TMP"
```

---

## 9. Dicas

- O arquivo exportado é **texto puro**: trate-o como uma senha. Use permissões
  restritas (o script já cria com `0600`) e apague-o após o uso
  (`shred -u` quando disponível).
- Para backup durável e seguro, prefira manter o próprio `.vault` (cifrado).
- Faça um teste primeiro em um **cofre de destino vazio** antes de mesclar em um
  cofre que já tenha registros.
- Lembre-se: ao importar num cofre que já tenha o mesmo `nome + login`, o item é
  **pulado** (não sobrescreve).
