#!/bin/bash
# Instala o actualiza el skill en ~/.claude/skills y revisa el entorno (macOS y Linux).
# En Windows usa:  python scripts/instalar.py
set -e
DEST="$HOME/.claude/skills/video-producto-ia-commerce"
REPO="${1:-https://github.com/infoecomplus-commits/video-producto-ia-commerce}"
mkdir -p "$HOME/.claude/skills"
if [ -d "$DEST/.git" ]; then
  echo "Actualizando video-producto-ia-commerce…"; git -C "$DEST" pull --ff-only
else
  echo "Instalando video-producto-ia-commerce…"; git clone --depth 1 "$REPO" "$DEST"
fi
python3 "$DEST/scripts/doctor.py" || true
echo
echo "Listo. Abre Claude Code y dile: haz un video de este producto."
