# Assets

Visual identity of the repository. Everything in the root `README.md` is generated
from `templates/README.md.j2`, which references these files — regeneration never
touches them.

| File | Purpose |
|---|---|
| `readme/*.svg` | **Generated** — the README's pictures (the radar hero and the strong-models chart, each wide in light and dark and narrow for phones) and `radar.svg`, the hero's radar alone that the website (`index.html`) shows beside its name — drawn by `freetier-render` from the registry (`src/freetier_radar/pictures.py`); never edit them by hand |
| `social-preview.svg` | Source of the social preview card |
| `social-preview.png` | 1280×640 render for GitHub's social preview, and every Pages page's preview card (`_config.yml` defaults) |
| `favicon.svg` | The site's icon, on `index.html`, `browse.html` and every page `_layouts/default.html` serves |

The radar animates. The beam turns once every 6 seconds, driven by SMIL
(`animateTransform`) rather than a CSS transform — a rendered-as-image SVG does not
animate CSS transforms everywhere, and the beam is the one part that must move.
Each dot, a live offer, lights up as the beam reaches its bearing, on a CSS animation
whose `animation-delay` **is** that arrival time (`pictures._arrival`). Readers who ask
their system for less motion (`prefers-reduced-motion`) get no flashing and every dot
lit; the beam keeps its slow turn, which CSS cannot stop for a SMIL animation.

The social preview is a still — it is rendered to PNG — and it carries no counts,
because a number baked into an image is a claim nothing re-verifies. It is drawn in
the README hero's style: the radar's section colours, the repository's name on one
line in JetBrains Mono with *free* in the list's green, the rest in Inter.

## Social preview setup (one-time, maintainer)

GitHub has no API for this, so it's a one-click manual step:
**Settings → General → Social preview → Edit → Upload an image** → pick
`assets/social-preview.png`. To restyle it later, edit `social-preview.svg` and re-render.
The SVG names its fonts, and cairosvg takes them from the machine: install JetBrains Mono
(Bold, ExtraBold, Medium) and Inter (Regular, Medium, SemiBold) first — both SIL OFL, from
github.com/JetBrains/JetBrainsMono and github.com/rsms/inter — or a fallback font lays the
name out wider and it no longer fits on one line:

```bash
uvx --from cairosvg cairosvg assets/social-preview.svg -o assets/social-preview.png \
  --output-width 1280 --output-height 640
```
