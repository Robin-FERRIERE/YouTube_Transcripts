#!/usr/bin/env python3
"""YouTube transcript extractor.

Récupère le transcript d'une ou plusieurs vidéos YouTube et l'exporte en
Markdown (prêt à être donné à Claude), texte brut, SRT ou JSON.

Exemples :
    python yt_transcript.py https://www.youtube.com/watch?v=VIDEO_ID
    python yt_transcript.py VIDEO_ID -l fr en -f md -o transcripts/
    python yt_transcript.py URL1 URL2 --timestamps
    python yt_transcript.py URL --list
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(value: str) -> str:
    """Accepte un ID brut ou n'importe quelle forme d'URL YouTube."""
    value = value.strip()
    if VIDEO_ID_RE.match(value):
        return value
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    candidate = None
    if host == "youtu.be":
        candidate = parsed.path.lstrip("/").split("/")[0]
    elif host.endswith("youtube.com") or host == "youtube-nocookie.com":
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [None])[0]
        else:
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live", "v", "e"}:
                candidate = parts[1]
    if candidate and VIDEO_ID_RE.match(candidate):
        return candidate
    raise ValueError(f"Impossible d'extraire un ID de vidéo depuis : {value!r}")


def fetch_metadata(video_id: str) -> dict:
    """Titre et chaîne via oEmbed (sans clé API). Non bloquant en cas d'échec."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        r = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return {"title": data.get("title"), "author": data.get("author_name"), "url": url}
    except Exception:
        return {"title": None, "author": None, "url": url}


def fmt_ts(seconds: float, srt: bool = False) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    if srt:
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def to_paragraphs(snippets: list[dict], max_chars: int = 600) -> list[str]:
    """Regroupe les fragments en paragraphes lisibles (le transcript YT est haché)."""
    paragraphs, buf = [], ""
    for sn in snippets:
        t = clean(sn["text"])
        if not t:
            continue
        buf = f"{buf} {t}".strip()
        if len(buf) >= max_chars and buf[-1:] in ".!?":
            paragraphs.append(buf)
            buf = ""
        elif len(buf) >= max_chars * 2:
            paragraphs.append(buf)
            buf = ""
    if buf:
        paragraphs.append(buf)
    return paragraphs


def render(snippets, meta, info, fmt, timestamps):
    if fmt == "json":
        return json.dumps({**meta, **info, "snippets": snippets}, ensure_ascii=False, indent=2)
    if fmt == "srt":
        blocks = []
        for i, sn in enumerate(snippets, 1):
            end = sn["start"] + sn["duration"]
            blocks.append(f"{i}\n{fmt_ts(sn['start'], True)} --> {fmt_ts(end, True)}\n{sn['text']}\n")
        return "\n".join(blocks)
    if timestamps:
        body = "\n".join(f"[{fmt_ts(sn['start'])}] {clean(sn['text'])}" for sn in snippets if clean(sn["text"]))
    else:
        body = "\n\n".join(to_paragraphs(snippets))
    if fmt == "txt":
        return body + "\n"
    # Markdown avec en-tête de contexte, pratique pour alimenter un LLM
    title = meta.get("title") or info["video_id"]
    lines = [f"# {title}", ""]
    if meta.get("author"):
        lines.append(f"- **Chaîne** : {meta['author']}")
    lines += [
        f"- **URL** : {meta['url']}",
        f"- **Langue** : {info['language']} ({info['language_code']})"
        + (" — générée automatiquement" if info["is_generated"] else ""),
        "",
        "## Transcript",
        "",
        body,
        "",
    ]
    return "\n".join(lines)


def safe_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", name).strip().strip(".")
    return re.sub(r"\s+", " ", name)[:120] or "transcript"


def list_transcripts(api, video_id):
    print(f"Transcripts disponibles pour {video_id} :")
    for t in api.list(video_id):
        kind = "auto" if t.is_generated else "manuel"
        tr = " (traduisible)" if t.is_translatable else ""
        print(f"  - {t.language_code:8} {t.language} [{kind}]{tr}")


def get_transcript(api, video_id, languages, translate):
    tlist = api.list(video_id)
    try:
        transcript = tlist.find_transcript(languages)
    except CouldNotRetrieveTranscript:
        # Aucune langue demandée : on prend le premier disponible (manuel en priorité)
        available = sorted(tlist, key=lambda t: t.is_generated)
        if not available:
            raise
        transcript = available[0]
        print(f"  ! Langues {languages} indisponibles, utilisation de '{transcript.language_code}'",
              file=sys.stderr)
    if translate and transcript.language_code != translate:
        transcript = transcript.translate(translate)
    fetched = transcript.fetch()
    snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
    info = {
        "video_id": video_id,
        "language": fetched.language,
        "language_code": fetched.language_code,
        "is_generated": fetched.is_generated,
    }
    return snippets, info


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Extrait le transcript de vidéos YouTube.")
    p.add_argument("videos", nargs="+", help="URL(s) ou ID(s) de vidéo YouTube")
    p.add_argument("-l", "--languages", nargs="+", default=["fr", "en"],
                   help="Langues par ordre de préférence (défaut : fr en)")
    p.add_argument("-f", "--format", choices=["md", "txt", "srt", "json"], default="md",
                   help="Format de sortie (défaut : md)")
    p.add_argument("-o", "--output", help="Dossier de sortie (sinon : affichage à l'écran)")
    p.add_argument("-t", "--timestamps", action="store_true",
                   help="Une ligne par fragment avec horodatage (md/txt)")
    p.add_argument("--translate", metavar="LANG", help="Traduire le transcript (ex : fr)")
    p.add_argument("--list", action="store_true", help="Lister les transcripts disponibles")
    args = p.parse_args(argv)

    api = YouTubeTranscriptApi()
    out_dir = Path(args.output) if args.output else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    errors = 0
    for raw in args.videos:
        try:
            vid = extract_video_id(raw)
            if args.list:
                list_transcripts(api, vid)
                continue
            snippets, info = get_transcript(api, vid, args.languages, args.translate)
            meta = fetch_metadata(vid)
            content = render(snippets, meta, info, args.format, args.timestamps)
            if out_dir:
                base = safe_filename(f"{meta['title']} [{vid}]" if meta.get("title") else vid)
                path = out_dir / f"{base}.{args.format}"
                path.write_text(content, encoding="utf-8")
                print(f"✓ {vid} → {path}", file=sys.stderr)
            else:
                print(content)
        except (ValueError, CouldNotRetrieveTranscript) as e:
            errors += 1
            print(f"✗ {raw} : {e}", file=sys.stderr)
        except requests.RequestException as e:
            errors += 1
            print(f"✗ {raw} : erreur réseau ({e.__class__.__name__}) — YouTube est-il joignable ?",
                  file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
