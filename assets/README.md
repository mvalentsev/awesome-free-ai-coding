# Assets

Images and browser assets. `freetier-render` generates `readme/*.svg`;
the other files are maintained by hand.

| File | Purpose |
|---|---|
| `readme/*.svg` | **Generated** — the README's hero and model chart, each in wide and narrow layouts with both palettes inside; `radar.svg` is the website's radar. Written by `freetier-render` through [`pictures.py`](../src/freetier_radar/pictures.py); never edit by hand |
| `social-preview.svg` | Source of the social preview card |
| `social-preview.png` | Render of `social-preview.svg` at its declared dimensions, used by GitHub and the Pages preview cards (`_config.yml` defaults) |
| `favicon.svg` | The site's icon, on `index.html`, `browse.html` and every page `_layouts/default.html` serves |
| `model-name.js` | Model-name matching shared by the front-page search and the filterable table; preserves version dots |
| `search.js` | Search and filter matching shared by the home page and Browse |
| `model-sort.js` | Model ordering shared by the home page, model index, provider pages and Browse; preserves the choice in the URL and local storage |
| `model-sort.css` | Shared styling for the model-order control |

The radar beam uses CSS animation; its period is
`pictures.BEAM_PERIOD`.
Each dot, a live offer, lights up as the beam reaches its bearing, on a CSS animation
whose `animation-delay` **is** that arrival time (`pictures._arrival`). Readers who ask
their system for less motion (`prefers-reduced-motion`) get no flashing and every dot
lit; the beam stays still.

The social preview is a still — it is rendered to PNG — and it carries no counts,
so changes to the registry do not require a new upload. It is drawn in
the README hero's style: the radar's section colours, the repository's name on one
line in JetBrains Mono with *free* in the list's green, the rest in Inter.

## Social preview setup (one-time, maintainer)

Setting it is a one-click manual step:
**Settings → General → Social preview → Edit → Upload an image** → pick
`assets/social-preview.png`. To restyle it later, edit `social-preview.svg` and re-render.
The SVG names its fonts, and cairosvg takes them from the machine: install JetBrains Mono
(Bold, ExtraBold, Medium) and Inter (Regular, Medium, SemiBold) first — both SIL OFL, from
github.com/JetBrains/JetBrainsMono and github.com/rsms/inter — or a fallback font lays the
name out wider and it no longer fits on one line:

```bash
uvx --from cairosvg cairosvg assets/social-preview.svg -o assets/social-preview.png
```
