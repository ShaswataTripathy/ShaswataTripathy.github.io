#!/usr/bin/env python3
"""
Fetches latest Medium posts and Hugging Face models and rewrites the
BLOGS and MODELS sections of index.html between marker comments.

Runs on GitHub Actions daily. Uses only the Python stdlib.
"""

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

MEDIUM_USER = "tripathyshaswata"
HF_USER = "tripathyShaswata"

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

UA = "Mozilla/5.0 (compatible; shaswata-site-updater/1.0)"


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# ---------- Medium ----------

def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def excerpt(text: str, limit: int = 140) -> str:
    text = strip_tags(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def parse_medium_date(s: str) -> str:
    # RFC 822 like "Fri, 10 Apr 2026 12:34:56 GMT"
    try:
        dt = datetime.strptime(s.strip(), "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        try:
            dt = datetime.strptime(s.strip()[:25], "%a, %d %b %Y %H:%M:%S")
        except ValueError:
            return s
    return dt.strftime("%b %d, %Y")


def clean_medium_link(url: str) -> str:
    # Strip RSS tracking params like ?source=rss-...
    return url.split("?", 1)[0]


def fetch_medium_posts() -> list[dict]:
    url = f"https://medium.com/feed/@{MEDIUM_USER}"
    data = fetch(url).decode("utf-8", errors="replace")
    root = ET.fromstring(data)
    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = clean_medium_link((item.findtext("link") or "").strip())
        pub = (item.findtext("pubDate") or "").strip()
        desc_node = item.find("description")
        content_node = item.find("content:encoded", ns)
        raw_desc = ""
        if content_node is not None and content_node.text:
            raw_desc = content_node.text
        elif desc_node is not None and desc_node.text:
            raw_desc = desc_node.text
        posts.append({
            "title": title,
            "link": link,
            "date": parse_medium_date(pub),
            "excerpt": excerpt(raw_desc, 130),
        })
    return posts


# ---------- Hugging Face ----------

PIPELINE_LABEL = {
    "text-generation": "text-generation",
    "text-classification": "text-classification",
    "token-classification": "token-classification",
    "question-answering": "question-answering",
    "summarization": "summarization",
    "translation": "translation",
    "feature-extraction": "embeddings",
    "sentence-similarity": "sentence-similarity",
    "image-classification": "image-classification",
    "image-segmentation": "image-segmentation",
    "object-detection": "object-detection",
    "automatic-speech-recognition": "speech-recognition",
    "text-to-image": "text-to-image",
    "image-to-text": "image-to-text",
    "zero-shot-classification": "zero-shot",
}

PIPELINE_BLURB = {
    "text-generation": "Text-generation model published on the Hugging Face hub.",
    "text-classification": "Text classification model for labeling and routing.",
    "feature-extraction": "Embedding model for semantic search and similarity.",
    "image-classification": "Computer-vision classifier published to the hub.",
    "object-detection": "Object detection model for vision pipelines.",
    "automatic-speech-recognition": "Speech recognition model for transcription tasks.",
    "text-to-image": "Generative text-to-image model.",
    None: "Open-source model and experiment on the Hugging Face hub.",
}


def format_hf_date(iso: str) -> str:
    try:
        dt = datetime.strptime(iso[:10], "%Y-%m-%d")
    except ValueError:
        return ""
    return dt.strftime("%b %Y")


def fetch_hf_models() -> list[dict]:
    url = f"https://huggingface.co/api/models?author={HF_USER}&full=false&limit=100"
    data = json.loads(fetch(url).decode("utf-8"))
    models = []
    for m in data:
        model_id = m.get("modelId") or m.get("id", "")
        pipe = m.get("pipeline_tag")
        downloads = int(m.get("downloads") or 0)
        last = m.get("lastModified") or ""
        name = model_id.split("/", 1)[-1]
        models.append({
            "model_id": model_id,
            "name": name,
            "pipeline": pipe,
            "pipeline_label": PIPELINE_LABEL.get(pipe, pipe or "experiment"),
            "downloads": downloads,
            "updated": format_hf_date(last),
            "blurb": PIPELINE_BLURB.get(pipe, PIPELINE_BLURB[None]),
            "last_modified": last,
        })
    # newest first
    models.sort(key=lambda m: m["last_modified"], reverse=True)
    return models


# ---------- HTML builders ----------

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def build_blogs_html(posts: list[dict]) -> str:
    if not posts:
        return '<div class="blog-grid"></div>'
    cards = []
    for p in posts:
        cards.append(
            '                <a class="blog-card" href="' + esc(p["link"]) + '" target="_blank" rel="noopener">\n'
            '                    <div class="blog-meta"><span class="blog-date">' + esc(p["date"]) + '</span><span class="blog-source">Medium</span></div>\n'
            '                    <h3 class="blog-title">' + esc(p["title"]) + '</h3>\n'
            '                    <p class="blog-excerpt">' + esc(p["excerpt"]) + '</p>\n'
            '                    <span class="blog-cta">Read article <span class="arrow">→</span></span>\n'
            '                </a>'
        )
    return '<div class="blog-grid">\n' + "\n".join(cards) + "\n            </div>"


def build_models_html(models: list[dict]) -> str:
    if not models:
        return '<div class="model-grid"></div>'
    cards = []
    for m in models:
        stats_left = (
            '<span class="stat-item"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v14M5 12l7 7 7-7"/></svg>'
            + f'{m["downloads"]} downloads</span>'
        ) if m["downloads"] else '<span class="stat-item">Experiment</span>'
        stats_right = (
            f'<span class="stat-item">Updated {esc(m["updated"])}</span>' if m["updated"] else ""
        )
        cards.append(
            '                <a class="model-card" href="https://huggingface.co/' + esc(m["model_id"]) + '" target="_blank" rel="noopener">\n'
            '                    <div class="model-header">\n'
            '                        <span class="model-icon">HF</span>\n'
            '                        <span class="model-tag">' + esc(m["pipeline_label"]) + '</span>\n'
            '                    </div>\n'
            '                    <h3 class="model-name">' + esc(m["name"]) + '</h3>\n'
            '                    <p class="model-id">' + esc(m["model_id"].replace("/", " / ")) + '</p>\n'
            '                    <p class="model-desc">' + esc(m["blurb"]) + '</p>\n'
            '                    <div class="model-stats">' + stats_left + stats_right + '</div>\n'
            '                    <span class="model-cta">View on Hugging Face <span class="arrow">→</span></span>\n'
            '                </a>'
        )
    return '<div class="model-grid">\n' + "\n".join(cards) + "\n            </div>"


# ---------- Splice into index.html ----------

def splice(html_text: str, start_tag: str, end_tag: str, new_inner: str) -> str:
    pattern = re.compile(
        r"(<!--\s*" + re.escape(start_tag) + r"\s*-->)(.*?)(<!--\s*" + re.escape(end_tag) + r"\s*-->)",
        re.DOTALL,
    )
    replacement = r"\1\n            " + new_inner.replace("\\", r"\\") + r"\n            \3"
    if not pattern.search(html_text):
        raise RuntimeError(f"Markers {start_tag} / {end_tag} not found in index.html")
    return pattern.sub(lambda m: f"{m.group(1)}\n            {new_inner}\n            {m.group(3)}", html_text)


def main() -> int:
    html_text = INDEX.read_text(encoding="utf-8")

    # Fetch with per-source guards so one failing API doesn't wipe the other section.
    try:
        print("Fetching Medium posts...")
        posts = fetch_medium_posts()
        print(f"  {len(posts)} posts")
        if posts:
            html_text = splice(html_text, "BLOGS:START", "BLOGS:END", build_blogs_html(posts))
        else:
            print("  (empty result — keeping existing blog cards)")
    except Exception as exc:
        print(f"  Medium fetch failed: {exc} — keeping existing blog cards")

    try:
        print("Fetching Hugging Face models...")
        models = fetch_hf_models()
        print(f"  {len(models)} models")
        if models:
            html_text = splice(html_text, "MODELS:START", "MODELS:END", build_models_html(models))
        else:
            print("  (empty result — keeping existing model cards)")
    except Exception as exc:
        print(f"  HF fetch failed: {exc} — keeping existing model cards")

    INDEX.write_text(html_text, encoding="utf-8")
    print(f"Wrote {INDEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
