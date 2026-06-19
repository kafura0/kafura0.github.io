# kafura0.github.io — Portfolio Website

Joan Njoroge's personal portfolio. Static GitHub Pages site (single `index.html`) styled
with Materialize CSS 0.95.3 and a custom `assets/css/style.css`. No build step required
for the base site.

## Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Hosting     | GitHub Pages                        |
| CSS framework | Tailwind CSS (CDN Play)           |
| Icons       | Font Awesome 6.4.0                  |
| Animations  | AOS (Animate On Scroll) 2.3.1       |
| Typing FX   | Typed.js (vendored)                 |
| Analytics   | Google Tag Manager + GA4             |
| Auto-update | GitHub Actions + Python script      |
| Dark mode   | CSS custom properties + localStorage |

## File Structure

```
kafura0.github.io/
├── index.html                  # Single-page portfolio (all sections)
├── CLAUDE.md                   # This file
├── assets/
│   ├── css/
│   │   └── style.css           # All custom styles
│   ├── img/
│   │   ├── projects/           # Auto-downloaded preview images (managed by CI)
│   │   └── ...                 # Static images for manual project cards
│   ├── resume/
│   │   └── Joan K Njoroge CV.pdf
│   └── vendor/
│       └── typed.js/
│           └── typed.min.js
├── scripts/
│   └── update_projects.py      # Fetches portfolio-tagged repos → updates index.html
└── .github/
    └── workflows/
        └── update-projects.yml # GitHub Actions workflow (daily + on push)
```

## Auto-Update System (Private Repos → Portfolio)

The GitHub Actions workflow in `.github/workflows/update-projects.yml` runs daily and on
every push to `main`. It calls `scripts/update_projects.py`, which:

1. Authenticates with the GitHub API using a PAT stored as `PORTFOLIO_TOKEN` secret.
2. Fetches all repos (public + private) owned by `kafura0`.
3. Filters for repos with the GitHub topic **`portfolio`**.
4. For each matching repo, downloads `preview.png` (or `preview.jpg`) from the repo root
   and saves it to `assets/img/projects/{repo-name}.png`.
5. Generates a Tailwind CSS card for each repo using the repo's name, description, topics
   (as tech pills), and `homepage` field (as the demo link).
6. Injects the generated cards between the markers in `index.html`:
   ```html
   <!-- PROJECTS:AUTO:START -->
   ...generated cards...
   <!-- PROJECTS:AUTO:END -->
   ```
7. Commits any changes back to `main` with `[skip ci]` to prevent infinite loops.

### One-Time Setup (do this once)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with **`repo`** scope (full control of private repos)
3. Copy the token
4. Go to this portfolio repo → Settings → Secrets and variables → Actions
5. Click **New repository secret**, name it `PORTFOLIO_TOKEN`, paste the token

### Per-Repo Setup (do this for each project you want featured)

In each private repo you want on the portfolio:

| Step | Where | What to do |
|------|-------|------------|
| 1 | Repo → Settings → General | Add topic **`portfolio`** |
| 2 | Repo → Settings → General | Set **Website** to your live demo URL |
| 3 | Repo root | Add a **`preview.png`** (or `preview.jpg`) screenshot/mockup |
| 4 | Repo → Settings → General | Write a clear one-line **Description** |
| 5 | Repo → Settings → General | Add technology topics (e.g. `python`, `django`, `docker`) — these become the skill pills on the card |

### Trigger a Manual Run

Go to this repo → Actions → "Auto-Update Projects" → Run workflow.

## Sections (index.html)

| Section ID     | Content                                      |
|----------------|----------------------------------------------|
| `#intro`       | Hero with typed.js animation                 |
| `#about`       | Bio paragraphs                               |
| `#experience`  | Work experience cards                        |
| `#projects`    | Auto-generated (top) + manually curated cards|
| `#certificates`| Udemy / course certificates                  |
| `#skills`      | Skill pill groups                            |
| `#education`   | University cards                             |
| `#contact`     | Contact links                                |

## Editing Guide

### Add a new manual project card

Copy an existing `.project-card` div inside `#projects .grid` (below the 
`<!-- PROJECTS:AUTO:END -->` marker) and update the image, title, description, 
and links. Make sure `data-tags` includes relevant tech tags for filtering.

### Add a skill pill

Find the relevant skill group in `#skills` and add:
```html
<span class="skill-pill">Your Skill</span>
```

### Change the hero gradient

In `assets/css/style.css`, find `#intro` and edit the `background` property.

### Change the typing strings

In `index.html`, find the `Typed` initialiser near the bottom of the `<script>`:
```js
strings: ["Backend Developer", "ML Engineer", "Data Scientist", "Problem Solver"],
```

### Add a filter button for project filtering

In the `#filters` div inside `#projects`, add:
```html
<button class="filter-btn" data-filter="your-tag">Your Tag</button>
```
Matching project cards need `data-tags="your-tag"` to appear when this filter is active.

### Dark mode

The dark mode toggle saves preference to `localStorage` under the key `"dark"`.
Dark mode styles use the `.dark` class on `<body>` and `<html>`. Add dark variants
for new elements in `style.css` using `.dark .your-class {...}`.

## Common Issues

| Issue | Fix |
|-------|-----|
| Auto-update not running | Check `PORTFOLIO_TOKEN` secret exists and has `repo` scope |
| No cards generated | Ensure repos have the `portfolio` topic set in GitHub settings |
| Preview image missing | Add `preview.png` to the root of the repo |
| Demo button missing | Set the Website field in the repo's GitHub settings |
| Infinite Action loop | Commits include `[skip ci]` — should not loop; check workflow `if:` condition |
