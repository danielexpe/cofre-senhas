#!/usr/bin/env bash
#
# Gera, assina e verifica os artefatos de release do Cofre de Senhas.
#
# Uso:
#   scripts/release.sh                    # VERSION=1.5.0, TAG=v1.5.0
#   VERSION=1.6 TAG=v1.6.0 scripts/release.sh
#   SKIP_BUILD=1 scripts/release.sh       # reaproveita o AppDir já gerado
#
# Requisitos:
#   - Chave GPG secreta importada (padrão: F7E956C837ABD08F)
#   - appimagetool em $HOME/ferramentas (ou defina APPIMAGETOOL)
#
# A passphrase GPG é solicitada uma vez pelo gpg-agent. Para cacheá-la antes:
#   export GPG_TTY=$(tty)
#   echo unlock | gpg --armor --local-user F7E956C837ABD08F --clearsign >/dev/null
#
set -euo pipefail

VERSION="${VERSION:-1.5.0}"
TAG="${TAG:-v1.5.0}"
GPG_KEY="${GPG_KEY:-F7E956C837ABD08F}"
APPIMAGETOOL="${APPIMAGETOOL:-$HOME/ferramentas/appimagetool-x86_64.AppImage}"

PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="CofreDeSenhas-${VERSION}-x86_64.AppImage"
APPDIR="$PROJ/build_appimage/CofreDeSenhas.AppDir"
OUT="$PROJ/release/$TAG"

export GPG_TTY="${GPG_TTY:-$(tty 2>/dev/null || true)}"

echo "==> Release $TAG (AppImage $VERSION)"

if [ "${SKIP_BUILD:-0}" != "1" ]; then
    echo "==> Build com PyInstaller + AppImage..."
    ( cd "$PROJ" && PATH="$PROJ/.venv/bin:$PATH" bash build_appimage.sh )
    # build_appimage.sh remove *.spec; restaura se for versionado
    ( cd "$PROJ" && git checkout -- CofreDeSenhas.spec 2>/dev/null || true )
else
    echo "==> Build pulado (SKIP_BUILD=1)"
fi

[ -d "$APPDIR" ] || { echo "ERRO: AppDir não encontrado: $APPDIR" >&2; exit 1; }
[ -x "$APPIMAGETOOL" ] || { echo "ERRO: appimagetool não encontrado: $APPIMAGETOOL" >&2; exit 1; }
gpg --list-secret-keys "$GPG_KEY" >/dev/null 2>&1 || { echo "ERRO: chave GPG secreta $GPG_KEY não encontrada" >&2; exit 1; }

mkdir -p "$OUT"

echo "==> Assinando o AppImage (chave $GPG_KEY)..."
ARCH=x86_64 "$APPIMAGETOOL" --sign --sign-key "$GPG_KEY" "$APPDIR" "$OUT/$APP"

# Normaliza o nome caso o appimagetool gere outro (derivado do .desktop)
if [ ! -f "$OUT/$APP" ]; then
    ALT="$(ls -1 "$OUT"/*.AppImage 2>/dev/null | head -n1 || true)"
    [ -n "$ALT" ] && mv "$ALT" "$OUT/$APP"
fi

echo "==> Gerando SHA256SUMS..."
( cd "$OUT" && sha256sum "$APP" > SHA256SUMS )

echo "==> Assinando SHA256SUMS..."
gpg --batch --yes --armor --local-user "$GPG_KEY" \
    --detach-sign --output "$OUT/SHA256SUMS.asc" "$OUT/SHA256SUMS"

echo "==> Exportando chave pública..."
gpg --batch --armor --export "$GPG_KEY" > "$OUT/DANIEL-PUBKEY.asc"

echo
echo "==> Verificação da assinatura embutida no AppImage:"
"$OUT/$APP" --appimage-signature | head -n 5 || true

echo
echo "==> Artefatos em: $OUT"
ls -lh "$OUT"
echo
echo "==> Para publicar (você mesmo):"
echo "    veja release/$TAG/PUBLICAR.md"
