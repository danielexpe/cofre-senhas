# 🔐 Cofre de Senhas

> Gerenciador de senhas local, seguro e open-source, com criptografia forte e interface gráfica moderna.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-active-success)

---

## 📖 Sobre o Projeto

O **Cofre de Senhas** é uma aplicação desktop para armazenamento seguro de credenciais, desenvolvida em Python com foco em **privacidade total** e **criptografia robusta**. Todos os dados são armazenados **localmente** em arquivos criptografados — nenhuma informação trafega pela internet.

### ✨ Por que usar?

- 🔒 **Criptografia forte**: AES + SHA512 + PBKDF2 com múltiplas iterações
- 🏠 **100% local**: seus dados nunca saem da sua máquina
- 🔑 **Autenticação dupla**: Secret ID + Senha Mestra
- 💾 **Múltiplos cofres**: gerencie senhas pessoais, do trabalho, etc., separadamente
- 🚀 **Cache inteligente**: acesso rápido aos cofres recentes
- 🎨 **Interface moderna**: GUI limpa e intuitiva com CustomTkinter

---

## 🔐 Segurança

### Como funciona a criptografia?

1. Sua **senha mestra** passa por **PBKDF2** (centenas de milhares de iterações) com salt aleatório
2. A chave derivada criptografa o conteúdo do cofre via **AES**
3. A integridade é validada por hash **SHA512**
4. O **Secret ID** atua como camada adicional de identificação

### Princípios adotados

- ✅ Senha mestra **nunca** é armazenada (nem em cache, nem em arquivo)
- ✅ Cada cofre tem seu próprio salt único
- ✅ Cache local guarda apenas metadados não-sensíveis (caminhos e Secret IDs)
- ✅ Validação automática remove referências a cofres inexistentes

> ⚠️ **Aviso importante**: se você esquecer sua senha mestra, **não há como recuperá-la**. Esse é o preço da segurança real. Faça backups dos seus arquivos `.vault`.

---

## Downloads

- Página de Releases: https://github.com/danielexpe/cofre-senhas/releases
- Última versão: https://github.com/danielexpe/cofre-senhas/releases/latest

Artefatos disponíveis no Release:
- AppImage (ex.: `CofreDeSenhas-1.1-x86_64.AppImage`)
- `SHA256SUMS`
- `SHA256SUMS.asc`
- `DANIEL-PUBKEY.asc` (chave pública do autor)

## Verifique a integridade e a assinatura

Fingerprint GPG do autor: `D7E1 90A8 26A9 82E5 01B7 469F F7E9 56C8 37AB D08F`  
(Chave: `D7E190A826A982E501B7469FF7E956C837ABD08F`)

```bash
# 0) Ajuste o nome do arquivo que você baixou
APP="CofreDeSenhas-1.1-x86_64.AppImage"

# (Opcional) Baixe direto os arquivos de verificação da última release
# wget https://github.com/danielexpe/cofre-senhas/releases/latest/download/DANIEL-PUBKEY.asc
# wget https://github.com/danielexpe/cofre-senhas/releases/latest/download/SHA256SUMS
# wget https://github.com/danielexpe/cofre-senhas/releases/latest/download/SHA256SUMS.asc

# 1) Importar a chave pública do Daniel
gpg --import DANIEL-PUBKEY.asc

# 2) Verificar a assinatura dos checksums
gpg --verify SHA256SUMS.asc SHA256SUMS

# 3) Conferir o hash do AppImage (deve bater com a linha correspondente em SHA256SUMS)
sha256sum "$APP"

# 4) (Opcional) Verificar a assinatura PGP embutida no AppImage
./"$APP" --appimage-signature | head -n 20
```

---

## 🚀 Instalação

### Pré-requisitos

- Python **3.10** ou superior
- pip
- tkinter (geralmente já vem com o Python)

### Método 1: Executando o código-fonte

