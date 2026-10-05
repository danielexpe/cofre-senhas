# Especificação — Exportação de Registros

> Ferramenta de linha de comando para exportar **todos** os registros de um cofre
> `.vault` para um arquivo `.json` em texto puro, no **mesmo formato aceito pela
> Importação Massiva**, garantindo round-trip (reimportar o JSON gerado em outro
> cofre sem qualquer ajuste manual).

Versão do documento: 0.1
Autor: Daniel
Status: **Aprovada e implementada** (`scripts/exportar_registros.py`)

Documentos relacionados:
- [Especificação — Importação Massiva](./importacao_massiva.md)
- [Importação Massiva — Exemplos](./importacao_massiva_exemplos.md)
- [Guia do script de exportação](../scripts/README_exportar_registros.md)

---

## 1. Objetivo

Permitir que o usuário extraia o conteúdo de um cofre existente para um arquivo
`.json` legível, sem passar pela interface gráfica. O arquivo gerado deve ser
**100% compatível** com `scripts/importar_registros.py`, de modo que possa ser
reimportado em outro cofre (migração, backup em texto, mescla entre cofres).

O script reaproveita a camada de criptografia (`seguranca/encriptacao.py`) e o
modelo de dados (`dados/armazenamento.py`) já existentes.

## 2. Fora de escopo

- Novos botões ou telas na GUI (função apenas via linha de comando).
- Exportação parcial / filtros (por busca, tag ou seleção de registros).
- Exportação cifrada do JSON (o arquivo é texto puro por definição; para backup
  seguro, manter o próprio `.vault`).
- Sincronização em nuvem ou rede.
- Importação (já existe em `scripts/importar_registros.py`).

---

## 3. Decisões de projeto

| Tema | Decisão |
|------|---------|
| Formato raiz | **Objeto** `{"registros": [...]}` (Formato B do import) |
| Campos por registro | **Somente os 5 efetivos**: `nome`, `login`, `senha`, `url`, `observacoes` — sempre presentes (mesmo vazios) |
| `id`, `criado_em`, `atualizado_em` | **Não são exportados** (o import os regenera) |
| Metadados no topo | **Não** — apenas a chave `registros` |
| Ordem | **Mesma ordem** do cofre (fiel ao armazenamento) |
| Caminho de saída | **Argumento posicional opcional**; se omitido, pergunta no terminal |
| Arquivo de saída existente | **Confirmar** (s/N); flag `--force` sobrescreve sem perguntar |
| Proteção do arquivo | **Aviso de texto puro** + permissão restrita **`0600`** (best-effort no Windows) |
| Escrita | **Atômica** (arquivo temporário no mesmo diretório + `os.replace`) |
| Codificação | UTF-8, `indent=2`, `ensure_ascii=False`, com quebra de linha final |
| Secret ID | **Lido do cabeçalho** do `.vault` (`ler_secret_id_do_arquivo`) |
| Senha mestra | Prompt com `getpass` — **nunca** por argumento nem ecoada |
| Cofre vazio | Gera `{"registros": []}` e reporta 0 exportados (código `0`) |
| Cofre alterado | **Nunca** — a operação é somente leitura no `.vault` |
| Local do script | **Definido:** `scripts/exportar_registros.py` |

---

## 4. Formato do arquivo JSON de saída

O topo é um objeto com a chave `registros`, contendo uma lista na ordem do cofre.
Cada item tem exatamente os campos abaixo:

| Campo | Sempre presente | Descrição |
|-------|:---------------:|-----------|
| `nome` | ✅ | Nome/identificação do registro |
| `login` | ✅ | Login ou e-mail |
| `senha` | ✅ | Senha (texto puro) |
| `url` | ✅ | Endereço do site (`""` se vazio) |
| `observacoes` | ✅ | Texto livre (`""` se vazio) |

Exemplo:

```json
{
  "registros": [
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
      "senha": "outra-senha",
      "url": "",
      "observacoes": ""
    }
  ]
}
```

### 4.1 Compatibilidade com a Importação Massiva

- O formato raiz (`{"registros": [...]}`) é o **Formato B** aceito por
  `carregar_json()` do import.
- Os 5 campos emitidos são válidos: `nome`, `login` e `senha` sempre textos não
  vazios (ver §4.2); `url` e `observacoes` sempre textos.
- Nenhum campo desconhecido é emitido, então **não há aviso** de "campos
  desconhecidos" ao reimportar.
