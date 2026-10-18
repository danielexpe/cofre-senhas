# 🔐 Cofre de Senhas

> Gerenciador de senhas desktop, 100% local e open-source, com criptografia forte e interface gráfica moderna.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-active-success)

**Atalhos:** [Para usuários](#-para-usuários) · [Segurança](#-segurança) · [Downloads](#-downloads-e-verificação) · [Para desenvolvedores](#-para-desenvolvedores)

---

## 📖 Visão geral

O **Cofre de Senhas** armazena credenciais localmente em arquivos `.vault` criptografados. Nenhum dado é enviado para a internet e não há conta, nuvem ou telemetria.

### ✨ Destaques

- 🔒 **Criptografia forte** — AES (Fernet) + SHA512 + PBKDF2.
- 🏠 **100% local** — arquivos `.vault` na sua máquina, sem conta, nuvem ou telemetria.
- 🔑 **Autenticação dupla** — Secret ID + Senha Mestra.
- 🆕 **Formato de cofre v2** — o Secret ID não é gravado no `.vault`; cofres v1 são migrados automaticamente no login.
- 💾 **Múltiplos cofres** — separe senhas pessoais, do trabalho etc.
- 🚀 **Acesso rápido** — cache local de cofres recentes.
- 🎨 **Interface moderna** — GUI em pt-BR com CustomTkinter.
- 📤 **Exportação e importação** — JSON e PDF pela interface, com scripts para importação em massa.

---

## 🚀 Para usuários

### Windows — baixar e usar (`.exe`)

1. Acesse a página de [Releases](https://github.com/danielexpe/cofre-senhas/releases) e abra a versão mais recente (atualmente `v2.0.0`).
2. Baixe o arquivo **`CofreSenhas.exe`**.
3. Execute o arquivo. Ele é portátil: **não precisa instalar Python** nem dependências.

Observações:

- Se a release atual ainda não tiver um `.exe` anexado, gere o seu localmente seguindo [Gerar o `.exe` no Windows](#gerar-o-exe-no-windows).
- Se o Windows/SmartScreen exibir um aviso, confirme que o download veio da release oficial. Se quiser, valide o hash antes de executar (veja [Downloads e verificação](#-downloads-e-verificação)).
- Alvo: Windows 10/11 (64 bits).

### Linux — AppImage (sem instalação)

1. Baixe `CofreDeSenhas-2.0.0-x86_64.AppImage` na página de [Releases](https://github.com/danielexpe/cofre-senhas/releases) (versão `v2.0.0`).
2. Dê permissão de execução e abra:

```bash
chmod +x CofreDeSenhas-2.0.0-x86_64.AppImage
./CofreDeSenhas-2.0.0-x86_64.AppImage
```

Também é possível abrir com **dois cliques**. Se o AppImage não iniciar por falta de FUSE, use:

```bash
./CofreDeSenhas-2.0.0-x86_64.AppImage --appimage-extract-and-run
```

### macOS

Não há artefato pronto para download. Use o código-fonte ou gere um `.app` conforme [Gerar `.app` no macOS](#gerar-app-no-macos).

---

## 🎯 Primeiros passos

### Criar um cofre

1. Abra o aplicativo.
2. Clique em **➕ Novo**.
3. Defina:
   - 📁 **Local do arquivo** — onde o `.vault` será salvo.
   - 🔑 **Secret ID** — gerado automaticamente; copie e guarde em local seguro.
   - 🔑 **Senha Mestra** — forte, com letras, números e símbolos.
4. Confirme. O cofre já é criado criptografado.

### Abrir um cofre existente

1. Selecione um cofre nos **cards recentes** ou use **📂 Abrir**.
2. Informe o **Secret ID** (quando solicitado) e a **Senha Mestra**.
3. Gerencie os registros: adicionar, editar, copiar e excluir.

### Onde ficam os dados

- **Cofre**: no caminho `.vault` escolhido por você.
- **Cache de recentes**: `~/.cofre_cache.json` (Linux/macOS) ou `%USERPROFILE%\.cofre_cache.json` (Windows). Ele guarda caminhos e Secret IDs por conveniência.
- **Backups**: faça cópias periódicas dos arquivos `.vault` e guarde o Secret ID separadamente.

> ℹ️ Cofres convertidos para o formato **v2** não podem ser abertos por versões antigas do aplicativo.

---

## 🔐 Segurança

### Como funciona a criptografia

1. **Secret ID** + **Senha Mestra** passam por **PBKDF2** com salt aleatório.
2. A chave derivada criptografa o conteúdo do cofre via **AES (Fernet)**.
3. A integridade é validada com **SHA512**.
4. O **Secret ID nunca é gravado no `.vault`** (formato v2).

### Princípios adotados

- ✅ A Senha Mestra **nunca** é armazenada, nem em cache nem em arquivo.
- ✅ Cada cofre possui seu próprio salt único.
- ✅ O Secret ID não é gravado nos arquivos `.vault`.
- ✅ O cache local guarda caminhos e Secret IDs por conveniência; esse risco é assumido pelo usuário.
- ✅ Referências a cofres inexistentes são removidas automaticamente do cache.

> ⚠️ **Aviso importante**: se você esquecer a Senha Mestra ou o Secret ID, **não há recuperação**. Faça backups dos `.vault` e guarde o Secret ID em local seguro.

---

## ⬇️ Downloads e verificação

### Artefatos da release

| Plataforma | Arquivo | Observação |
|---|---|---|
| Windows | `CofreSenhas.exe` | Portátil; disponível quando anexado à release |
| Linux | `CofreDeSenhas-2.0.0-x86_64.AppImage` | Portátil, sem instalação |
| Todos | `SHA256SUMS` | Hashes SHA-256 dos artefatos |
| Todos | `SHA256SUMS.asc` | Assinatura GPG dos checksums |
| Todos | `DANIEL-PUBKEY.asc` | Chave pública GPG do autor |

Fingerprint GPG do autor: `D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`
(Chave: `D7E190A826A982E501B7469FF7E956C837ABD08F`)

### Verificar no Linux/macOS

```bash
# Ajuste o nome do arquivo baixado
APP="CofreDeSenhas-2.0.0-x86_64.AppImage"

# 1) Importar a chave pública do autor
gpg --import DANIEL-PUBKEY.asc

# 2) Verificar a assinatura dos checksums
gpg --verify SHA256SUMS.asc SHA256SUMS

# 3) Conferir o hash do artefato
sha256sum "$APP"

# 4) Opcional: verificar a assinatura PGP embutida no AppImage
./"$APP" --appimage-signature | head -n 20
```

### Verificar no Windows (PowerShell)

```powershell
# Hash do arquivo baixado
Get-FileHash .\CofreSenhas.exe -Algorithm SHA256

# Opcional: se tiver GPG instalado, valide os checksums
gpg --import DANIEL-PUBKEY.asc
gpg --verify SHA256SUMS.asc SHA256SUMS
```

Compare o hash exibido com a linha correspondente em `SHA256SUMS`.

---

## 🧑‍💻 Para desenvolvedores

### Pré-requisitos

- **Python 3.10+** (recomendado 3.12+).
- **pip** e **git**.
- **tkinter** (normalmente incluso no Python; em algumas distribuições Linux é um pacote separado).
- **Windows** apenas para gerar o `.exe` (PyInstaller não faz cross-compile confiável).

### Executar a partir do código-fonte

#### Windows — PowerShell ou Prompt de Comando

```powershell
git clone https://github.com/danielexpe/cofre-senhas.git
cd cofre-senhas

py -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python main.py
```

#### Linux/macOS

```bash
git clone https://github.com/danielexpe/cofre-senhas.git
cd cofre-senhas

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python main.py
```

### Gerar o `.exe` no Windows

Execute **no Windows**, com o ambiente virtual ativado:

```powershell
py -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --name CofreSenhas --onefile --windowed --icon=assets/icone.ico --add-data "assets;assets" --collect-all customtkinter main.py
```

O executável será criado em:

```text
dist\CofreSenhas.exe
```

Notas:

- No Windows, o separador do `--add-data` é **`;`**. Em Linux/macOS é **`:`**.
- Mantenha a pasta `assets/` no projeto: fontes e ícones são necessários para a interface e para o PDF.
- Para distribuir, envie apenas `dist\CofreSenhas.exe` (o `--onefile` já embute as dependências).
- Se o `.exe` for anexado a uma release, ele deve ser gerado em Windows e validado antes da publicação.

### Gerar o AppImage no Linux

```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

O script usa PyInstaller + `appimagetool`. Por padrão, espera o `appimagetool` em `~/ferramentas/appimagetool-x86_64.AppImage` (ajustável no próprio script). O AppImage final fica na raiz do projeto.

Para gerar uma release assinada (AppImage + checksums + chave pública):

```bash
scripts/release.sh
```

Os artefatos ficam em `release/v<versão>/`. Consulte `release/v2.0.0/PUBLICAR.md` para o passo a passo de publicação.

### Gerar `.app` no macOS

```bash
pip install -r requirements.txt

pyinstaller --name CofreSenhas --onefile --windowed \
  --icon=assets/icone.icns \
  --add-data "assets:assets" \
  --collect-all customtkinter \
  main.py
```

O repositório inclui `assets/icone.png` e `assets/icone.ico`, mas **não** inclui `icone.icns`. Gere o `.icns` a partir do PNG (por exemplo, com `iconutil`) ou remova a opção `--icon` para usar o ícone padrão.

### Scripts de linha de comando

Documentação detalhada em [`scripts/`](scripts/):

- **Exportar registros (JSON)** — [`README_exportar_registros.md`](scripts/README_exportar_registros.md)
- **Importar registros em massa (JSON)** — [`README_importar_registros.md`](scripts/README_importar_registros.md)
- **Exportar relatório (PDF)** — [`README_exportar_pdf.md`](scripts/README_exportar_pdf.md)

Especificações e exemplos ficam em [`docs/`](docs/).

### Estrutura do projeto

| Caminho | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada da aplicação. |
| `ui/` | Telas, formulários, diálogos e tooltips. |
| `dados/` | Cache de cofres recentes e modelo de registros. |
| `seguranca/` | Criptografia, formato do cofre e Secret ID. |
| `servicos/` | Exportação JSON/PDF, importação e backup. |
| `utils/` | Senha aleatória, força e clipboard. |
| `scripts/` | Ferramentas de linha de comando e release. |
| `docs/` | Especificações técnicas e guias. |

### Validação

Não há suíte de testes automatizada. Valide sintaxe e inicialização com:

```bash
python -m compileall -q main.py ui
python main.py
```

### Atalho no Linux (a partir do código-fonte)

```bash
chmod +x instalar_atalho.sh
./instalar_atalho.sh
```

Isso cria um ícone na área de trabalho e uma entrada no menu de aplicativos.

---

## 🧰 Tecnologias

- **Python 3.10+** — linguagem principal.
- **CustomTkinter** — interface gráfica moderna.
- **cryptography** — primitivas criptográficas.
- **PyInstaller** — empacotamento de executáveis.
- **AppImageTool** — distribuição Linux portátil.

---

## 🗺️ Roadmap

- [x] Criptografia AES + SHA512 + PBKDF2.
- [x] Interface gráfica com CustomTkinter.
- [x] Cache de cofres recentes.
- [x] Atalho desktop para Linux.
- [x] Empacotamento como AppImage.
- [x] Build para Windows (`.exe`).
- [x] Busca/filtro de senhas.
- [x] Gerador de senhas fortes integrado.
- [x] Exportar/importar registros (JSON) e relatório PDF.

---

## 🤝 Contribuindo

1. Faça um fork do projeto.
2. Crie uma branch: `git checkout -b feature/minha-feature`.
3. Commit suas mudanças: `git commit -m 'feat: adiciona minha feature'`.
4. Push para a branch: `git push origin feature/minha-feature`.
5. Abra um Pull Request.

### Padrão de commits

Este projeto segue Conventional Commits, com mensagens em pt-BR:

- `feat:` nova funcionalidade.
- `fix:` correção de bug.
- `docs:` mudanças na documentação.
- `refactor:` refatoração de código.
- `chore:` tarefas gerais.

---

## 📜 Licença

Este projeto está sob a licença **MIT**.

---

## 👨‍💻 Autor

Desenvolvido por **Daniel** 🚀

- 🌎 Porto Alegre, RS — Brasil

---

## 🙏 Agradecimentos

- Comunidade **Python** pela linguagem e bibliotecas.
- **Tom Schimansky** pelo CustomTkinter.
- Projeto **AppImage** por viabilizar distribuição Linux portátil.

---

<div align="center">

**Se este projeto te ajudou, considere dar uma ⭐ no repositório!**

Feito com ☕ e 🐍 em Porto Alegre, RS 🇧🇷

</div>
