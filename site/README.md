# OpenCode Harness Site

This directory contains the static landing page for OpenCode Harness.

Open locally:

```powershell
Start-Process site/index.html
```

Deploy options:

- GitHub Pages through `.github/workflows/pages.yml`.
- Vercel static project with `site/` as the project root.
- Any static hosting service that can serve `index.html`, `styles.css`, and `assets/`.

The page is intentionally dependency-free.

Expected GitHub Pages URL:

```text
https://samarailly51-pixel.github.io/opencode-harness/
```

Launch assets:

- Product Hunt gallery image 1: `assets/product-hunt-gallery-1.png`
- Product Hunt gallery image 2: `assets/product-hunt-gallery-2.png`
- Square logo: `assets/product-hunt-logo.png`
- Product Hunt thumbnail: `assets/product-hunt-thumbnail.png`
- Embedded demo video: `assets/opencode-harness-demo.mp4`
- Demo video poster: `assets/opencode-harness-demo-thumbnail.png`
