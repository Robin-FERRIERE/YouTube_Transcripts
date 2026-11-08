# YT_Transcript

Application Mac qui récupère le transcript d'une vidéo YouTube et l'enregistre en Markdown, texte ou SRT.

## Installation

1. Installez Python 3 depuis [python.org](https://www.python.org/downloads/) (macOS).
2. Placez le dossier `desktop` où vous voulez (par exemple sur le Bureau) et renommez-le `YT_Transcript`.
3. Dans le Terminal, autorisez le lanceur une fois :
   ```bash
   chmod +x ~/Desktop/YT_Transcript/YT_Transcript.command
   ```
4. Double-cliquez sur `YT_Transcript.command`. Au premier lancement, les dépendances s'installent automatiquement.

## Utilisation

1. Collez l'adresse d'une vidéo YouTube.
2. Choisissez les langues (ordre de préférence) et le format.
3. Cliquez sur **Récupérer**. Le fichier est enregistré dans le dossier `transcripts/`.

## Limites

- La vidéo doit avoir des sous-titres (manuels ou générés automatiquement).
- La bibliothèque `youtube-transcript-api` n'est pas officielle : elle peut cesser de fonctionner si YouTube modifie ses pages. Mettez-la à jour avec `.venv/bin/python -m pip install -U youtube-transcript-api`.
- YouTube peut bloquer les adresses IP de serveurs cloud.
