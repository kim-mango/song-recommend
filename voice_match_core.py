# voice_match_core.py
import librosa
import numpy as np


def analyze_pitch(path, fmin_note="C2", fmax_note="C6"):
    y, sr = librosa.load(path, sr=22050, mono=True)

    fmin = librosa.note_to_hz(fmin_note)
    fmax = librosa.note_to_hz(fmax_note)

    f0 = librosa.yin(y, fmin=fmin, fmax=fmax)
    f0 = f0[np.isfinite(f0)]
    f0 = f0[f0 > 0]

    if len(f0) == 0:
        raise ValueError("No valid pitch found")

    min_hz = float(np.percentile(f0, 5))
    max_hz = float(np.percentile(f0, 95))
    median_hz = float(np.median(f0))

    return {
        "min_hz": min_hz,
        "max_hz": max_hz,
        "median_hz": median_hz,
        "min_note": librosa.hz_to_note(min_hz),
        "max_note": librosa.hz_to_note(max_hz),
    }


def extract_tone_vector(path):
    y, sr = librosa.load(path, sr=22050, mono=True)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_std = mfcc.std(axis=1)

    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0].mean()
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0].mean()
    zcr = librosa.feature.zero_crossing_rate(y)[0].mean()

    vec = np.concatenate([
        mfcc_mean,
        mfcc_std,
        np.array([spec_centroid, spec_bw, zcr])
    ])

    vec = (vec - vec.mean()) / (vec.std() + 1e-8)
    return vec.astype(float)


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
