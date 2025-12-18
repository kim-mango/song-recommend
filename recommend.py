# recommend.py
import json
import pandas as pd
import librosa
import numpy as np
from voice_match_core import cosine_similarity

USER_PROFILE = "user_profile.json"
TOP100 = "songs_profile.csv"


def note_to_midi(note):
    return librosa.note_to_midi(note)


def get_rank(row, fallback_rank):
    # if CSV has 'rank' use it, else use row index + 1
    if "rank" in row.index:
        return int(row["rank"])
    return int(fallback_rank)


def main():
    with open(USER_PROFILE, "r", encoding="utf-8") as f:
        user = json.load(f)

    user_min = note_to_midi(user["pitch"]["min_note"])
    user_max = note_to_midi(user["pitch"]["max_note"])
    user_tone = np.array(user["tone_vector"], dtype=float)

    df = pd.read_csv(TOP100)

    required = ["title", "artist", "min_note", "max_note", "tone_brightness", "tone_weight"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"CSV missing column: {col}")

    results = []

    for i, row in df.iterrows():
        song_min = note_to_midi(row["min_note"])
        song_max = note_to_midi(row["max_note"])

        overlap = max(0, min(user_max, song_max) - max(user_min, song_min))
        song_range = song_max - song_min
        range_score = overlap / song_range if song_range > 0 else 0.0

        # song tone vector (2D)
        song_tone = np.array([float(row["tone_brightness"]), float(row["tone_weight"])], dtype=float)

        # user tone simplified from MFCC stats (2D proxy)
        user_tone_simple = np.array([
            float(np.mean(user_tone[:13])),
            float(np.mean(user_tone[13:26]))
        ], dtype=float)

        tone_score = cosine_similarity(user_tone_simple, song_tone)

        # normalize tone score to 0..1 (prevents negatives)
        tone_score_norm = (tone_score + 1.0) / 2.0

        final_score = 0.6 * range_score + 0.4 * tone_score_norm

        results.append({
            "rank": get_rank(row, i + 1),
            "title": str(row["title"]),
            "artist": str(row["artist"]),
            "score": round(float(final_score), 3),
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    print("=== Recommended Songs (Range + Tone) ===")
    for r in results[:10]:
        print(f"[{r['score']}] #{r['rank']} {r['title']} - {r['artist']}")


if __name__ == "__main__":
    main()
