"""
Auto-updates the Projects section of index.html with repos tagged `portfolio` on GitHub.

How it works:
  1. Fetches all repos (public + private) for the authenticated user.
  2. Filters for repos with the GitHub topic "portfolio".
  3. For each repo, downloads preview.png (or preview.jpg) from the repo root.
  4. Generates a Tailwind CSS card HTML block for each repo.
  5. Injects all cards between the <!-- PROJECTS:AUTO:START --> and
     <!-- PROJECTS:AUTO:END --> markers in index.html.

Required environment variables:
  GITHUB_TOKEN    - Personal Access Token with `repo` scope
  GITHUB_USERNAME - Your GitHub username (default: kafura0)

Per-repo setup (in each private repo you want featured):
  1. Add the topic "portfolio" in repo Settings → Topics
  2. Set the live demo URL in repo Settings → Website
  3. Add a preview.png (or preview.jpg) to the repo root
"""

import os
import re
import sys
import base64
import requests

TOKEN    = os.environ.get("GITHUB_TOKEN", "")
USERNAME = os.environ.get("GITHUB_USERNAME", "kafura0")

if not TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

PROJECTS_DIR  = "assets/img/projects"
INDEX_FILE    = "index.html"
MARKER_START  = "<!-- PROJECTS:AUTO:START -->"
MARKER_END    = "<!-- PROJECTS:AUTO:END -->"
FALLBACK_IMG  = "/assets/img/bg.png"


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def get_portfolio_repos():
    """Return all repos tagged with the 'portfolio' topic, sorted by most recently pushed."""
    repos = []
    page  = 1
    while True:
        url  = (
            f"https://api.github.com/user/repos"
            f"?visibility=all&affiliation=owner&sort=pushed&per_page=100&page={page}"
        )
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1

    portfolio = [r for r in repos if "portfolio" in r.get("topics", [])]
    # Most recently pushed first
    portfolio.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    print(f"Found {len(portfolio)} repo(s) tagged 'portfolio'.")
    return portfolio


def download_preview(repo_name, repo_full_name):
    """
    Download preview.png or preview.jpg from the repo root.
    Saves it to assets/img/projects/{repo_name}.{ext}.
    Returns the web path on success, or None if no preview exists.
    """
    os.makedirs(PROJECTS_DIR, exist_ok=True)

    for filename in ("preview.png", "preview.jpg"):
        url  = f"https://api.github.com/repos/{repo_full_name}/contents/{filename}"
        resp = requests.get(url, headers=HEADERS, timeout=30)

        if resp.status_code != 200:
            continue

        data = resp.json()
        ext  = filename.split(".")[-1]
        dest = f"{PROJECTS_DIR}/{repo_name}.{ext}"

        if "content" in data and data["content"]:
            # File small enough to be inlined as base64
            content = base64.b64decode(data["content"])
        elif "download_url" in data and data["download_url"]:
            # File too large for inline — fetch via download URL
            dl   = requests.get(data["download_url"], headers=HEADERS, timeout=60)
            dl.raise_for_status()
            content = dl.content
        else:
            continue

        with open(dest, "wb") as fh:
            fh.write(content)

        web_path = f"/assets/img/projects/{repo_name}.{ext}"
        print(f"  Preview saved: {web_path}")
        return web_path

    print(f"  No preview found for '{repo_name}' — using fallback image.")
    return None


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def format_title(repo_name):
    """Turn 'my-cool-project' or 'my_cool_project' into 'My Cool Project'."""
    return repo_name.replace("-", " ").replace("_", " ").title()


def build_card(repo, index):
    name        = repo["name"]
    title       = format_title(name)
    description = (repo.get("description") or "No description provided.").strip()
    homepage    = (repo.get("homepage") or "").strip()
    html_url    = repo["html_url"]
    is_private  = repo.get("private", False)
    # All topics except the 'portfolio' marker itself
    topics      = [t for t in repo.get("topics", []) if t != "portfolio"]

    img_path    = download_preview(name, repo["full_name"]) or FALLBACK_IMG
    aos_delay   = (index % 3) * 100

    # Tech pills (up to 8 topics)
    tech_pills = "".join(
        f'<span class="skill-pill">{t}</span>'
        for t in topics[:8]
    )

    # Demo button — only if a homepage URL is set
    demo_btn = ""
    if homepage:
        demo_btn = f"""\
              <a href="{homepage}" target="_blank"
                class="w-10 h-10 rounded-full bg-teal-600 text-white flex items-center justify-center hover:bg-teal-700 transition"
                aria-label="View live demo">
                <i class="fas fa-external-link-alt text-sm"></i>
              </a>"""

    # GitHub button — shown for all repos; private repos will need auth to view
    github_btn = f"""\
              <a href="{html_url}" target="_blank"
                class="w-10 h-10 rounded-full bg-gray-500 text-white flex items-center justify-center hover:bg-gray-600 transition"
                aria-label="{'Private Repo' if is_private else 'View source on GitHub'}">
                <i class="fab fa-github"></i>
              </a>"""

    card = f"""\
          <div class="project-card bg-white rounded-xl shadow-md overflow-hidden border border-gray-200"
            data-aos="fade-up" data-aos-delay="{aos_delay}"
            data-tags="{','.join(topics[:5])}">
            <img src="{img_path}" alt="{title}" class="h-48 w-full object-cover" />
            <div class="p-5">
              <h4 class="text-teal-700 font-semibold text-lg">{title}</h4>
              <p class="text-gray-600 text-sm mt-2 leading-relaxed">{description}</p>
            </div>
            <div class="px-5 pb-5 flex gap-2">
              {demo_btn}
              {github_btn}
            </div>
          </div>"""
    return card


# ---------------------------------------------------------------------------
# HTML injection
# ---------------------------------------------------------------------------

def inject_into_html(cards_html):
    with open(INDEX_FILE, "r", encoding="utf-8") as fh:
        content = fh.read()

    if MARKER_START not in content or MARKER_END not in content:
        print(
            f"ERROR: Markers not found in {INDEX_FILE}.\n"
            f"  Expected: {MARKER_START} ... {MARKER_END}",
            file=sys.stderr,
        )
        sys.exit(1)

    pattern     = re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END)
    replacement = f"{MARKER_START}\n{cards_html}\n          {MARKER_END}"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(INDEX_FILE, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    print(f"Injected {len(cards_html.splitlines())} lines into {INDEX_FILE}.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    repos = get_portfolio_repos()

    if not repos:
        print("No repos tagged 'portfolio' found. Nothing to update.")
        return

    cards     = [build_card(repo, i) for i, repo in enumerate(repos)]
    cards_html = "\n\n".join(cards)
    inject_into_html(cards_html)
    print("Done.")


if __name__ == "__main__":
    main()
