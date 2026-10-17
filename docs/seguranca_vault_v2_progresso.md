# Progresso — Implementação do cofre V2

Plano completo: `docs/seguranca_vault_v2.md`.
Objetivo: retomar rapidamente em caso de interrupção.

## Status atual

- [x] Etapa 0 — Fixture v1 criada em `/tmp/cofre_v1_test.vault`
      (SID `a` x 32, senha `senha-teste`, 1 registro).
- [x] Etapa 1 — Núcleo: formato v2 + escrita atômica em
      `seguranca/encriptacao.py`. Testado v2, v1, SID/senha errados, versão
      futura e arquivo truncado.
- [x] Etapa 2 — `dados/cache.py:buscar_secret_id` + scripts de exportação
      (JSON/PDF) usando cache ou prompt.
- [x] Etapa 3 — Migração automática no login em `ui/tela_autenticacao.py` +
      mensagem unificada de autenticação.
- [x] Etapa 4 — Documentação: `README.md`, `AGENTS.md`, `docs/exportacao_*`,
      `scripts/README_exportar_*` e checklist do plano atualizados.
- [x] Etapa 5 — Validação completa (ver seção Testes executados).
- [x] Etapa 6 — Conclusão. Implementação finalizada em 2026-10-17.

## Testes executados

- `py_compile` em todos os módulos: OK.
- Criação/abertura v2: OK; magic `VAULTv2`, SID ausente, permissão `600`.
- Abertura v1 legado: OK; SID e senha corretos.
- SID errado e senha errada: erro unificado esperado.
- Magic desconhecido e arquivo truncado: mensagens esperadas.
- Migração v1 → v2 no login (`_autenticar`): registros preservados e SID ausente.
- Escrita atômica com diretório sem permissão: original intacto, sem temporário.
- `buscar_secret_id`: caminho exato, normalizado (`..`) e ausente.
- Scripts JSON/PDF: SID via cache e fallback por prompt; exportação OK.
- `strings` no `.vault` v2: Secret ID não encontrado.
- Smoke headless: `TelaInicial`, `TelaAutenticacao`, `TelaPrincipal` OK.

## Release

- Versão 2.0.0 publicada em 2026-10-17.
- Tag: `v2.0.0`.
- Release: https://github.com/danielexpe/cofre-senhas/releases/tag/v2.0.0
- Artefatos: AppImage, `SHA256SUMS`, `SHA256SUMS.asc` e `DANIEL-PUBKEY.asc`.
- Notas: `release/v2.0.0/RELEASE_NOTES.md`.
- Sem pendências de implementação.

## Decisões firmadas

- Migração v1 → v2 automática no login bem-sucedido.
- Secret ID continua no cache local (risco aceito); nunca no `.vault`.
- Layout v2: `[VAULTv2][salt 16][salt2 32][Fernet]`, KDF usa `salt + salt2`.

## Arquivos alterados

- `seguranca/encriptacao.py`
- `dados/cache.py`
- `scripts/exportar_registros.py`
- `scripts/exportar_pdf.py`
- `ui/tela_autenticacao.py`
- `README.md`, `AGENTS.md`
- `docs/seguranca_vault_v2.md`, `docs/seguranca_vault_v2_progresso.md`
- `docs/exportacao_registros.md`, `docs/exportacao_pdf.md`,
  `docs/exportacao_registros_exemplos.md`
- `scripts/README_exportar_registros.md`, `scripts/README_exportar_pdf.md`

## Retomada rápida

Se interromper, ler esta página, conferir `git status`/`git diff` e rodar:

```bash
python -m py_compile main.py ui/*.py seguranca/*.py dados/*.py scripts/*.py servicos/*.py utils/*.py
```

A implementação está completa; resta apenas decisão de release (versão/build).
