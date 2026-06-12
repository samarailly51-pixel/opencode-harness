# Website Deployment

The public website is the dependency-free static site in `site/`.

## GitHub Pages

The repository includes `.github/workflows/pages.yml`, which deploys `site/` to GitHub Pages on every `master` push that changes the site.

Expected production URL:

```text
https://samarailly51-pixel.github.io/opencode-harness/
```

Manual deployment:

```powershell
gh workflow run Pages --repo samarailly51-pixel/opencode-harness
```

Check deployment status:

```powershell
gh run list --repo samarailly51-pixel/opencode-harness --workflow Pages --limit 5
```

## Vercel

Vercel is still a good option for custom domains and preview deployments. Use `site/` as the project root.

Recommended setup:

```powershell
npx vercel --cwd site
npx vercel --cwd site --prod
```

If the CLI asks for login, use the browser OAuth flow and then rerun the command.

## Static Hosting

Any static host can serve the site. The required files are:

- `site/index.html`
- `site/styles.css`
- `site/assets/`
- `site/.nojekyll` for GitHub Pages

The GitHub Pages site also serves the embedded demo video from `site/assets/opencode-harness-demo.mp4`.
