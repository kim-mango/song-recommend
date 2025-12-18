# build_song_db.py
import os
import re
import librosa
import numpy as np
import pandas as pd


AUDIO_DIR = "audio"
OUTPUT_CSV = "songs_profile.csv"


def clamp01(x):
    return max(0.0, min(1.0, float(x)))


def parse_filename(filename):
    """
    Extract title and artist from filename.
    Supported:
      - title(artist).wav
      - title - artist.mp3
    """
    name = os.path.splitext(filename)[0]

    m = re.match(r"(.+?)\((.+?)\)$", name)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    if " - " in name:
        parts = name.split(" - ", 1)
        return parts[0].strip(), parts[1].strip()

    return name.strip(), "Unknown"


def analyze_pitch(path, fmin_note="C2", fmax_note="C6"):
    y, sr = librosa.load(path, sr=22050, mono=True)

    fmin = librosa.note_to_hz(fmin_note)
    fmax = librosa.note_to_hz(fmax_note)

    f0 = librosa.yin(y, fmin=fmin, fmax=fmax)
    f0 = f0[np.isfinite(f0)]
    f0 = f0[f0 > 0]

    if len(f0) == 0:
        raise ValueError("No valid pitch")

    min_hz = float(np.percentile(f0, 5))
    max_hz = float(np.percentile(f0, 95))

    return {
        "min_note": librosa.hz_to_note(min_hz),
        "max_note": librosa.hz_to_note(max_hz),
    }


def extract_tone_summary(path):
    y, sr = librosa.load(path, sr=22050, mono=True)

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0].mean()
    brightness = clamp01((centroid - 800.0) / (3500.0 - 800.0))

    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)

    low = S[(freqs >= 80) & (freqs <= 400)]
    full = S[(freqs >= 80) & (freqs <= 6000)]

    ratio = float(np.mean(low) / (np.mean(full) + 1e-9))
    weight = clamp01((ratio - 0.05) / (0.35 - 0.05))

    return round(brightness, 3), round(weight, 3)


def main():
    if not os.path.exists(AUDIO_DIR):
        print("audio folder not found")
        return

    rows = []
    idx = 1

    for fname in os.listdir(AUDIO_DIR):
        if not fname.lower().endswith((".wav", ".mp3")):
            continue

        path = os.path.join(AUDIO_DIR, fname)
        title, artist = parse_filename(fname)

        try:
            pitch = analyze_pitch(path)
            brightness, weight = extract_tone_summary(path)

            rows.append({
                "id": idx,
                "title": title,
                "artist": artist,
                "audio_path": path,
                "min_note": pitch["min_note"],
                "max_note": pitch["max_note"],
                "tone_brightness": brightness,
                "tone_weight": weight,
            })

            print(f"OK: {title} - {artist}")
            idx += 1

        except Exception as e:
            print(f"FAIL: {fname} -> {e}")

    if not rows:
        print("No audio files processed")
        return

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nCreated {OUTPUT_CSV} ({len(rows)} songs)")


if __name__ == "__main__":
    main()
