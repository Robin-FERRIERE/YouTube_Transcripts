# Mode d'emploi : extraire le transcript d'une vidéo YouTube

## Phase 1 : ouvrir le projet

1. Ouvrez **VS Code**.
2. Menu **File > Open Folder…** (Fichier > Ouvrir un dossier).
3. Dans OneDrive, ouvrez le dossier **`YouTube_Transcripts`** (chemin : `OneDrive-orange.com/DEV/YouTube_Transcripts/YouTube_Transcripts`), puis cliquez sur **Open**.
4. Ouvrez le terminal : menu **Terminal > New Terminal** (ou `` Ctrl + ` ``).

## Phase 2 : mettre le code à jour

À faire une seule fois après une modification sur GitHub :

```bash
git checkout main
git pull
```

Le message `Already up to date` signifie que tout est à jour.

## Phase 3 : activer l'environnement Python

Dans le terminal, à partir du dossier du projet :

```bash
source .venv/bin/activate
```

Le début de la ligne doit afficher `(.venv)`. **Sans cette ligne, le script ne fonctionne pas.** Vous devez la refaire à chaque nouvelle ouverture de VS Code.

*Si `.venv` n'existe pas (erreur « no such file »), créez-le une fois :*

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Phase 4 : lancer l'extraction

Copiez l'adresse de la vidéo dans la barre du navigateur, puis tapez :

```bash
python yt_transcript.py "ADRESSE_DE_LA_VIDEO" -o transcripts/
```

- **Mettez toujours l'adresse entre guillemets** (`"…"`). Sans eux, le terminal Mac plante sur le `?`.
- Vous pouvez aussi donner seulement l'identifiant, après le `v=` (ex. `AkIuxNdInvc`).

**Options utiles :**

| Ce que vous voulez | Commande (à ajouter à la fin) |
|---|---|
| Transcript en anglais en priorité | `-l en fr` |
| Texte brut au lieu de Markdown | `-f txt` |
| Lignes horodatées | `--timestamps` |
| Voir les langues disponibles | `--list` (au lieu de `-o transcripts/`) |
| Traduire en français | `--translate fr` |

## Phase 5 : récupérer le résultat

1. Dans l'explorateur de VS Code (à gauche), ouvrez le dossier **`transcripts`**.
2. Cliquez sur le fichier `.md` : il porte le titre de la vidéo.
3. Copiez le texte et collez-le dans Claude.

Le terminal affiche `✓ … → transcripts/…` quand c'est réussi.

## Phase 6 : dépannage

| Message ou symptôme | Ce qu'il faut faire |
|---|---|
| `no matches found` | Mettez l'adresse entre guillemets. |
| `command not found: python` | Remplacez `python` par `python3`. |
| `No such file or directory: yt_transcript.py` | Vérifiez que vous êtes dans le bon dossier (`pwd`). |
| `(.venv)` absent de la ligne | Relancez `source .venv/bin/activate`. |
| `Could not retrieve a transcript` | La vidéo n'a pas de sous-titres, ou elle est privée ou supprimée. Essayez une autre vidéo. |
| Erreur réseau ou `ProxyError` | Vérifiez votre connexion, ou réessayez plus tard. |
| Le script ne marche plus alors qu'il marchait | Mettez la bibliothèque à jour (voir ci-dessous). |

## Maintenance (de temps en temps)

YouTube change parfois ses pages, ce qui peut casser la bibliothèque. Pour la mettre à jour :

```bash
pip install -U youtube-transcript-api
```

---

**Rappel :** votre modification locale du `README.md` est toujours rangée dans la réserve Git (`git stash list`). Elle ne gêne pas l'outil. Vous pouvez l'ignorer.