- `id`, `criado_em` e `atualizado_em` não são enviados; o import cria novos. O
  round-trip preserva `nome`, `login`, `senha`, `url` e `observacoes`.

### 4.2 Registros que não sobrevivem ao round-trip

A GUI e o `.vault` permitem, em tese, registros com `nome`/`login`/`senha`
vazios. Como o import **rejeita** itens com esses campos vazios, o export deve:

- Exportar o registro **fielmente** (não alterar dados);
- **Listar um aviso** no relatório final com os registros que seriam inválidos no
  import (índice + motivo), para que o usuário saiba que não serão reimportados.

Essa é a única situação em que o round-trip não reproduz um registro.

---

## 5. Fluxo de execução

```
1. Obter o caminho do JSON de saída (argumento posicional ou prompt).
2. Prompt: caminho do cofre (.vault).
3. Verificar se o arquivo do cofre existe.
4. Ler o Secret ID do cabeçalho do .vault (ler_secret_id_do_arquivo).
5. Prompt: Senha Mestra (getpass).
6. Decriptar o cofre (decriptar_cofre) → lista de registros.
7. Montar o payload {"registros": [...]} com os 5 campos.
8. Se o arquivo de saída existir e não houver --force: pedir confirmação (s/N).
9. Escrever o JSON de forma atômica (UTF-8, indent=2, ensure_ascii=False).
10. Aplicar permissão 0600 ao arquivo final (best-effort).
11. Exibir relatório final (caminho de saída, total, avisos de round-trip).
```

Em nenhum momento o `.vault` é modificado.

---

## 6. Interface de linha de comando

```
Uso:
    python scripts/exportar_registros.py [SAIDA.json]
    python scripts/exportar_registros.py [SAIDA.json] --force
    python scripts/exportar_registros.py --help

Argumentos:
    SAIDA.json        Caminho do JSON de saída (opcional; se omitido, o script
                      pergunta no terminal). Aceita "~".

Opções:
    -h, --help        Mostra ajuda e encerra.
    -f, --force       Sobrescreve o arquivo de saída sem pedir confirmação.
```

As credenciais **não** são argumentos de linha de comando:

| Dado | Forma de obtenção |
|------|-------------------|
| Caminho do cofre | Prompt interativo (`input`) |
| Secret ID | Lido automaticamente do cabeçalho do `.vault` |
| Senha mestra | Prompt (`getpass.getpass`) — não aparece na tela |

---

## 7. Segurança

- ⚠️ **O JSON exportado contém as senhas em texto puro.** O script deve imprimir
  um alerta claro antes de gravar e no relatório final, orientando a guardar o
  arquivo com cuidado e apagá-lo após o uso.
- O arquivo é gravado com permissão **`0600`** (`chmod` best-effort; no Windows
  aplica o que for possível). A escrita é **atômica**: cria um temporário no mesmo
  diretório, aplica a permissão e só então `os.replace`, evitando arquivos
  parciais e janela de exposição.
- A senha mestra é lida com `getpass` e mantida **somente em memória** durante a
  execução.
- O script **não** grava a senha mestra, o Secret ID nem o conteúdo do cofre em
  logs ou arquivos temporários além do JSON de saída solicitado.
- O `.vault` é aberto somente para leitura; um backup **não** é necessário (nada
  é alterado no cofre).
- Em caso de erro durante a escrita, o arquivo temporário é removido e o arquivo
  de destino existente (se houver) permanece intacto.

---

## 8. Relatório final (exemplo)

```
=== Exportação — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo JSON .: /home/daniel/meu_cofre.json
Registros ....: 60
Exportados ...: 60

⚠️  ATENÇÃO: o arquivo contém senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.
```

Exemplo com registros que não sobreviveriam ao round-trip:

```
=== Exportação — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo JSON .: /home/daniel/meu_cofre.json
Registros ....: 60
Exportados ...: 60

⚠️  ATENÇÃO: o arquivo contém senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.

--- Avisos de round-trip (não serão reimportados) ---
[inválido] #12  motivo: 'senha' vazio
[inválido] #27  motivo: 'nome' vazio
```

**Códigos de saída:**

| Código | Significado |
|--------|-------------|
| `0` | Sucesso (inclusive cofre vazio, que gera `{"registros": []}`) |
| `1` | Erro de autenticação ou de leitura do cofre (não existe, Secret ID/senha incorretos, arquivo corrompido) |
| `2` | Erro ao escrever o JSON de saída (caminho inválido, sem permissão, não é diretório) |
| `130` | Cancelado pelo usuário (recusa em sobrescrever, ou Ctrl+C) |

