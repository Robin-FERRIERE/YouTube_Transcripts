"""Logique de récupération des transcripts (sans interface graphique)."""
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
EXTENSIONS = {"md": ".md", "txt": ".txt", "srt": ".srt"}


def extract_video_id(value: str) -> str:
    """Accepte un identifiant brut ou une adresse YouTube (watch, youtu.be, shorts…)."""
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
    raise ValueError("Cette adresse ne ressemble pas à une adresse de vidéo YouTube.")


def fetch_metadata(video_id: str) -> dict:
    """Titre et chaîne via oEmbed. Ne bloque pas si l'appel échoue."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        r = requests.get("https://www.youtube.com/oembed",
                         params={"url": url, "format": "json"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {"title": data.get("title"), "author": data.get("author_name"), "url": url}
    except Exception:
        return {"title": None, "author": None, "url": url}


def fetch_snippets(video_id: str, languages: list[str]):
    """Retourne (fragments, infos). Repli sur la première langue disponible."""
    tlist = YouTubeTranscriptApi().list(video_id)
    try:
        transcript = tlist.find_transcript(languages)
    except CouldNotRetrieveTranscript:
        available = sorted(tlist, key=lambda t: t.is_generated)
        if not available:
            raise
        transcript = available[0]
    fetched = transcript.fetch()
    snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
    info = {
        "language": fetched.language,
        "language_code": fetched.language_code,
        "is_generated": fetched.is_generated,
    }
    return snippets, info


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def to_paragraphs(snippets: list[dict], max_chars: int = 600) -> list[str]:
    """Regroupe les fragments (haché sur YouTube) en paragraphes lisibles."""
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


def fmt_ts(seconds: float, srt: bool = False) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    if srt:
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def render(fmt: str, snippets, meta: dict, info: dict, video_id: str) -> str:
    if fmt == "srt":
        blocks = []
        for i, sn in enumerate(snippets, 1):
            end = sn["start"] + sn["duration"]
            blocks.append(f"{i}\n{fmt_ts(sn['start'], True)} --> {fmt_ts(end, True)}\n{sn['text']}\n")
        return "\n".join(blocks)

    body = "\n\n".join(to_paragraphs(snippets))
    if fmt == "txt":
        return body + "\n"

    title = meta.get("title") or video_id
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


def save(content: str, fmt: str, meta: dict, video_id: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = safe_filename(f"{meta['title']} [{video_id}]" if meta.get("title") else video_id)
    path = out_dir / f"{base}{EXTENSIONS.get(fmt, '.md')}"
    path.write_text(content, encoding="utf-8")
    return path


def friendly_error(exc: Exception) -> str:
    if isinstance(exc, CouldNotRetrieveTranscript):
        return ("Impossible de récupérer le transcript. La vidéo n'a probablement pas de "
                "sous-titres, elle est privée ou supprimée, ou YouTube bloque temporairement la connexion.")
    if isinstance(exc, requests.RequestException):
        return "Erreur réseau. Vérifiez votre connexion internet et réessayez."
    return f"Erreur inattendue : {exc}"
