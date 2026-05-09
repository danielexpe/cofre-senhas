#!/bin/bash
# Script para criar atalho do Cofre de Senhas no Zorin OS

# Detecta o diretório onde este script está (raiz do projeto)
PROJETO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detecta qual python usar (prioriza venv local se existir)
if [ -f "$PROJETO_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJETO_DIR/.venv/bin/python"
elif [ -f "$PROJETO_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$PROJETO_DIR/venv/bin/python"
else
    PYTHON_BIN="$(which python3)"
fi

# Caminho do ícone (usa o do projeto se existir, senão um genérico do sistema)
if [ -f "$PROJETO_DIR/assets/icone.png" ]; then
    ICONE="$PROJETO_DIR/assets/icone.png"
else
    ICONE="dialog-password"  # ícone genérico do tema do sistema
fi

# Conteúdo do arquivo .desktop
ATALHO_CONTENT="[Desktop Entry]
Version=1.0
Type=Application
Name=Cofre de Senhas
Comment=Gerenciador seguro de senhas
Exec=$PYTHON_BIN $PROJETO_DIR/main.py
Path=$PROJETO_DIR
Icon=$ICONE
Terminal=false
Categories=Utility;Security;
StartupNotify=true
StartupWMClass=Cofre de Senhas"

# 1. Cria no menu de aplicativos
MENU_FILE="$HOME/.local/share/applications/cofre-senhas.desktop"
mkdir -p "$HOME/.local/share/applications"
echo "$ATALHO_CONTENT" > "$MENU_FILE"
chmod +x "$MENU_FILE"
echo "✓ Atalho criado no menu: $MENU_FILE"

# 2. Cria também no Desktop
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
DESKTOP_FILE="$DESKTOP_DIR/cofre-senhas.desktop"
mkdir -p "$DESKTOP_DIR"
echo "$ATALHO_CONTENT" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

# Marca como confiável (necessário no GNOME/Zorin recente)
gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null

echo "✓ Atalho criado na área de trabalho: $DESKTOP_FILE"

# Atualiza o cache de aplicativos
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null

echo ""
echo "✅ Pronto! Você pode:"
echo "   • Clicar no ícone da área de trabalho"
echo "   • Ou buscar 'Cofre de Senhas' no menu de aplicativos"

