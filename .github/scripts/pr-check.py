#!/usr/bin/env python3
import os, json, requests, sys


def main():
    # 1) Load PR title/body
    event_path = os.getenv("GITHUB_EVENT_PATH")
    with open(event_path, "r") as f:
        event = json.load(f)
    pr = event["pull_request"]
    pr_number = os.getenv("PR_NUMBER")
    print(f"🔖 PR #{pr_number}: {pr['title']}")
    print("Description:\n", pr["body"])
    print("=" * 60)

    # 2) Fetch changed files via REST API
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    api_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.get(api_url, headers=headers)
    resp.raise_for_status()

    for fobj in resp.json():
        print(f"\n📝 {fobj['filename']}")
        print("-" * len(fobj["filename"]))
        print(fobj.get("patch", "(no diff)"))


if __name__ == "__main__":
    main()
