#!/usr/bin/env bash

if ! command -v flatpak-spawn >/dev/null 2>&1; then
    echo "Erro: flatpak-spawn não foi encontrado. Execute este script no terminal do VS Code Flatpak."
    exit 1
fi

exec flatpak-spawn --host -- /usr/bin/script -q -c '/bin/bash -l' /dev/null


