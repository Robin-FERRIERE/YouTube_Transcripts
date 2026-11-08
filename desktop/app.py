#!/usr/bin/env python3
"""YT_Transcript : fenêtre native (pywebview) avec interface HTML/CSS au style verre."""
import subprocess
from pathlib import Path

import webview

from transcript_core import (extract_video_id, fetch_metadata, fetch_snippets,
                             friendly_error, render, save)

APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / "transcripts"
UI_FILE = APP_DIR / "ui" / "index.html"


class Api:
    """Méthodes appelées depuis l'interface (JavaScript) via window.pywebview.api."""

    def get_transcript(self, url: str, languages: str, fmt: str) -> dict:
        try:
            video_id = extract_video_id(url)
        except ValueError as e:
            return {"ok": False, "message": str(e)}

        langs = languages.split() or ["fr", "en"]
        fmt = fmt if fmt in {"md", "txt", "srt"} else "md"
        try:
            meta = fetch_metadata(video_id)
            snippets, info = fetch_snippets(video_id, langs)
            content = render(fmt, snippets, meta, info, video_id)
            path = save(content, fmt, meta, video_id, OUTPUT_DIR)
        except Exception as e:  # on affiche toute erreur à l'utilisateur
            return {"ok": False, "message": friendly_error(e)}

        return {
            "ok": True,
            "title": meta.get("title") or video_id,
            "author": meta.get("author") or "",
            "language": f"{info['language']} ({info['language_code']})",
            "generated": bool(info["is_generated"]),
            "text": content,
            "filename": path.name,
        }

    def copy(self, text: str) -> bool:
        """Copie dans le presse-papiers macOS."""
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=False)
        return True

    def close(self) -> None:
        webview.windows[0].destroy()

    def minimize(self) -> None:
        webview.windows[0].minimize()

    def fullscreen(self) -> None:
        webview.windows[0].toggle_fullscreen()

    def open_folder(self) -> bool:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(OUTPUT_DIR)], check=False)
        return True


def main():
    webview.create_window(
        "YT_Transcript",
        str(UI_FILE),
        js_api=Api(),
        width=880,
        height=620,
        min_size=(640, 480),
        frameless=True,
        transparent=True,
        easy_drag=True,
    )
    webview.start()


if __name__ == "__main__":
    main()
