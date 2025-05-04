# this module is responsible to store the output from the files

import json
import os
from datetime import datetime
from typing import Any
import re

# Create storage directories if they don’t exist
BASE_DIRS = {
    "scraped_data": "storage/scraped_data",
    "ideas": "storage/ideas",
    "blogs": "storage/blogs"
}

for path in BASE_DIRS.values():
    os.makedirs(path, exist_ok=True)


def _get_timestamped_filename(prefix: str, ext: str = "json") -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return f"{prefix}_{date_str}.{ext}"


def save_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved: {path}")


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# SCRAPER
def save_scraped_data(data: list[dict]) -> None:
    filename = _get_timestamped_filename("scraped")
    path = os.path.join(BASE_DIRS["scraped_data"], filename)
    save_json(data, path)


# IDEA GENERATION
def save_ideas(ideas: list[dict]) -> None:
    filename = _get_timestamped_filename("ideas")
    path = os.path.join(BASE_DIRS["ideas"], filename)
    save_json(ideas, path)


# BLOG GENERATION

def save_blog(idea_title: str, content: dict) -> None:
    # Sanitize title to remove problematic characters
    sanitized_title = re.sub(r"[^\w\s-]", "", idea_title)  # Remove special chars
    sanitized_title = re.sub(r"\s+", "_", sanitized_title)  # Replace spaces with underscores
    sanitized_title = sanitized_title.strip().lower()

    # Truncate to avoid long filenames (max 100 chars)
    if len(sanitized_title) > 100:
        sanitized_title = sanitized_title[:100]

    filename = f"blog_{sanitized_title}.json"
    path = os.path.join(BASE_DIRS["blogs"], filename)
    save_json(content, path)




def load_latest_scraped_data() -> list[dict]:
    files = sorted(os.listdir(BASE_DIRS["scraped_data"]), reverse=True)
    if not files:
        raise FileNotFoundError("No scraped data found.")
    path = os.path.join(BASE_DIRS["scraped_data"], files[0])
    return load_json(path)


def load_latest_ideas() -> list[dict]:
    files = sorted(os.listdir(BASE_DIRS["ideas"]), reverse=True)
    if not files:
        raise FileNotFoundError("No idea data found.")
    path = os.path.join(BASE_DIRS["ideas"], files[0])
    return load_json(path)
