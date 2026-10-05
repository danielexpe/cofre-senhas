# Especificação — Integração GUI: Exportar/Importar JSON e Exportar PDF

> Levar para a **interface gráfica** as três funcionalidades já disponíveis via
> CLI — exportar JSON, importar JSON e gerar relatório PDF — por meio de **três
> botões no cabeçalho da tela principal do cofre**, reaproveitando a lógica por
> trás dos scripts (refatorada para um pacote compartilhado).

Versão do documento: 0.1
Autor: Daniel
Status: **Aprovada e implementada**

Documentos relacionados:
- [Exportação de registros (JSON)](./exportacao_registros.md)
- [Importação Massiva](./importacao_massiva.md)
- [Exportação em PDF](./exportacao_pdf.md)

---

## 1. Objetivo

Permitir que o usuário, já autenticado e dentro de um cofre, execute as três
operações sem sair da interface: **⬆️ Exportar JSON**, **⬇️ Importar JSON** e
**📄 Exportar PDF**. Como o cofre já está aberto, o `.vault` e os registros estão
em memória — não é preciso redigitar a senha mestra nem escolher o cofre.

Para não duplicar regra de negócio, o núcleo lógico dos scripts CLI é extraído
para o pacote `servicos/`, e tanto os scripts quanto a GUI passam a usá-lo.

## 2. Fora de escopo

- Alterar o formato dos arquivos JSON/PDF (permanecem idênticos aos do CLI).
- Novas funcionalidades além das três (ex.: exportar para outros formatos).
- Refatorar o restante da GUI (autenticação, cadastro, cache).
- Operações em lote sobre vários cofres ao mesmo tempo.
- Cifrar o JSON exportado (continua texto puro, com aviso).

---

## 3. Decisões de projeto

| Tema | Decisão |
|------|---------|
| Reuso | **Refatorar o núcleo para o pacote `servicos/`**; scripts e GUI viram camadas finas |
| Fonte de dados (export) | **Registros em memória** (`self.registros`) — sem reler o `.vault` |
| Importação | **Mesclar com dedup** (`nome`+`login`), igual ao CLI |
| Backup no import | **Automático** (`.vault.<timestamp>.bak`) antes de gravar |
| Re-autenticação | **Não** pedir a senha mestra (sessão já autenticada) |
| Resumo antes de importar | **Sim** — diálogo com contagens + confirmação |
| Relatório final | **Diálogo detalhado** (contagens e lista de pulados/inválidos) |
| Execução | **Thread de fundo + indicador de progresso** (Tk só na thread principal) |
| Botões | **Três botões com rótulo** no cabeçalho |
| Senha do PDF | **Diálogo**; vazio = gera sem cifra (com aviso), igual ao CLI |
| Cifra do JSON | Sem cifra; diálogo de aviso de **texto puro** antes de gravar |
| Compatibilidade | JSON/PDF gerados pela GUI são **idênticos** aos do CLI |

---

## 4. Arquitetura e refatoração

### 4.1 Novo pacote `servicos/`

O código de negócio sai dos scripts e vai para um pacote importável pela GUI:

```
servicos/
  __init__.py
  arquivos.py          # backup + escrita atômica
  importacao.py        # parse, validação, dedup, planejamento
  exportacao_json.py   # payload e escrita do JSON
  exportacao_pdf.py    # geração do relatório PDF
```

### 4.2 Funções públicas (sem prompts, sem I/O de terminal)

`servicos/importacao.py`

| Função | Descrição |
|--------|-----------|
| `carregar_json(caminho) -> list` | Lê/normaliza formatos A/B |
| `normalizar(item) -> (registro \| None, motivo \| None)` | Valida um item |
| `chave_duplicidade(registro) -> str` | `"nome\|login"` normalizado |
| `planejar_importacao(existentes, itens) -> ResultadoImportacao` | Separa importáveis/pulados/inválidos/repetidos e campos extras |

`ResultadoImportacao` (dataclass): `importaveis`, `duplicados`, `repetidos`,
`invalidos`, `campos_extras`, `total_lidos`.

