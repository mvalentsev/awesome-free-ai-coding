# Assets

Visual identity of the repository. Everything in the root `README.md` is generated
from `templates/README.md.j2`, which references these files — regeneration never
touches them.

| File | Purpose |
|---|---|
| `banner-light.svg` / `banner-dark.svg` | README hero banner, theme-switched via `<picture>` |
| `social-preview.svg` | Source of the social preview card |
| `social-preview.png` | 1280×640 render for GitHub's social preview |

The banners animate. The beam turns once every 6 seconds, driven by SMIL
(`animateTransform`) rather than a CSS transform — a rendered-as-image SVG does not
animate CSS transforms everywhere, and the beam is the one part that must move.
Each blip then lights up as the beam reaches its bearing, on a CSS animation whose
`animation-delay` **is** that arrival time: moving a blip means recomputing its delay
as `((atan2(dy, dx) + 45°) mod 360°) / 60°` seconds. Readers who ask their system for
less motion (`prefers-reduced-motion`) get no flashing and every contact lit; the beam
keeps its slow turn, which CSS cannot stop for a SMIL animation.

The social preview is a still — it is rendered to PNG — and it carries no counts,
because a number baked into an image is a claim nothing re-verifies.

## Social preview setup (one-time, maintainer)

GitHub has no API for this, so it's a one-click manual step:
**Settings → General → Social preview → Edit → Upload an image** → pick
`assets/social-preview.png`. To restyle it later, edit `social-preview.svg` and re-render:

```bash
uvx --from cairosvg cairosvg assets/social-preview.svg -o assets/social-preview.png \
  --output-width 1280 --output-height 640
```
