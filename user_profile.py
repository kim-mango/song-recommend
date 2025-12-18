# user_profile.py
import json
import os
from voice_match_core import analyze_pitch, extract_tone_vector

SCALE_FILE = "user_recordings/scale_up.m4a"
TONE_FILE = "user_recordings/sustain_mid.m4a"
OUTPUT = "user_profile.json"


def main():
    if not os.path.exists(SCALE_FILE):
        print("scale_up.wav not found")
        return
    if not os.path.exists(TONE_FILE):
        print("sustain_mid.wav not found")
        return

    pitch = analyze_pitch(SCALE_FILE)
    tone_vec = extract_tone_vector(TONE_FILE)

    profile = {
        "pitch": pitch,
        "tone_vector": tone_vec.tolist()
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print("User profile created")
    print(pitch)


if __name__ == "__main__":
    main()