`servicos/exportacao_json.py`

| Função | Descrição |
|--------|-----------|
| `montar_payload(registros) -> dict` | `{"registros": [...]}` com os 5 campos |
| `registros_invalidos_para_import(payload) -> list` | Itens que o import rejeitaria |
| `escrever_json_atomico(caminho, payload) -> str` | Grava UTF-8/indent=2/`0600` |

`servicos/exportacao_pdf.py`

| Função | Descrição |
|--------|-----------|
| `gerar_pdf(caminho, registros, nome_cofre, senha_pdf) -> str` | Gera o PDF (AES se `senha_pdf`) |
| `registrar_fontes()` etc. | Helpers internos de layout/fontes |

`servicos/arquivos.py`

| Função | Descrição |
|--------|-----------|
| `fazer_backup(caminho) -> str` | Copia o `.vault` com timestamp |

### 4.3 Scripts CLI viram wrappers finos

`scripts/importar_registros.py`, `scripts/exportar_registros.py` e
`scripts/exportar_pdf.py` mantêm **exatamente** a CLI atual (argumentos,
prompts, relatórios e códigos de saída), mas delegam a regra de negócio para
`servicos/`. Nenhuma mudança de comportamento observável.

### 4.4 Garantia de compatibilidade

Porque GUI e CLI chamam as mesmas funções, o JSON exportado pela GUI é
reimportável pelo CLI (e vice-versa) e o PDF é idêntico em formato. Os testes de
round-trip existentes continuam valendo.

---

## 5. Interface gráfica

### 5.1 Cabeçalho (`tela_principal`)

Adicionar três botões ao `topo`, à esquerda dos já existentes:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🔐 meu_cofre.vault   [⬆️ Exportar JSON] [⬇️ Importar JSON] [📄 Exportar PDF]   │
│                                          [➕ Novo Registro] [🚪 Sair]          │
└──────────────────────────────────────────────────────────────────────────────┘
```

- Rótulos: **⬆️ Exportar JSON**, **⬇️ Importar JSON**, **📄 Exportar PDF**.
- Cada botão chama o respectivo método da `TelaPrincipal`.

### 5.2 Estados dos botões

- Durante uma operação em andamento, os três botões (e "Novo Registro") ficam
  **desabilitados** (`state="disabled"`) para evitar reentrância.
- Ao terminar (sucesso ou erro), voltam a `normal`.

---

## 6. Diálogos

| Diálogo | Tipo | Uso |
|---------|------|-----|
| Seleção de arquivo | Nativo (`filedialog`) | Escolher JSON de entrada / destino JSON/PDF |
| Senha do PDF | Customizado (`CTkToplevel`) | Senha de abertura do PDF (opcional) |
| Resumo da importação | Customizado | Contagens + confirmar/cancelar |
| Relatório final | Customizado | Resultado detalhado da operação |
| Progresso | Customizado | Indicador indeterminado durante a thread |

### 6.1 Diálogo de senha do PDF

```
┌───────────────────────────────────────────┐
│  🔒 Senha de abertura do PDF              │
│                                           │
│  Deixe em branco para gerar SEM cifra.    │
│  ┌─────────────────────────────┐  [👁️]    │
│  │ •••••••••                   │          │
│  └─────────────────────────────┘          │
│                                           │
│            [Cancelar]   [Continuar]       │
└───────────────────────────────────────────┘
```

- Reutiliza o padrão do `FormularioRegistro` (modal, centralizado, `grab_set`).
- Campo com `show="•"` e botão 👁️ para revelar.
- Vazio = sem cifra (com aviso no relatório final).

### 6.2 Diálogo de resumo da importação

Mostra, antes de gravar:

```
Arquivo: registros.json
Itens lidos: 42

  ✓ A importar ........: 35
  ↷ Pulados (existente): 3
  ↷ Pulados (repetido) : 1
  ✗ Inválidos ..........: 3

Backup será criado antes de gravar.

            [Cancelar]   [Importar]
