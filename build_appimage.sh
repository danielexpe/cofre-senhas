#!/bin/bash
# Script para gerar AppImage do Cofre de Senhas
set -e  # para no primeiro erro

PROJETO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="CofreDeSenhas"
VERSION="1.1"
BUILD_DIR="$PROJETO_DIR/build_appimage"
APPDIR="$BUILD_DIR/${APP_NAME}.AppDir"

echo "🧹 Limpando builds anteriores..."
rm -rf "$BUILD_DIR" "$PROJETO_DIR/build" "$PROJETO_DIR/dist" "$PROJETO_DIR"/*.spec

echo "📦 Empacotando com PyInstaller..."
cd "$PROJETO_DIR"
pyinstaller \
    --name "$APP_NAME" \
    --onedir \
    --windowed \
    --noconfirm \
    --add-data "assets:assets" \
    --hidden-import customtkinter \
    --collect-all customtkinter \
    --collect-all tkinter \
    main.py

echo "📁 Criando estrutura AppDir..."
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copia tudo que o PyInstaller gerou
cp -r "$PROJETO_DIR/dist/$APP_NAME/"* "$APPDIR/usr/bin/"

# Ícone (usa o do projeto se existir)
if [ -f "$PROJETO_DIR/assets/icone.png" ]; then
    cp "$PROJETO_DIR/assets/icone.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
    cp "$PROJETO_DIR/assets/icone.png" "$APPDIR/${APP_NAME}.png"
else
    echo "⚠️  Sem assets/icone.png — criando ícone placeholder"
    # cria um PNG vazio mínimo (você deve substituir depois)
    convert -size 256x256 xc:'#2b6cb0' "$APPDIR/${APP_NAME}.png" 2>/dev/null || \
        touch "$APPDIR/${APP_NAME}.png"
fi

# Arquivo .desktop dentro do AppDir
cat > "$APPDIR/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Cofre de Senhas
Comment=Gerenciador seguro de senhas
Exec=${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Categories=Utility;Security;
EOF

cp "$APPDIR/${APP_NAME}.desktop" "$APPDIR/usr/share/applications/"

# AppRun (script de inicialização que o AppImage executa)
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
cd "${HERE}/usr/bin"
exec "${HERE}/usr/bin/CofreDeSenhas" "$@"
EOF
chmod +x "$APPDIR/AppRun"

echo "🔨 Gerando AppImage..."
APPIMAGETOOL="$HOME/ferramentas/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "❌ AppImageTool não encontrado em $APPIMAGETOOL"
    echo "   Baixe com: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    exit 1
fi

ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "$PROJETO_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"

echo ""
echo "✅ AppImage gerado com sucesso!"
echo "   📦 $PROJETO_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"
echo ""
echo "Para executar:"
echo "   chmod +x ${APP_NAME}-${VERSION}-x86_64.AppImage"
echo "   ./${APP_NAME}-${VERSION}-x86_64.AppImage"

