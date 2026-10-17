# AGENTS.md — Guia de Desenvolvimento

Guia de referência para dar continuidade ao projeto **Cofre de Senhas** (v1.5.0). Leia antes de mexer no código.

## Visão geral

Gerenciador de senhas desktop, 100% local, em Python + **CustomTkinter**. Tema escuro, interface em **pt-BR**, criptografia AES + SHA512 + PBKDF2. Nenhuma informação trafega pela internet.

## Como rodar

```bash
source .venv/bin/activate   # Python 3.15 (ver .python-version)
python main.py              # ou: py main.py
```

Não há suíte de testes automatizada. Valide com:

```bash
python -m py_compile main.py ui/*.py
```

E, quando necessário, smoke tests headless (criar `ctk.CTk()`, instanciar a tela, `update()`, destruir) — o ambiente tem `DISPLAY` disponível.

## Estrutura

| Pasta/Arquivo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada; tema escuro, janela 700x600, minsize 700x450 |
| `ui/tela_inicial.py` | Tela de cofres recentes (lista de `.vault`) |
| `ui/tela_novo_cofre.py` | Criação de novo cofre |
| `ui/tela_autenticacao.py` | Login (Secret ID + Senha Mestra) |
| `ui/tela_principal.py` | Lista de secrets/registros de um cofre aberto |
| `ui/formulario_registro.py` | Formulário criar/editar registro (CTkToplevel) |
| `ui/dialogos_exportacao.py` | Diálogos de progresso/relatório/importação/PDF |
| `ui/tooltip.py` | `Tooltip` (label flutuante em botões de ícone) |
| `dados/cache.py` | Histórico de cofres recentes (`~/.cofre_cache.json`) |
| `dados/armazenamento.py` | Modelo de registro + `buscar_registros` |
| `seguranca/encriptacao.py` | `encriptar_cofre` / `decriptar_cofre` / `gerar_secret_id` |
| `servicos/` | Exportação JSON/PDF, importação, backup |
| `utils/helpers.py` | Senha aleatória, força, clipboard |
| `docs/` | Especificações (ver `melhoria_layout_01.md` e `_02.md`) |

## Convenções de código

- **Idioma**: textos da UI sempre em **pt-BR**.
- **Comentários**: só quando realmente necessários (o código é autoexplicativo).
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`), mensagens em pt-BR.
- **Navegação entre telas**: cada tela faz `_limpar()` (destroi filhos de `master`) e `_construir()`. As telas são instanciadas passando `self.master` (a `CTk` raiz), não criam janelas novas.
- **Regras de negócio intocáveis**: encriptação, cache, histórico, persistência e a pasta `seguranca/`.

## Identidade visual (tema escuro)

| Item | Valor |
|---|---|
| Fundo da janela | cinza-escuro (padrão CustomTkinter dark) |
| Card | `#2d2d2d` |
| Card hover | `#3a3a3a` |
| Texto secundário | `#9ca3af` |
| Acento azul (links/datas) | `#60a5fa` |
| Botão azul | tema `blue`; variante `#2b6cb0` (hover `#2c5282`) |
| Verde (copiar) | `#16a085` |
| Âmbar (editar) | `#d68910` |
| Vermelho (excluir/sair) | `#c0392b` (hover `#922b21`) |

Fontes (referência do estado atual): título 24 bold, subtítulo 12 cinza, cabeçalho de seção 17 bold, nome de card 14 bold, texto de apoio 12, rodapé 10–12.

## Padrões de UI consolidados (das melhorias de layout)

1. **Cabeçalho em uma linha**: título + subtítulo à esquerda, botões compactos à direita (ver `tela_inicial.py` e `tela_principal.py`).
2. **Cards de 2 linhas**: `corner_radius=8`, hover (`#3a3a3a`) + cursor de mão, textos longos truncados com reticências.
3. **Botões só de ícone** sempre acompanhados de `Tooltip` (`ui/tooltip.py`) — ex.: exportar/importar/PDF e copiar/editar/excluir.
4. **Barra de rolagem condicional**: exibir apenas com mais de 5 itens (cofre ou registro).
5. **Lista virtualizada** em `tela_principal.py` (canvas + pool de cards) — preservar para desempenho.
6. **Nome de arquivo `.vault`** exibido sem a extensão na primeira linha (o caminho completo fica na segunda/ subtítulo).

## Referências úteis

- `docs/melhoria_layout_01.md` — briefing da tela inicial (já implementado).
- `docs/melhoria_layout_02.md` — briefing da tela de secrets (já implementado).
- `docs/integracao_gui.md`, `docs/exportacao_*.md`, `docs/importacao_*.md` — exportação/importação.
