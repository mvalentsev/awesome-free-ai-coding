# Assets

Visual identity of the repository. Everything in the root `README.md` is generated
from `templates/README.md.j2`, which references these files — regeneration never
touches them.

| File | Purpose |
|---|---|
| `banner-light.svg` / `banner-dark.svg` | README hero banner, theme-switched via `<picture>` |
| `social-preview.svg` | Source of the social preview card |
| `social-preview.png` | 1280×640 render for GitHub's social preview |

## Social preview setup (one-time, maintainer)

GitHub has no API for this, so it's a one-click manual step:
**Settings → General → Social preview → Edit → Upload an image** → pick
`assets/social-preview.png`. To restyle it later, edit `social-preview.svg` and re-render:

```bash
uvx --from cairosvg cairosvg assets/social-preview.svg -o assets/social-preview.png \
  --output-width 1280 --output-height 640
```
