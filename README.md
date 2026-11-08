# YouTube Transcripts

Récupérez le transcript d'une vidéo YouTube et enregistrez-le en Markdown, texte ou SRT, prêt à être utilisé avec un assistant IA comme Claude.

Le projet propose deux outils :

- **Une application Mac** (`desktop/`) : une fenêtre où l'on colle l'adresse de la vidéo et l'on clique sur un bouton. Voir [`desktop/README.md`](desktop/README.md).
- **Un script en ligne de commande** (`yt_transcript.py`) : pratique pour traiter plusieurs vidéos d'un coup ou automatiser l'export.

## Fonctionnalités

- Acceptation de tous les formats d'adresse YouTube (`watch`, `youtu.be`, `shorts`, `embed`, `live`) ou de l'identifiant seul.
- Choix de la langue par ordre de préférence, avec repli automatique sur le premier transcript disponible.
- Sous-titres manuels ou générés automatiquement.
- Export en Markdown (avec titre, chaîne, URL et langue), en texte brut, en SRT ou en JSON.
- Traduction via YouTube (ligne de commande).

## Installation du script en ligne de commande

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Affiche le transcript en Markdown
python yt_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Enregistre dans le dossier transcripts/
python yt_transcript.py "URL" -o transcripts/

# Plusieurs vidéos, langues préférées anglais puis français, format texte
python yt_transcript.py "URL1" "URL2" -l en fr -f txt -o transcripts/

# Lignes horodatées, ou liste des transcripts disponibles
python yt_transcript.py "URL" --timestamps
python yt_transcript.py "URL" --list
```

| Option | Rôle | Défaut |
|---|---|---|
| `-l`, `--languages` | Langues par ordre de préférence | `fr en` |
| `-f`, `--format` | `md`, `txt`, `srt` ou `json` | `md` |
| `-o`, `--output` | Dossier de sortie (sinon affichage à l'écran) | — |
| `-t`, `--timestamps` | Une ligne horodatée par fragment | désactivé |
| `--translate LANG` | Traduction automatique YouTube | — |
| `--list` | Liste les transcripts disponibles | — |

## Limites

- La vidéo doit avoir des sous-titres, manuels ou générés automatiquement.
- La bibliothèque utilisée, [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api), n'est pas officielle : elle peut cesser de fonctionner si YouTube modifie ses pages.
- YouTube peut bloquer les adresses IP de serveurs cloud. Préférez une machine personnelle.

## Licence

Ce projet est distribué sous licence MIT. Voir [LICENSE](LICENSE).
