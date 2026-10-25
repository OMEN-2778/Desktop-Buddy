#!/usr/bin/env python3
"""Rebuild the 16 final BGM files and fetch the seven CC0 SFX previews.
Run from the repository root. Requires Python, numpy, scipy, ffmpeg and curl.
"""
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "AUDIO_LIBRARY"
SOURCE = LIB / "SOURCE"
BGM = LIB / "BGM"
SFX = LIB / "SFX"

GENERATORS = [
    "make_lofi_bgm_v2_long.py",
    "make_seasons_bgm.py",
    "make_park_spring_pop_v4.py",
    "make_park_remaining_seasons_final.py",
    "make_mall_crowd_rush.py",
    "make_bar_low_jazz.py",
    "make_harbor_return.py",
]

OUTPUTS = {
    "spring-白天.mp3": "home/spring-day.mp3",
    "spring-夜晚.mp3": "home/spring-night.mp3",
    "宅家四季-夏天.mp3": "home/summer-day.mp3",
    "宅家四季-夏天-夜晚.mp3": "home/summer-night.mp3",
    "宅家四季-秋天.mp3": "home/autumn-day.mp3",
    "宅家四季-秋天-夜晚.mp3": "home/autumn-night.mp3",
    "宅家四季-冬天.mp3": "home/winter-day.mp3",
    "宅家四季-冬天-夜晚.mp3": "home/winter-night.mp3",
    "公园四季-春天-前卫丰厚版.mp3": "park/park-spring.mp3",
    "公园四季-夏天-巴萨诺瓦版.mp3": "park/park-summer.mp3",
    "公园四季-秋天-室内民谣版.mp3": "park/park-autumn.mp3",
    "公园四季-冬天-极简氛围版.mp3": "park/park-winter.mp3",
    "商场-人潮高光.mp3": "mall/mall-crowd-rush.mp3",
    "酒吧-琥珀低音.mp3": "bar/bar-amber-bass.mp3",
    "酒吧-杯中日光.mp3": "bar/bar-daylight-cup.mp3",
    "海边码头-雾港归帆.mp3": "harbor/harbor-mist-return.mp3",
}

CC0_SFX = {
    "park-wind-cc0.mp3":"https://cdn.freesound.org/previews/444/444921_8439257-hq.mp3",
    "park-birds-cc0.mp3":"https://cdn.freesound.org/previews/688/688301_14970017-hq.mp3",
    "park-leaves-cc0.mp3":"https://cdn.freesound.org/previews/575/575645_2061858-hq.mp3",
    "cat-meow-cc0.mp3": "https://cdn.freesound.org/previews/110/110011_1537422-hq.mp3",
    "cat-purr-meow-cc0.mp3": "https://cdn.freesound.org/previews/412/412016_3652520-hq.mp3",
    "rain-soft-loop-cc0.mp3": "https://cdn.freesound.org/previews/595/595717_2530992-hq.mp3",
    "rain-heavy-window-cc0.mp3": "https://cdn.freesound.org/previews/720/720153_1504845-hq.mp3",
    "thunder-heavy-no-rain-cc0.mp3": "https://cdn.freesound.org/previews/446/446753_1790434-hq.mp3",
    "crowd-indoor-walla-cc0.mp3": "https://cdn.freesound.org/previews/529/529802_2905988-hq.mp3",
    "crowd-small-laugh-cc0.mp3": "https://cdn.freesound.org/previews/324/324894_2104797-hq.mp3",
}

for source in json.loads((LIB / "docs" / "REAL_FOLEY_SOURCES.json").read_text()):
    CC0_SFX[source["id"] + ".mp3"] = source["download"]

def run(command, cwd=None):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)

def main():
    BGM.mkdir(parents=True, exist_ok=True)
    SFX.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="desktop-buddy-audio-") as temporary:
        work = Path(temporary)
        for item in SOURCE.iterdir():
            if item.suffix == ".py":
                text = item.read_text(encoding="utf-8")
                text = text.replace("/mnt/agents/output/", str(work) + "/")
                (work / item.name).write_text(text, encoding="utf-8")
            else:
                shutil.copy2(item, work / item.name)
        for generator in GENERATORS:
            run(["python3", work / generator], cwd=work)
        for original, destination in OUTPUTS.items():
            source = work / original
            if not source.is_file():
                raise FileNotFoundError(f"Expected generated file: {source}")
            target = BGM / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    # These are Freesound's public HQ preview encodes, not login-only original files.
    # The corresponding sound pages and CC0 terms are recorded in docs/LICENSES.md.
    for name, url in CC0_SFX.items():
        destination = SFX / name
        if destination.is_file() and destination.stat().st_size > 1000:
            continue
        run(["curl", "-L", "--fail", "--retry", "3", "--retry-delay", "3",
             "--max-time", "120", "-o", destination, url])
        if destination.stat().st_size < 1000:
            raise RuntimeError(f"Downloaded SFX is unexpectedly small: {name}")

    missing = [name for name in CC0_SFX if not (SFX / name).is_file()]
    if missing:
        raise RuntimeError(f"Missing SFX: {missing}")
    run(["python3", LIB / "tools" / "build_game_sfx.py"])
    run(["python3", LIB / "tools" / "prepare_game_samples.py"])
    run(["python3", LIB / "tools" / "build_emotion_cues.py"])
    report = {
        "bgm_count": len(OUTPUTS),
        "source_sfx_count": len(CC0_SFX),
        "game_sfx_count": len(list((SFX / "game").glob("*.mp3"))),
        "playback_sfx_count": len(list((SFX / "game").glob("*.mp3"))) + len(CC0_SFX),
        "bgm": sorted(str(path.relative_to(LIB)) for path in BGM.rglob("*.mp3")),
        "sfx": sorted(str(path.relative_to(LIB)) for path in SFX.rglob("*.mp3")),
    }
    (LIB / "docs" / "BUILD_MANIFEST.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = []
    for path in sorted([*BGM.rglob("*.mp3"), *SFX.rglob("*.mp3")]):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(LIB)}")
    (LIB / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: {len(OUTPUTS)} BGM + {len(CC0_SFX)} CC0 SFX + game sounds", flush=True)

if __name__ == "__main__":
    main()
