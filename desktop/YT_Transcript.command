#!/bin/bash
# Double-cliquez sur ce fichier pour lancer YT_Transcript.
# Au premier lancement (ou après une mise à jour), il installe les dépendances.

cd "$(dirname "$0")" || exit 1

pause_and_exit() {
  echo ""
  read -r -p "Appuyez sur Entrée pour fermer cette fenêtre..."
  exit 1
}

if [ ! -x ".venv/bin/python" ]; then
  echo "Première utilisation : création de l'environnement..."
  python3 -m venv .venv || pause_and_exit
fi

if ! .venv/bin/python -c "import webview, youtube_transcript_api" >/dev/null 2>&1; then
  echo "Installation des dépendances (quelques minutes la première fois)..."
  .venv/bin/python -m pip install -q -U pip || pause_and_exit
  .venv/bin/python -m pip install -q -U youtube-transcript-api requests pywebview || pause_and_exit
  echo "Installation terminée."
fi

.venv/bin/python app.py
