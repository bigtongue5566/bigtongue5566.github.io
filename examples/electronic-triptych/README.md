# Sound / Form — 聲音的三種時間

Three original electronic miniatures and matching motion films, made on 2026-10-24.
Each has a separate arrangement, palette, focal object, movement language and ending.

| Work | Sound | Image | Duration |
| --- | --- | --- | --- |
| Still Current / 靜流 | Free-time Ambient; additive clouds and filtered air, no drums | Mint contour field absorbs a warm moving core, opens, then settles | 32 s |
| Phase Index / 相位索引 | 128 BPM Techno; pulse motif, sub, drums and progressive brightness | Acid/ink modules assemble, rotate, compress and combine | 30 s |
| Amber Hours / 琥珀時光 | 90 BPM Downtempo; laid-back broken beat, rounded keys and sub | Warm cut-paper record rotates, unfolds into sectors and returns home | 32 s |

The films use actual composed event times from `work/cues.json`. Still Current
uses seconds and harmonic/texture changes, with no fabricated beat grid. A fixed
60 BPM MIDI reference is retained only for note-file transport. The other films
use their actual kick/snare/key onsets. This is an original small collection,
not a claim that these three works represent every electronic genre.

## Rebuild

Python is managed with uv. From this directory, use an empty output directory for
each new build. The renderer includes Space Grotesk and does not need system fonts.
No third-party recording, image, company material or paid instrument is downloaded.

```text
uv sync
uv run python compose.py still-current --output ./work/still-current
uv run python render.py --project ./work/still-current --mode preview
uv run python render.py --project ./work/still-current --mode study
uv run python render.py --project ./work/still-current --mode render
uv run python finish.py --project ./work/still-current
```

Replace `still-current` with `phase-index` or `amber-hours` for the other works.
`projects/` preserves published configurations, note events, timing cues and QC.
`compose.py` contains the custom compositions; the general audio utilities are
copied from the companion music skill in `engine/`, retaining their MIT license.
`render.py` is original Skia animation. `video_pipeline/` preserves the reviewed
motion skill's audio-import/mux/check helpers and their license.

The finisher uses a finished WAV master with its source metadata and skips a
second loudness master. It converts to 48 kHz stereo PCM/AAC for delivery, then
copies the picture stream into H.264/AAC MP4. AAC is a lossy encoding; untouched
gain does not mean bit-identical audio samples after encoding.

MIDI records pitched and drum note events but cannot reproduce additive timbre,
filtered noise, effects or automation. The Python sources rebuild these features.
The original WAV master is retained in the build's outputs. The website publishes
the MP4, AAC, source ZIP, stills and readable QC/provenance alongside the source.

## Validation and limits

The published builds verify exact video frame count and WAV sample count, complete
AAC/MP4 decode, loudness, true peak, mono fold-down, ending energy, source hashes,
unchanged picture packets during mux, encoded palette, arbitrary-time render
determinism and the final actual compositional onset against the ending cue.
Keyframes, motion strips and encoded ending strips were exported for visual review.
These objective checks do not certify musical quality or mean the audio was auditioned.

See [RIGHTS.md](RIGHTS.md), [TREATMENT.md](TREATMENT.md) and [sources.json](sources.json).
