# YouTube_Transcripts
Un truc pour récupérer des transcripts de vidéos YT pour alimenter Claude.

## Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Affiche le transcript (Markdown) d'une vidéo
python yt_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Sauvegarde dans transcripts/ (nom de fichier = titre de la vidéo)
python yt_transcript.py URL -o transcripts/

# Plusieurs vidéos, langue préférée anglais puis français, en texte brut
python yt_transcript.py URL1 URL2 -l en fr -f txt -o transcripts/

# Avec horodatages, ou en SRT / JSON
python yt_transcript.py URL --timestamps
python yt_transcript.py URL -f srt -o transcripts/

# Lister les langues disponibles / traduire vers le français
python yt_transcript.py URL --list
python yt_transcript.py URL --translate fr
```

Formats acceptés en entrée : ID brut, `youtube.com/watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`.

| Option | Rôle | Défaut |
|---|---|---|
| `-l / --languages` | Langues par ordre de préférence | `fr en` |
| `-f / --format` | `md`, `txt`, `srt`, `json` | `md` |
| `-o / --output` | Dossier de sortie (sinon stdout) | — |
| `-t / --timestamps` | Une ligne horodatée par fragment | off |
| `--translate LANG` | Traduction automatique YouTube | — |
| `--list` | Liste les transcripts disponibles | — |

Si aucune des langues demandées n'existe, le script prend le premier transcript disponible (manuel prioritaire sur auto-généré) et le signale.

Le format `md` regroupe les fragments en paragraphes et ajoute un en-tête (titre, chaîne, URL, langue) : c'est le plus adapté pour coller dans Claude.

## Limites

- Ne fonctionne que si la vidéo a des sous-titres (manuels ou auto-générés).
- YouTube bloque souvent les IP de serveurs cloud (AWS, GCP…) : lancer le script depuis une machine perso.
