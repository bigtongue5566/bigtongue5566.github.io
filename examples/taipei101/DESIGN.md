# Taipei 101 / Xinyi maquette

Visual thesis: a warm paper architectural maquette, with a jade tower and calm typography; the city is the main visual.

Content plan: a full-canvas model with a brief title; four views reveal the tower, street blocks and plan; the model dialog contains sources and limits; GitHub and downloadable model/standalone HTML are the final actions.

Interaction thesis: a short model entrance, smooth camera moves between landmarks, and restrained scene-panel reveals. Reduced-motion settings disable entrance and camera animations. Rotation starts only through user input or the explicit auto-orbit switch.

## References observed on 2026-10-10

| Source | Observation | Use |
| --- | --- | --- |
| [Google Earth](https://earth.google.com/web/search/Taipei+101/@25.03395,121.56447,90a,1600d,35y,0h,55t,0r) | 3D overview, north-up plan and opposite oblique view; visible imagery date 2018/11 | Tower and connected podium; green roofs, TICC terraces, Hyatt stepped wings, road/block layout. The initial overview did not resolve Hall 1's covered centre; see the focused review below. |
| [Google Maps Street View](https://www.google.com/maps/@?api=1&map_action=pano&pano=DJx8RfyhF9l9h6cosRiC3g&viewpoint=25.0323288,121.5653816&heading=319&pitch=21&fov=75) | 14 Songzhi Road; visible capture date 2025/01, panorama DJx8RfyhF9l9h6cosRiC3g | Flared tower segments, curtain-wall grid, pale cornices and round coin ornaments |
| [C.Y. Lee & Partners](https://www.cylee.com/project/Taipei-101?lang=tw) | Published 508 m height; bamboo / eight-floor motif | Height anchor and tower vocabulary |
| [Council on Vertical Urbanism](https://www.skyscrapercenter.com/building/taipei-101/117) | Published tip and architectural height 508 m | Independent height check |
| [Taipei World Trade Center](https://www.twtc.com.tw/about) | Hall 1 documented as seven storeys; official complex exterior and first-floor interior photos | Hall identity, storey count and cross-check that the exhibition centre is covered |

No Earth ruler measurements were made. Google images are observational references, not included textures, preview photos or extracted meshes. All geometry, colours and landscaping are newly generated. Preview images are renders of this model.

## Hall 1 correction / individual building review

The first model wrongly turned Hall 1 into four equal low wings around an open grass courtyard. The street-block overview was insufficient to resolve the dark central roof, and the previous file checks did not validate this neighbouring building's appearance. This public demo includes the corrected covered-roof version.

| Building / part | Actually viewed reference | Visible evidence / adopted geometry | Limits |
| --- | --- | --- | --- |
| Hall 1 outline / roof | Earth focused search for 台北世界貿易中心展覽大樓, north-up plan at 25.0339262,121.56177555 | Broad near-square outline, green terrace roofs surrounding a continuous dark rectangular central roof | Footprint is a visual estimate, not a ruler measurement |
| Hall 1 south / roof | [Earth south oblique](https://earth.google.com/web/search/台北世界貿易中心展覽大樓/@25.0339262,121.56177555,7.23a,500d,35y,0h,45t,0r), imagery 2018/11/11 | Shallow barrel vault with scattered roof lights; repeated stepped wings, projecting capped piers, dark recessed central entrance; covered bridge to 101 podium | Exterior widths, canopy slope and elevations approximate |
| Hall 1 west | Earth heading 90, tilt 45, distance 500 | Multiple green terrace levels and projecting piers | Trade Building partly occludes the western facade; that hidden facade is not treated as fully checked |
| Hall 1 north | Earth heading 180, tilt 55, distance 680 | Curved roof end and covered central roof; upper northern green strip | Hyatt occludes lower northern facade; simplified window arrangement remains approximate |
| Hall 1 east | Earth heading 270, tilt 45, distance 600 | Eastern stepped massing and side terraces | 101 partly occludes the central roof; south view resolves it |
| Hall 1 centre / floors | [TWTC introduction](https://www.twtc.com.tw/about), official exterior and [interior photo](https://www.twtc.com.tw/img/floor1/1F展場圖_1.JPG), viewed 2026-10-10 | Seven storeys total: first-floor exhibition space and second-to-seventh-floor trading spaces; covered centre, no invented grass court | Official photo capture dates unknown; no interior is modelled |

Model adopts an approximately 216 m wide stepped footprint, about 210 m north-to-south before the entrance canopy, seven-storey stepped wings, and an approximately 84 x 126 m central roof. Upper green roof level ~39 m and vault crown ~47 m are estimates. These are chosen model dimensions, not surveyed measurements. Roof closure and setback relationships are supported by the focused views; exact dimensions and obscured facade details remain approximate.

Review images use daylight from the south and west, plus plan, before validating night lighting. A geometry regression check samples the exported roof over the central region and a west/east roof profile: the old open courtyard fails this check. File integrity checks are recorded separately from this shape review.

## Geometry and confidence

Metres, Blender X=east / Y=north / Z=up. The tower tip is anchored to 508 m; the eight flared sections and curtain-wall grid are recognisable abstractions. The roofed west-north shopping podium is connected to the tower.

Surrounding footprints and heights are approximate, based on observed plan and oblique views. Named landmarks are TWTC Hall 1, Taipei International Convention Center, International Trade Building, Grand Hyatt Taipei and Taipei City Hall. Other blocks retain a simplified skyline; they are deliberately unnamed. Trees and vehicles establish scale. This is an exterior demo, not a survey, engineering model, current cadastral map, or representation of underground/indoor spaces.

The Earth imagery and street panorama represent different capture dates. They do not establish that every neighbouring building has the same appearance in 2026. Exported meshes retain `layer`, `landmark` and `approximate` metadata; the web app uses these fields for display controls.

Night includes separately modelled emissive window panes, cornice strips, lamp heads and plaza rings. They follow facade planes and turn on only in the night preset, with a bloom/output pass at a capped resolution. Patterns and lighting colour are illustrative. The Blender daylight render hides the Lighting meshes; exported GLB retains `night_only` metadata for the viewer.

## Delivery

Blender source builds batched meshes without third-party textures. GLB has no external buffers; HTML embeds that GLB and its bundled Three.js runtime. The interactive site is published under `docs/demos/taipei101/` on the shared Skill Library GitHub Pages site. No API keys, analytics, external fonts or runtime CDN requests are required. The only external navigation is through source/GitHub links chosen by the visitor.