```

### 6.3 Diálogo de relatório final

- Exportação JSON/PDF: caminho, total, avisos (texto puro; cifrado ou não;
  registros vazios que não sobreviveriam ao round-trip).
- Importação: contagens e, se houver, lista de itens pulados/inválidos/repetidos.
- Botão **Fechar** (e, quando fizer sentido, **Abrir pasta** — opcional futuro).

### 6.4 Diálogo de progresso

- `CTkToplevel` pequeno, modal, com `CTkProgressBar` em modo **indeterminado** e
  texto ("Gerando PDF…", "Importando…").
- Abre antes de iniciar a thread e fecha ao concluir.

---

## 7. Fluxos

### 7.1 ⬆️ Exportar JSON

```
1. filedialog.asksaveasfilename(defaultextension=".json",
     initialfile="<cofre>.json", initialdir=<pasta do cofre>,
     filetypes=[("JSON", "*.json")])
   → se cancelado, encerra.
2. Diálogo de aviso: "O arquivo conterá senhas em texto puro. Continuar?"
3. payload = servicos.exportacao_json.montar_payload(self.registros)
4. Em thread: servicos.exportacao_json.escrever_json_atomico(caminho, payload)
5. Relatório final: caminho, total exportado, avisos de round-trip + texto puro.
```

### 7.2 ⬇️ Importar JSON

```
1. filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
   → se cancelado, encerra.
2. Em thread: itens = carregar_json(caminho)
              resultado = planejar_importacao(self.registros, itens)
3. Diálogo de resumo com as contagens → Cancelar ou Importar.
4. Se importar:
   a. backup = servicos.arquivos.fazer_backup(self.caminho)
   b. self.registros += resultado.importaveis
   c. encriptar_cofre(self.caminho, self.secret_id, self.senha, self.registros)
   d. self._renderizar_lista() + atualizar status
5. Relatório final (contagens + não importados).
```

Observações:

- A importação **não** altera o comportamento de dedup (pula `nome`+`login` já
  existente e repetidos dentro do próprio arquivo).
- Como já estamos autenticados, usa-se `self.secret_id`/`self.senha` da sessão.

### 7.3 📄 Exportar PDF

```
1. filedialog.asksaveasfilename(defaultextension=".pdf",
     initialfile="<cofre>.pdf", initialdir=<pasta do cofre>,
     filetypes=[("PDF", "*.pdf")])
   → se cancelado, encerra.
2. Diálogo de senha do PDF (vazio = sem cifra) → se cancelado, encerra.
3. Em thread:
   servicos.exportacao_pdf.gerar_pdf(caminho, ordenar_registros(self.registros),
                                     os.path.basename(self.caminho), senha_pdf)
4. Relatório final: caminho, total, cifrado? e aviso de texto puro.
```

---

## 8. Concorrência e threading

- A interface Tk **só é tocada na thread principal**. O trabalho pesado
  (PBKDF2, geração do PDF, escrita) roda em uma **thread `daemon`**.
- Resultado/erro são entregues à thread principal via `self.master.after(0, cb, ...)`.
- Helper proposto em `ui/tela_principal.py` (ou `ui/async_util.py`):

```python
def _executar_em_thread(self, trabalho, ao_sucesso, ao_erro):
    # mostra diálogo de progresso; desabilita botões
    def runner():
        try:
            resultado = trabalho()
        except Exception as e:
            self.master.after(0, lambda: self._finalizar(erro=e))
        else:
            self.master.after(0, lambda: self._finalizar(resultado=resultado))
    threading.Thread(target=runner, daemon=True).start()
