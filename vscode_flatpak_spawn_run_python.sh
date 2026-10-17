#!/usr/bin/env bash
set -e

flatpak-spawn --host bash -lc '
  cd "$HOME/myDev/development/cofre-senhas"
  source .venv/bin/activate
  exec python main.py
'

