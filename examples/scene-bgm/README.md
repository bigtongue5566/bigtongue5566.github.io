# 五個場景・五種聲音

Five original 60-second BGM demonstrations made for Skill Library on 2026-10-24.

| Work | Context | Musical identity |
| --- | --- | --- |
| 決勝脈衝 / Victory Circuit | Esports event | 174 BPM cinematic D&B; broken drums, Reese/sub split, real drum withdrawal and return |
| 向光提案 / Daybreak Proposal | Business presentation | 112 BPM clean electronic pop; sampled piano, muted guitar and finger bass; space for narration |
| 雲朵補給站 / Cloudside Cafe | Casual game | 104 BPM playful electronica; pizzicato/nylon guitar and short synth answers; light syncopation |
| 御風入雲 / Jade Wind Ascent | Xianxia fantasy | 80 BPM pentatonic fantasy hybrid; flute, GM Koto, strings, generated air and sparse low drum |
| 靠近的那一秒 / Almost Yours | Romantic moment | 72 quarter-note BPM, 6/8; soft piano, nylon guitar and slow strings, no drum kit |

Each arrangement has its own motif, instrumentation, rhythm, sections and written
cadence. These are finished audition miniatures with endings, **not seamless loops**.
No copyrighted songs, copied melodies or third-party song recordings are used.

## Rebuild

Python dependencies are managed with uv:

```powershell
uv sync
uv run python compose.py victory-circuit --output work/victory-circuit
uv run python compose.py daybreak-proposal --output work/daybreak-proposal --soundfont C:/audio/GeneralUser-GS.sf2 --fluidsynth C:/audio/fluidsynth.exe
```

Use the other IDs from the table for the remaining scores. The sampled scores
require **GeneralUser GS 2.0.3** and **FluidSynth 2.6.1**, acquired separately from
their upstream projects; neither binary nor the SoundFont is bundled here.
Actual SoundFont SHA-256 and the zero-based GM programs are in `sources.json`
and each project's music metadata. All melodic sampled tracks use bank 0.

The code reuses the electronic-music-production engine's voices, note-off release
handling and audio mastering/checking. `compose.py` writes the five arrangements,
multi-instrument MIDI routing and mix. It does not call unchanged style presets.

Outputs include 48kHz/24-bit stereo WAV, 256 kbps AAC, MIDI, actual note events,
instrument provenance and QC. MIDI preserves the meter, notes and GM programs;
the custom synth voices and mix must be rebuilt with the code.

`publish.py --build <folder> --local-outputs <folder>` checks audio fingerprints
against QC, renders the original covers, copies small web assets and updates the
existing website catalog. Cover generation uses the bundled Space Grotesk font
and locally installed Microsoft JhengHei at `C:/Windows/Fonts/msjh.ttc`.
The Chinese font binary is not redistributed and may be substituted for rebuilds.

## Validation and limits

Each completed WAV/AAC is decoded and checked for exact master sample count,
stereo 48kHz format, integrated loudness, true peak, mono compatibility and ending
level. Actual note-on/chord membership is checked before rendering. Sample tails
and reflections are not fully described by MIDI gates, so these checks do not
certify subjective musical quality. No claim of actual audio audition is made.
The quiet, short gaps in the casual game's groove are intentional articulation.

All five `projects/` folders contain the actual notes, MIDI, source metadata,
configuration, mastering measurements and production notes for the published mix.
See [RIGHTS.md](RIGHTS.md) for attribution and the precise fantasy instrument names.
