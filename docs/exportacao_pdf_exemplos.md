# Exportação em PDF — Exemplos e Modelos

Documento complementar à [especificação](./exportacao_pdf.md).

> O relatório é gerado para **impressão**, em A4, com capa, cards por registro e
> rodapé com numeração. As senhas são sempre exibidas em texto puro; o PDF pode
> ser cifrado com uma senha de abertura.

---

## 1. Modelo da capa

```
                     ┌───────────────────────┐
                     │        [ LOGO ]        │
                     └───────────────────────┘

                    RELATÓRIO DE CREDENCIAIS

                    Cofre: meu_cofre.vault
                    Gerado em: 05/10/2026 01:30
                    Registros: 42

             ─────────────────────────────────────

             ⚠  Documento confidencial.
                Contém credenciais de acesso.
                [ Cifrado com AES ]     (ou)
                [ SEM PROTEÇÃO — texto puro ]
```

---

## 2. Modelo de um card de registro

Cada registro vira um bloco numerado, mantido inteiro na mesma página sempre que
possível:

```
┌──────────────────────────────────────────────────────────────┐
│▌ Card 01                                                       │
│▌ Banco Ação 🏦 → "Banco Ação"                                  │
│                                                               │
│▌   Login:  josé.silva@exemplo.com                              │
│▌   Senha:  S3nh@ "quotes" \barra\ e nova linha                 │
│▌   URL:    https://banco.exemplo.com                           │
│▌   Obs.:   chave PIX: josé@exemplo.com — atenção à acentuação   │
└──────────────────────────────────────────────────────────────┘
```

- A barra azul à esquerda (`▌`) é a cor primária `#2b6cb0`.
- `Senha` sai em fonte **monoespaçada**.
- `URL` em azul; `Observações` em cinza.
- Campos vazios aparecem como `—`.

---

## 3. Modelo de página (a partir da 2ª)

```
 me u_cofre.vault                    Relatório de Credenciais
 ─────────────────────────────────────────────────────────────

   Card 01  ...
   Card 02  ...
   Card 03  ...

 ─────────────────────────────────────────────────────────────
 05/10/2026 01:30                              Página 2 de 5
```

---

## 4. Execução com senha de abertura (PDF cifrado)

```bash
python scripts/exportar_pdf.py ~/meu_cofre.pdf
```

Sessão:

```
Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Senha Mestra: (a digitação não aparece)
Senha de abertura do PDF (vazio = sem cifra): (a digitação não aparece)

=== Exportação PDF — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo PDF ..: /home/daniel/meu_cofre.pdf
Registros ....: 42
Cifrado ......: sim (AES)

⚠️  O PDF contém senhas em TEXTO PURO. A proteção é a senha de abertura.
    Guarde o arquivo e a senha com cuidado. Não há recuperação da senha.
```

---

## 5. Execução sem cifra (senha vazia)

Pressionar **Enter** no prompt da senha do PDF gera o arquivo **sem cifra**, com
aviso destacado:

```
Caminho do cofre (.vault): /home/daniel/meu_cofre.vault
Senha Mestra: (a digitação não aparece)
Senha de abertura do PDF (vazio = sem cifra):

=== Exportação PDF — Cofre de Senhas ===

Cofre ........: /home/daniel/meu_cofre.vault
Arquivo PDF ..: /home/daniel/meu_cofre.pdf
Registros ....: 42
Cifrado ......: NÃO

⚠️  ATENÇÃO: PDF SEM CIFRA, contendo senhas em TEXTO PURO.
    Guarde-o com segurança e apague-o após o uso.
```

---

## 6. Arquivo de saída já existente

Sem `--force`:

```
O arquivo /home/daniel/meu_cofre.pdf já existe. Sobrescrever? [s/N]:
```

- `s` → sobrescreve.
- Qualquer outra resposta → aborta com código `130`, sem tocar no arquivo.

Para automação:

```bash
python scripts/exportar_pdf.py ~/meu_cofre.pdf --force
```

---

## 7. Cofre vazio

Gera um PDF de uma página com a capa e a mensagem no corpo:

```
                    RELATÓRIO DE CREDENCIAIS
                    Cofre: meu_cofre.vault
                    Registros: 0

           ─────────────────────────────────────
              Nenhum registro encontrado.
```

Código de saída `0`.

---

## 8. Textos longos e especiais

- **Acentos** são preservados: `José`, `Ação`, `coração`.
- **Emojis** são removidos: `Banco 🏦` vira `Banco`.
- **Senhas/URLs longas sem espaço** quebram em múltiplas linhas dentro do card,
  sem estourar a largura da página.
- Exemplo de senha com caracteres especiais:

```
   Senha:  S3nh@ "quotes" \barra\ e
           nova linha
```

---

## 9. Uso em automação

```bash
#!/usr/bin/env bash
set -euo pipefail

COFRE="/home/daniel/meu_cofre.vault"
PDF="/home/daniel/meu_cofre_$(date +%Y%m%d).pdf"

# Senha mestra e senha do PDF serão pedidas no terminal
python scripts/exportar_pdf.py "$PDF" --force

echo "PDF gerado em $PDF"
```

> As senhas **não** podem ser passadas por argumento (nem aparecem no histórico
> do shell); são sempre digitadas no prompt.

---

## 10. Dicas

- Imprima o relatório apenas quando necessário e **recolha/descarte** com
  segurança — o papel contém as senhas.
- Use sempre uma **senha de abertura** se for guardar o PDF em disco ou enviá-lo.
- Se esquecer a senha do PDF, não há recuperação — assim como a senha mestra.
- Para backup/migração de dados, prefira o
  [export em JSON](./exportacao_registros.md); o PDF é para leitura/impressão.
