#!/usr/bin/env python3
"""Refresh the "Recently shipped" list in README.md from Aman035's latest public repos.

A repo counts as "shipped" when it is not a fork, not archived, and has a live
homepage. Descriptions come from the repo, or from notes.json when one is set.
"""
import json, os, re, urllib.request

USER = "Aman035"
COUNT = 5
START, END = "<!-- shipped:start -->", "<!-- shipped:end -->"

def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?type=owner&sort=created&direction=desc&per_page=100",
        headers={"Accept": "application/vnd.github+json",
                 **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {})})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def main():
    notes = json.load(open("notes.json")) if os.path.exists("notes.json") else {}
    shipped = [r for r in fetch_repos()
               if not r["fork"] and not r["archived"] and r.get("homepage") and r["name"] != USER
               and r["name"] not in notes.get("_hide", [])][:COUNT]
    lines = []
    for r in shipped:
        desc = notes.get(r["name"]) or r.get("description") or ""
        when = r["created_at"][:7]
        line = f"- **[{r['name']}]({r['html_url']})**"
        if desc:
            line += f" · {desc.rstrip('.')}"
        line += f" · [live]({r['homepage']}) <sub>{when}</sub>"
        lines.append(line)
    readme = open("README.md").read()
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 START + "\n" + "\n".join(lines) + "\n" + END, readme, flags=re.S)
    if new != readme:
        open("README.md", "w").write(new)
        print("README updated")
    else:
        print("No change")

if __name__ == "__main__":
    main()
