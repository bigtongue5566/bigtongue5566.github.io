# Sources and rights

The five compositions, arrangements and cover graphics were created for
bigtongue5566 Skill Library. No third-party songs, vocal recordings, logos,
photographs or game assets are used. Original code and graphics are MIT licensed;
the copied electronic-music-production engine retains its own MIT notice.

## Instrument samples

- [GeneralUser GS](https://github.com/mrbumpy409/GeneralUser-GS), Chris / S. Christian
  Collins, v2.0.3. The complete unmodified license is in
  [GeneralUser-GS-LICENSE.txt](GeneralUser-GS-LICENSE.txt). It allows private and
  commercial music creation. Only rendered instrumental audio is published;
  the SF2 is not part of this source download.
- [FluidSynth 2.6.1](https://github.com/FluidSynth/fluidsynth/releases/tag/v2.6.1)
  renders the sampled MIDI parts. Its executable is an external build dependency,
  not bundled. Actual routing uses bank 0 and these zero-based programs:

| Track | Actual sampled programs |
| --- | --- |
| Victory Circuit | None; original oscillator/noise synthesis |
| Daybreak Proposal | 0 Acoustic Grand Piano; 28 Muted Guitar; 33 Fingered Bass |
| Cloudside Cafe | 45 Pizzicato Strings; 24 Nylon Guitar |
| Jade Wind Ascent | 73 Flute; 107 Koto; 48 Strings |
| Almost Yours | 0 Acoustic Grand Piano; 24 Nylon Guitar; 49 Slow Strings |

The fantasy work uses GM **Koto** for a zither-like texture and **Flute** for
the melodic line. These are not guzheng, guqin, dizi, xiao, erhu or live Chinese
instrument recordings. The main melody uses D-major pentatonic pitches; its
supporting harmony also uses notes from the broader D-major key.

All other sound is original synthesis: drums/noise, Reese/sub bass, short organ
derived synth phrases, sustained pads and filtered early reflections. No
commercial synthesizer preset pack or third-party song sample was imported.
Actual SoundFont and engine file fingerprints are recorded in `sources.json`.

## Covers

The five cover designs are original procedural illustrations in `publish.py`.
[Space Grotesk](https://github.com/floriankarsten/space-grotesk) is bundled under
SIL OFL 1.1 with its original notice at `fonts/SpaceGrotesk-OFL.txt`. Locally
installed Microsoft JhengHei is used to render Chinese cover text; its font file
is not bundled or offered for download.

## Method references

The electronic-music-production skill's production guidance informed rhythm,
foreground/background contrast, articulation and mix. Specific external source
materials were not copied into the compositions. The implementation itself and
the actual notes are the reviewable record; measurements are not a subjective
listening endorsement.