---

## 9. Estrutura de código proposta

```
scripts/
  exportar_registros.py     # entrypoint CLI
```

Implementado como arquivo único, importando:

```python
from seguranca.encriptacao import decriptar_cofre, ler_secret_id_do_arquivo
from dados.armazenamento import buscar_registros  # (opcional; export usa a lista inteira)
```

Funções internas sugeridas:

| Função | Responsabilidade |
|--------|------------------|
| `montar_payload(registros) -> dict` | Converte a lista do cofre no objeto `{"registros": [...]}` com os 5 campos |
| `registros_invalidos_para_import(registros) -> list[tuple]` | Detecta itens que o import rejeitaria (índice + motivo) |
| `confirmar_sobrescrita(caminho, force) -> bool` | Pergunta s/N se o arquivo existir e não houver `--force` |
| `escrever_json_atomico(caminho, payload) -> None` | Temporário no mesmo diretório + `os.replace`, UTF-8, indent=2, `0600` |
| `imprimir_relatorio(...)` | Saída padronizada (ver §8) |
| `main(argv=None) -> int` | Orquestra o fluxo e devolve o código de saída |

Reaproveita, do import, o estilo de CLI (`argparse`), de relatório e de códigos
de saída, mantendo consistência entre as duas ferramentas.

---

## 10. Casos de teste previstos

1. Exportar cofre com 3 registros → JSON `{"registros": [...]}` com exatamente os
   5 campos por registro.
2. **Round-trip real:** exportar do cofre A, importar o JSON gerado em um cofre B
   vazio → 3 importados; `nome`, `login`, `senha`, `url`, `observacoes` idênticos.
3. Reimportar o mesmo JSON no **mesmo** cofre → todos pulados (duplicados),
   nenhuma alteração.
4. Senha mestra errada → código `1`, **nenhum** arquivo criado.
5. Cofre inexistente ou corrompido → código `1`, nenhum arquivo criado.
6. Cofre vazio → grava `{"registros": []}`, código `0`.
7. Arquivo de saída existente, sem `--force`, resposta "não" → código `130`,
   arquivo original intacto.
8. Arquivo de saída existente, com `--force` → sobrescrito, código `0`.
9. Caminho de saída em diretório inexistente / sem permissão → código `2`,
   cofre inalterado.
10. Campos com acentos e emoji (`ensure_ascii=False`, UTF-8) preservados e
    reimportáveis.
11. Senha com caracteres especiais (`\`, aspas, `\n`, unicode) preservada.
12. Permissão final do arquivo é `0600`.
13. Registro com campo obrigatório vazio → exportado e listado nos avisos de
    round-trip.
14. Nenhuma alteração no `.vault` (hash do arquivo idêntico antes/depois).
15. Secret ID lido corretamente do cabeçalho (sem prompt de Secret ID).

---

## 11. Critérios de aceite

- [ ] O JSON gerado é **100% importável** por `scripts/importar_registros.py`.
- [ ] Round-trip preserva `nome`, `login`, `senha`, `url` e `observacoes`.
- [ ] O `.vault` **nunca** é modificado (operação somente leitura).
- [ ] Senha mestra nunca é exposta em histórico do shell nem em disco.
- [ ] Arquivo de saída gravado com permissão `0600` (best-effort) e aviso de
      texto puro exibido.
- [ ] Escrita atômica: sem arquivos parciais em caso de erro.
- [ ] Confirmação antes de sobrescrever; `--force` disponível.
- [ ] Relatório final claro, com total e avisos de round-trip.
- [ ] Códigos de saída conforme §8.
- [ ] CRUD da GUI continua funcionando sem regressão (nenhum código compartilhado
      é alterado).

---

## 12. Pontos em aberto (para versões futuras)

1. **Exportação pela GUI** — botão "Exportar" na tela principal.
2. **Filtros de exportação** — por busca, seleção de cards ou tags.
3. **Flags extras** — `--stdout` (imprimir em vez de gravar) e `--indent N`.
4. **Export cifrado opcional** — ex.: `--encrypt` com uma passphrase própria,
   para backups em texto sem trafegar senhas em claro.
5. **Preservar `id`/datas** — exigiria mudar o import para aceitar/opcionalmente
   respeitar esses campos; hoje fora de escopo.
