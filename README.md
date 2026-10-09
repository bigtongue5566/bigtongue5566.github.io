# Skill Library

A public, expandable directory for my published Skills, with a separate gallery
for their actual work. The homepage starts with choosing a Skill.

**[Browse Skills](https://bigtongue5566.github.io/)** · **[View works](https://bigtongue5566.github.io/?view=works)**

The first entries are [EDM music production](https://github.com/bigtongue5566/edm-music-production)
and [motion graphics video](https://github.com/bigtongue5566/motion-graphics-video).
The gallery's featured film, **Form & Frequency / 聲形之間**, is a newly produced 90-second
original motion-and-music study. Its soundtrack has a separate audio Demo.
One work can credit several Skills.

The gallery also includes two new 60-second studies: **Digital Pulse / 數位脈動**
(128 BPM Progressive House) and **Neon Drift / 霓虹漫遊** (96 BPM Synthwave).
Each has a film and a standalone soundtrack. The directory currently presents
three video Demos for the motion Skill and three audio Demos for the music Skill.

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

All media can live in this site or in a Skill's own GitHub Pages site. The central
catalog links to the existing 90-second film to avoid duplicating large files.
Keep media sources public, retain licenses, and confirm external pages allow
embedding before using `interactive`; otherwise use `link`.

## Stable links

- `https://bigtongue5566.github.io/` — Skill directory with search and categories
- `https://bigtongue5566.github.io/?view=works` — separate Demo gallery
- `https://bigtongue5566.github.io/?skill=edm-music-production`
- `https://bigtongue5566.github.io/?skill=motion-graphics-video`
- `https://bigtongue5566.github.io/?demo=form-and-frequency`
- `https://bigtongue5566.github.io/?demo=form-and-frequency-music`

Query-string routing works directly on GitHub Pages, including refreshes and
shared links. Browser Back/Forward, keyboard navigation, media controls, and
reduced-motion preferences are supported.
The sticky navigation highlights the current section; a breadcrumb names the
current Skill or Demo. Video and audio works have distinct labels.
Skill details link back to the Skill directory; Demo pages link back to the gallery.
The former `/#skills` and `/#works` links resolve to their respective new pages.
The homepage contains Skill entries; individual works appear on Skill detail
pages and in the gallery.

## Local preview and checks

No package install or build tool is required. With Python 3.12:

```powershell
python -X utf8 scripts/validate_catalog.py
python -X utf8 -m unittest discover -s tests -v
python -m http.server 9158 --bind 127.0.0.1 --directory docs
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
in the film's [source record](https://github.com/bigtongue5566/edm-music-production/blob/main/examples/form-and-frequency/sources.json).
The film and thumbnail were created for this showcase and are documented in its
[rights record](https://github.com/bigtongue5566/edm-music-production/blob/main/examples/form-and-frequency/RIGHTS.md).
New Skills and Demos retain their individual licenses and credits.