```

- Nenhum widget é acessado de dentro da thread; apenas dados (listas/dicts).

---

## 9. Segurança

- **Não** pede a senha mestra de novo (sessão já autenticada); usa
  `self.senha`/`self.secret_id` apenas em memória.
- Exportação JSON: aviso explícito de **texto puro**; arquivo gravado com
  permissão `0600` (escrita atômica).
- Exportação PDF: senha de abertura opcional (AES); sem senha, aviso destacado.
- Importação: **backup automático** do `.vault` antes de gravar; a gravação
  reutiliza `encriptar_cofre` (mesmo esquema PBKDF2 + AES/Fernet + SHA512).
- Erros não expõem senhas; mensagens apenas informam o que falhou.

---

## 10. Erros e mensagens

| Situação | Mensagem |
|----------|----------|
| JSON inválido/inexistente | `messagebox.showerror` com o motivo |
| Nada a importar | Relatório informando que não houve alterações |
| Falha ao gravar o cofre | `showerror` + cofre original preservado (backup existe) |
| Falha ao gerar PDF/JSON | `showerror` com o motivo |
| Operação cancelada | Simplesmente encerra, sem mensagens de erro |

---

## 11. Estrutura de código proposta

```
servicos/
  __init__.py
  arquivos.py            # fazer_backup
  importacao.py          # carregar_json, normalizar, chave_duplicidade,
                         # planejar_importacao, ResultadoImportacao
  exportacao_json.py     # montar_payload, registros_invalidos_para_import,
                         # escrever_json_atomico
  exportacao_pdf.py      # gerar_pdf + helpers
ui/
  tela_principal.py      # +3 botões e os 3 fluxos
  dialogos_exportacao.py # DialogoSenhaPDF, DialogoResumoImportacao,
                         # DialogoRelatorio, DialogoProgresso
scripts/
  importar_registros.py  # wrapper fino (usa servicos.importacao)
  exportar_registros.py  # wrapper fino (usa servicos.exportacao_json)
  exportar_pdf.py        # wrapper fino (usa servicos.exportacao_pdf)
```

Métodos novos em `TelaPrincipal`: `_exportar_json`, `_importar_json`,
`_exportar_pdf`, `_executar_em_thread`, `_definir_botoes_habilitados`.

---

## 12. Casos de teste previstos

1. Exportar JSON pela GUI → arquivo idêntico (formato) ao do CLI; reimportável.
2. Exportar PDF pela GUI (com e sem senha) → arquivo abre/precisa de senha
   conforme escolhido.
3. Importar JSON de um lote válido → resumo correto, registros adicionados e
   lista atualizada na tela.
4. Importar JSON com duplicados/repetidos/inválidos → contagens e pulos corretos.
5. Importar cria backup `.bak` do `.vault` antes de gravar.
6. Cancelar em cada diálogo (arquivo, senha, resumo) → nenhuma alteração.
7. JSON inválido → erro, cofre intacto.
8. Operação longa (muitos registros / PDF grande) → UI continua responsiva
   (thread) e botões reabilitados ao final.
9. Falha simulada na gravação → erro exibido e cofre original preservado.
10. Sessão já autenticada → nenhuma das três ações pede a senha mestra.
11. Compatibilidade cruzada: JSON exportado na GUI importado no CLI e vice-versa.
12. CRUD da GUI (novo/editar/excluir) continua funcionando sem regressão.

---

## 13. Critérios de aceite

- [ ] Três botões no cabeçalho da tela principal, com os rótulos definidos.
- [ ] Exportar JSON/PDF e Importar JSON funcionando pela GUI, sem terminal.
- [ ] Núcleo compartilhado em `servicos/`, sem duplicar regra de negócio.
- [ ] Formatos 100% compatíveis com os scripts CLI.
- [ ] Importação mescla com dedup e cria backup antes de gravar.
- [ ] Diálogos de arquivo/senha/resumo/relatório/progresso conforme §6.
- [ ] Operações pesadas em thread, interface responsiva, botões desabilitados
      durante a execução.
- [ ] Nenhuma das ações pede a senha mestra (sessão já autenticada).
- [ ] Sem regressão nas funcionalidades atuais.
- [ ] Scripts CLI permanecem com comportamento idêntico ao atual.

---

## 14. Pontos em aberto (versões futuras)

1. Botão "Abrir pasta/arquivo" no relatório final.
2. Filtro de exportação por busca/seleção de registros.
3. Marcar/desmarcar registros para exportação parcial.
4. Barra de progresso determinada (percentual) para lotes grandes.
5. Atalhos de teclado e menu de contexto para as três ações.
6. Exportação direta para a área de transferência (JSON).
