"""Generate synthetic content catalog."""
from __future__ import annotations

import csv
import random
from pathlib import Path

from faker import Faker

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "content.csv"
SEED = 43
NUM_CONTENT = 300
GENRE_RATIOS = {
    "movie": 0.5,
    "music": 0.3,
    "podcast": 0.2,
}
DURATION_RULES = {
    "movie": (80, 160),
    "music": (3, 8),
    "podcast": (15, 90),
}


def genre_allocation() -> list[str]:
    counts: list[str] = []
    for genre, ratio in GENRE_RATIOS.items():
        genre_count = int(NUM_CONTENT * ratio)
        counts.extend([genre] * genre_count)
    while len(counts) < NUM_CONTENT:
        counts.append(random.choice(list(GENRE_RATIOS.keys())))
    random.shuffle(counts)
    return counts


def generate_content() -> list[dict[str, str]]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    faker = Faker("en_US")
    Faker.seed(SEED)
    random.seed(SEED)

    genres = genre_allocation()
    rows: list[dict[str, str]] = []
    for idx, genre in enumerate(genres, start=1):
        min_dur, max_dur = DURATION_RULES[genre]
        duration = random.randint(min_dur, max_dur)
        title = faker.sentence(nb_words=3).rstrip(".")
        rows.append(
            {
                "content_id": str(idx),
                "title": title,
                "genre": genre,
                "duration_minutes": str(duration),
            }
        )
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["content_id", "title", "genre", "duration_minutes"]
        )
        writer.writeheader()
        writer.writerows(rows)


def print_stats(rows: list[dict[str, str]]) -> None:
    genre_counts: dict[str, int] = {}
    for row in rows:
        genre_counts[row["genre"]] = genre_counts.get(row["genre"], 0) + 1
    print(f"Generated {len(rows)} content items -> {OUTPUT_FILE}")
    for genre, count in genre_counts.items():
        pct = (count / len(rows)) * 100
        print(f"  {genre}: {count} ({pct:.1f}%)")


def main() -> None:
    rows = generate_content()
    write_csv(rows)
    print_stats(rows)


if __name__ == "__main__":
    main()
