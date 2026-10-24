# Skill Library

A public, expandable directory for my published Skills, with a separate gallery
for their actual work. The homepage starts with choosing a Skill.

**[Browse Skills](https://bigtongue5566.github.io/)** · **[View works](https://bigtongue5566.github.io/?view=works)**

The directory includes [Electronic music production](https://github.com/bigtongue5566/electronic-music-production),
[motion graphics video](https://github.com/bigtongue5566/motion-graphics-video),
and [Blender landmark generator](https://github.com/bigtongue5566/blender-landmark-generator).
The gallery's featured film is **台積電｜從設計到矽晶**, a 90-second independent, unofficial
company introduction with original conceptual graphics and a new electronic soundtrack.
Every company claim maps to an official source. The page exposes the complete references,
claim-by-claim timestamps, checked dates and actual materials/rights record.
One work can credit several Skills.

## New collection — 五個場景・五種聲音

**[Listen to five new BGM demos](https://bigtongue5566.github.io/?view=works#scene-bgm)**

| Work | Context | Music |
| --- | --- | --- |
| [決勝脈衝 / Victory Circuit](https://bigtongue5566.github.io/?demo=victory-circuit) | Esports event | 174 BPM cinematic Drum & Bass |
| [向光提案 / Daybreak Proposal](https://bigtongue5566.github.io/?demo=daybreak-proposal) | Business presentation | 112 BPM clean electronic pop |
| [雲朵補給站 / Cloudside Cafe](https://bigtongue5566.github.io/?demo=cloudside-cafe) | Casual game | 104 BPM playful electronica |
| [御風入雲 / Jade Wind Ascent](https://bigtongue5566.github.io/?demo=jade-wind-ascent) | Xianxia fantasy | 80 BPM pentatonic hybrid |
| [靠近的那一秒 / Almost Yours](https://bigtongue5566.github.io/?demo=almost-yours) | Romantic moment | 72 quarter-note BPM, 6/8 |

All five are original 60-second audio works with distinct arrangements and
written endings, cover art, chapters, editable MIDI and reproducible composition
code. The [source package](examples/scene-bgm) records actual sampled instruments,
licenses and completed-file QC. Sampled instruments use GeneralUser GS 2.0.3
and FluidSynth 2.6.1; external build dependencies are acquired separately.

## 聲音的三種時間

**[Watch the three new films](https://bigtongue5566.github.io/?view=works#electronic-triptych)**

| Work | Music | Duration | Watch / listen |
| --- | --- | --- | --- |
| 靜流 / Still Current | Free-time Ambient, no drums | 32 sec | [Film](https://bigtongue5566.github.io/?demo=still-current) · [Music](https://bigtongue5566.github.io/?demo=still-current-music) |
| 相位索引 / Phase Index | 128 BPM Techno | 30 sec | [Film](https://bigtongue5566.github.io/?demo=phase-index) · [Music](https://bigtongue5566.github.io/?demo=phase-index-music) |
| 琥珀時光 / Amber Hours | 90 BPM Downtempo | 32 sec | [Film](https://bigtongue5566.github.io/?demo=amber-hours) · [Music](https://bigtongue5566.github.io/?demo=amber-hours-music) |

Made on 2026-10-24 with three different original arrangements and visual systems:
fluid contours, kinetic modules and a warm cut-paper record that unfolds and returns.
All films are 1080p/30fps and have independent playable soundtracks. The
[editable source](examples/electronic-triptych), source ZIP, licenses, actual note/cue
events, frame/sample checks and encoded ending strips are published with the works.
The homepage remains a Skill directory, with a compact new-release link to this collection.
The gallery supports optional catalog `collections` with a date and valid demo IDs.

The gallery also includes the 90-second **Form & Frequency / 聲形之間** and two 60-second studies: **Digital Pulse / 數位脈動**
(172 BPM Drum & Bass) and **Neon Drift / 霓虹漫遊** (132 BPM UK Garage).
Each has a film and a standalone soundtrack. Together with the new collection,
the directory presents seven video Demos for the motion Skill and twelve audio Demos for the music Skill.
The revised Form & Frequency uses 148 BPM Future Bass; the TSMC film uses restrained
124 BPM Minimal Piano House. Playback assets carry content-hash version queries, and chapters
match the new musical timing. Source archives retain the actual notes and automation.

The Blender Skill includes an interactive **Taipei 101 / Xinyi District** maquette,
with a separately reviewed TWTC Hall 1, four camera views and day/night lighting.
Its self-contained viewer and GLB live in `docs/demos/taipei101/`; editable Blender
source and reconstruction scripts are in `examples/taipei101/`. Interactive embeds
allow downloads so visitors can save GLB, PNG or offline HTML; the full-page link
also exposes the viewer outside the embedded layout.

## Add a Skill

Edit `docs/data/catalog.json`. Add an object to `skills`:

```json
{
  "id": "your-skill",
  "name": "你的 Skill 名稱",
  "category": "工具",
  "summary": "一句話介紹它可以完成的工作。",
  "description": "使用情境與實際交付內容。",
  "repository": "https://github.com/your-account/your-skill",
  "license": "MIT",
  "artwork": "assets/your-preview.jpg",
  "tags": ["你的關鍵字"],
  "capabilities": ["主要能力"],
  "usage": "用 $your-skill 完成一項具體工作。",
  "demoIds": []
}
```

Place optional artwork in `docs/assets/`. The site derives its list, search,
categories, and detail pages from the catalog. It has no hardcoded Skill count
or category enum. A Skill without a Demo still has a useful detail page and a
repository link. Preserve IDs when changing display names so shared URLs remain stable.

## Add a Demo

Add a record to `demos`, add its ID to each relevant Skill's `demoIds`, and add
the participating Skill IDs to the Demo's `contributors`:

```json
{
  "id": "your-demo",
  "title": "作品名稱",
  "subtitle": "Optional English title",
  "summary": "作品的重點。",
  "description": "實際製作內容。",
  "type": "video",
  "poster": "assets/your-poster.jpg",
  "src": "https://your-account.github.io/your-skill/demo.mp4",
  "source": "https://github.com/your-account/your-skill/tree/main/examples/demo",
  "rights": "https://github.com/your-account/your-skill/blob/main/RIGHTS.md",
  "facts": ["90 SEC", "1080p"],
  "contributors": [{"skillId": "your-skill", "role": "這個 Skill 的貢獻"}],
  "chapters": [{"time": 0, "title": "開始"}]
}
```

| `type` | Player | Required media |
| --- | --- | --- |
| `video` | Native video with sound and optional chapters | `src` MP4 URL/path |
| `audio` | Native audio with optional artwork and chapters | `src` audio URL/path |
| `image` | Full-size image | `src` image URL/path; optional `alt` |
| `interactive` | Sandboxed embedded page and external fallback | `src` HTTPS page |
| `link` | Preview and external project link | `src` HTTPS page |

Optional `audio`, `download`, `source`, and `rights` fields expose accompanying
music, source archives, source code, and attribution. Change `site.featuredDemoId`
to select the featured work on the gallery page. Additional works appear automatically.
Use `relatedDemoId` to link a film and its standalone soundtrack without leaving
the showcase player. It must point to another existing Demo.

For researched Demos, optional `editorialNote`, `references` and `claims` add an
independent-production notice and a reusable source section. Each reference contains
`id`, `title`, `publisher`, `url`, `scope`, `checkedDate` and optional `dataYear`.
Each claim has a readable `time` label such as `00:08–00:20`, `text` and a nonempty `sourceIds` list matching
the reference IDs. Use `?demo=your-demo#references` to link directly to the source
section. The validator rejects unknown IDs and unsafe URLs. Source citations do
not imply permission to reproduce linked materials.

All media can live in this site or in a Skill's own GitHub Pages site. The central
catalog links to the existing 90-second film to avoid duplicating large files.
Keep media sources public, retain licenses, and confirm external pages allow
embedding before using `interactive`; otherwise use `link`.

## Stable links

- `https://bigtongue5566.github.io/` — Skill directory with search and categories
- `https://bigtongue5566.github.io/?view=works` — separate Demo gallery
- `https://bigtongue5566.github.io/?skill=electronic-music-production`
- `https://bigtongue5566.github.io/?skill=motion-graphics-video`
- `https://bigtongue5566.github.io/?demo=form-and-frequency`
- `https://bigtongue5566.github.io/?demo=form-and-frequency-music`
- `https://bigtongue5566.github.io/?demo=tsmc-explained`
- `https://bigtongue5566.github.io/?demo=tsmc-explained#references`
- `https://bigtongue5566.github.io/?skill=blender-landmark-generator`
- `https://bigtongue5566.github.io/?demo=taipei101-xinyi`
- `https://bigtongue5566.github.io/demos/taipei101/index.html`

Query-string routing works directly on GitHub Pages, including refreshes and
shared links. Browser Back/Forward, keyboard navigation, media controls, and
reduced-motion preferences are supported.
The sticky navigation highlights the current section; a breadcrumb names the
current Skill or Demo. Video and audio works have distinct labels.
Skill details link back to the Skill directory; Demo pages link back to the gallery.
The header includes an accessible light/dark switch shared across all routes.
The first visit follows the system theme; a manual choice is saved locally and
used on later visits. Unsaved preferences follow system changes, and saved
choices synchronize across tabs. The switch also works with keyboard input
and when browser storage is unavailable. Theme initialization runs before CSS
to avoid a flash; native audio/video controls follow the selected color scheme.
The former `/#skills` and `/#works` links resolve to their respective new pages.
The homepage contains Skill entries; individual works appear on Skill detail
pages and in the gallery.

## Local preview and checks

No package install or build tool is required. With Python 3.12:

```powershell
uv run --no-project python -X utf8 scripts/validate_catalog.py
uv run --no-project python -X utf8 -m unittest discover -s tests -v
uv run --no-project python -m http.server 9158 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:9158/` in a browser. Opening `index.html` as a `file:` URL
does not support the catalog fetch. The validator checks IDs, cross references,
media types, URLs, chapter ordering, and the existence of local assets. It does
not prove that remote media plays; verify new media in the actual page.

GitHub Pages publishes the `docs/` directory on `main`. Validate the catalog,
inspect the preview, then commit and push the intended content updates. The
UI is shared by all entries; adding normal content does not require editing
`app.js` or `style.css`. New media formats can extend the `mediaRenderers` map
in `app.js` and the validator's supported types.

## Sources and licenses

The site code and original SVG artwork are [MIT licensed](LICENSE). Space Grotesk
is included unmodified under OFL-1.1 with the exact upstream notice at
`docs/assets/SpaceGrotesk-OFL.txt`; font source and fingerprint are documented
in the film's [source record](https://github.com/bigtongue5566/electronic-music-production/blob/main/examples/form-and-frequency/sources.json).
The film and thumbnail were created for this showcase and are documented in its
[rights record](https://github.com/bigtongue5566/electronic-music-production/blob/main/examples/form-and-frequency/RIGHTS.md).
New Skills and Demos retain their individual licenses and credits.