\`\`\`bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/cofre-senhas.git
cd cofre-senhas

# 2. Crie um ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python main.py
\`\`\`

### Método 2: AppImage (Linux)

Baixe o AppImage da última release e execute:

\`\`\`bash
chmod +x CofreDeSenhas-1.1-x86_64.AppImage
./CofreDeSenhas-1.1-x86_64.AppImage
\`\`\`

Ou simplesmente **dois cliques** no arquivo. Sem instalação, sem dependências. ✨

---

## 🎯 Uso

### Primeiro acesso (criar um cofre)

1. Abra a aplicação
2. Clique em **"Criar Novo Cofre"**
3. Defina:
   - 📁 **Local do arquivo** (onde o .vault será salvo)
   - 🆔 **Secret ID** (identificador único, ex: daniel_pessoal)
   - 🔑 **Senha Mestra** (forte, com letras, números e símbolos)
4. Pronto! Seu cofre está criado e criptografado

### Acessos seguintes

1. Selecione um cofre dos **cards recentes** ou abra manualmente
2. Digite a **senha mestra**
3. Gerencie suas senhas: adicionar, editar, copiar, remover

---

## 🛠️ Atalho no Linux

Na raiz do projeto, execute o instalador de atalho:

\`\`\`bash
chmod +x instalar_atalho.sh
./instalar_atalho.sh
\`\`\`

Isso cria:
- 🖥️ Ícone na **área de trabalho**
- 📋 Entrada no **menu de aplicativos**

---

## 📦 Gerando Executáveis

### AppImage (Linux)

\`\`\`bash
chmod +x build_appimage.sh
./build_appimage.sh
\`\`\`

### .exe (Windows)

\`\`\`powershell
pip install pyinstaller
pyinstaller --name CofreSenhas --onefile --windowed \`
            --icon=assets/icone.ico \`
            --add-data "assets;assets" \`
            --collect-all customtkinter \`
            main.py
\`\`\`

### .app (macOS)

\`\`\`bash
pip install pyinstaller
pyinstaller --name CofreSenhas --onefile --windowed \\
            --icon=assets/icone.icns \\
            --add-data "assets:assets" \\
            --collect-all customtkinter \\
            main.py
\`\`\`

---

## 🧰 Tecnologias

- **Python 3.10+** — Linguagem principal
- **CustomTkinter** — Interface gráfica moderna
- **cryptography** — Primitivas criptográficas
- **PyInstaller** — Empacotamento de executáveis
- **AppImageTool** — Distribuição Linux portátil

---

## 🗺️ Roadmap

- [x] Criptografia AES + SHA512 + PBKDF2
- [x] Interface gráfica com CustomTkinter
- [x] Sistema de cache de cofres recentes
- [x] Atalho desktop para Linux
- [x] Empacotamento como AppImage
- [ ] Build para Windows (.exe)
- [ ] Build para macOS (.app)
- [ ] Busca/filtro de senhas
- [ ] Botão "copiar senha" com auto-limpeza do clipboard
- [ ] Gerador de senhas fortes integrado
- [ ] Exportar/importar cofre (backup)
- [ ] Auto-bloqueio por inatividade
- [ ] Suporte a 2FA/TOTP

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch: \`git checkout -b feature/minha-feature\`
3. Commit suas mudanças: \`git commit -m 'feat: adiciona minha feature'\`
4. Push para a branch: \`git push origin feature/minha-feature\`
5. Abra um Pull Request

### Padrão de commits

Este projeto segue Conventional Commits:

- \`feat:\` nova funcionalidade
- \`fix:\` correção de bug
- \`docs:\` mudanças na documentação
- \`refactor:\` refatoração de código
- \`chore:\` tarefas gerais

---

## 📜 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo LICENSE para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido por **Daniel** 🚀

- 🌎 Blumenau, SC — Brasil

---

## 🙏 Agradecimentos

- Comunidade **Python** pela linguagem e bibliotecas incríveis
- **Tom Schimansky** pelo CustomTkinter
- Projeto **AppImage** por viabilizar distribuição Linux portátil

---

<div align="center">

**Se este projeto te ajudou, considere dar uma ⭐ no repositório!**

Feito com ☕ e 🐍 em Blumenau, SC 🇧🇷

</div>
EOF

echo "✅ README.md criado com sucesso!"
ls -lh README.md
