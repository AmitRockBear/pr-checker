#!/usr/bin/env python3
import os
import json
import requests
import sys


def post_comment(repo, pr_number, token, comment_body):
    """Posts a comment to the GitHub PR."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",  # Needed for POST
    }
    payload = json.dumps({"body": comment_body})
    try:
        resp = requests.post(url, headers=headers, data=payload)
        resp.raise_for_status()  # Raise an exception for bad status codes
        print(f"✅ Comment posted successfully to PR #{pr_number}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to post comment to PR #{pr_number}.")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        else:
            print(f"Error: {e}")
        return False


def main():
    # --- Environment Variables ---
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")
    pr_number = os.getenv("PR_NUMBER")

    if not all([token, repo, event_path, pr_number]):
        print(
            "❌ Missing required environment variables (GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_EVENT_PATH, PR_NUMBER)."
        )
        sys.exit(1)

    print(f"🔍 Processing PR #{pr_number} in repository {repo}")

    # --- 1) Load PR title/body ---
    try:
        with open(event_path, "r") as f:
            event = json.load(f)
        pr = event.get("pull_request")
        if not pr:
            print(
                f"❌ Could not find 'pull_request' key in event payload at {event_path}"
            )
            sys.exit(1)

        print(f"🔖 PR Title: {pr.get('title', 'N/A')}")
        print("=" * 60)
        # Keep description short for comment, maybe?
        pr_body_snippet = (pr.get("body", "") or "No description provided.")[
            :500
        ]  # Limit length
        if len(pr.get("body", "")) > 500:
            pr_body_snippet += "\n...(truncated)"

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error reading or parsing event payload: {e}")
        sys.exit(1)

    # --- 2) Fetch changed files via REST API ---
    files_api_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    changed_files = []
    try:
        resp = requests.get(files_api_url, headers=headers)
        resp.raise_for_status()
        file_data = resp.json()
        print(f"⚙️ Found {len(file_data)} changed files:")
        for fobj in file_data:
            filename = fobj.get("filename", "Unknown file")
            status = fobj.get("status", "unknown")
            print(f"  - {filename} ({status})")
            changed_files.append(filename)  # Store filename
            # Optional: print diff patch to logs only
            # print(f"\n📝 {filename}")
            # print("-" * len(filename))
            # print(fobj.get("patch", "(no diff)"))

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch changed files for PR #{pr_number}.")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        else:
            print(f"Error: {e}")
        # Decide if you want to exit or try to comment anyway
        # sys.exit(1)

    # --- 3) Construct and Post Comment ---
    print("=" * 60)
    print("✍️ Preparing comment...")

    # Build the comment body using Markdown
    comment_body = f"### PR Analysis\n\n"
    comment_body += f"**Title:** {pr.get('title', 'N/A')}\n\n"
    # comment_body += f"**Description:**\n```\n{pr_body_snippet}\n```\n\n" # Optional: include description
    comment_body += "**Changed Files:**\n"
    if changed_files:
        for fname in changed_files:
            comment_body += f"- `{fname}`\n"
    else:
        comment_body += "_No files changed or unable to fetch file list._\n"

    comment_body += "\n----\n"
    comment_body += f"_Automated comment by workflow run [{os.getenv('GITHUB_RUN_ID')}](https://github.com/{repo}/actions/runs/{os.getenv('GITHUB_RUN_ID')})._"

    # print("\n--- Comment Preview ---")
    # print(comment_body)
    # print("--- End Comment Preview ---\n")

    post_comment(repo, pr_number, token, comment_body)


if __name__ == "__main__":
    main()
