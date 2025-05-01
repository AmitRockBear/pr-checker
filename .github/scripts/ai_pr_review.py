# .github/scripts/ai_pr_review.py

import os
import sys
import argparse
import json
import requests
from typing import Dict, Any, Optional

# --- Configuration ---
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
REQUEST_TIMEOUT = 120  # Seconds

# --- Prompt Template ---
# (Keep the PROMPT_TEMPLATE as it was)
PROMPT_TEMPLATE = """
**Role:** You are an expert AI assistant specializing in code review, analysis, and adherence to coding standards.

**Task:** Analyze the provided Pull Request (PR) details (title, description, file diffs) and a set of coding standards. Generate two distinct outputs:
1.  A concise "Summary" of the PR.
2.  A "Coding Standards Violations" section detailing code that does not adhere to the provided standards.

**Input:**

1.  **PR Title:** {pr_title}
2.  **Original PR Description:**
{pr_description}
3.  **File Diffs:**
    ```diff
{file_diffs}
    ```
4.  **Coding Standards (Markdown Content):**
    ```markdown
{coding_standards_md}
    ```

**Output Requirements:**

**Part 1: PR Summary**
[... rest of template ...]

---

**Part 2: Coding Standards Violations**
[... rest of template ...]

**Generate the Summary and Coding Standards Violations now based on the provided inputs.**
"""

# --- Helper Functions ---


def build_prompt(title: str, description: str, diff: str, standards: str) -> str:
    """Builds the full prompt string for the Gemini API."""
    return PROMPT_TEMPLATE.format(
        pr_title=title,
        pr_description=description,
        file_diffs=diff,
        coding_standards_md=standards,
    )


def call_gemini_api(api_key: str, prompt: str) -> str:
    """Calls the Gemini API and returns the generated text."""
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]})
    api_url = f"{GEMINI_API_ENDPOINT}?key={api_key}"

    try:
        response = requests.post(
            api_url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        response_json: Dict[str, Any] = response.json()
        candidates = response_json.get("candidates")
        if not candidates:
            raise ValueError("Gemini API response missing 'candidates' field.")
        content = candidates[0].get("content")
        if not content:
            raise ValueError(
                "Gemini API response missing 'content' field in candidate."
            )
        parts = content.get("parts")
        if not parts:
            raise ValueError("Gemini API response missing 'parts' field in content.")
        generated_text = parts[0].get("text")
        if generated_text is None:
            raise ValueError("Gemini API response missing 'text' field in part.")
        return generated_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_details = e.response.json()
                print(
                    f"API Error Details: {json.dumps(error_details)}", file=sys.stderr
                )
            except json.JSONDecodeError:
                print(f"API Response (non-JSON): {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, IndexError) as e:
        print(f"Error parsing Gemini API response: {e}", file=sys.stderr)
        # Avoid printing potentially huge raw response here if parsing fails early
        # print(f"Raw Response JSON: {response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Generate AI PR Review using Gemini.")
    parser.add_argument("--title", required=True, help="Pull Request title")
    parser.add_argument("--description", required=True, help="Pull Request description")
    parser.add_argument("--diff", required=True, help="File diffs content")
    # --- CHANGE: Accept file path instead of content ---
    parser.add_argument(
        "--standards-file", required=True, help="Path to coding standards markdown file"
    )

    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    # --- CHANGE: Read standards file content ---
    standards_content = ""
    try:
        # Ensure correct encoding is used, utf-8 is usually safe for markdown
        with open(args.standards_file, "r", encoding="utf-8") as f:
            standards_content = f.read()
    except FileNotFoundError:
        print(
            f"Error: Coding standards file not found at '{args.standards_file}'",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(
            f"Error reading coding standards file '{args.standards_file}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    # --- End Change ---

    try:
        # Pass the read content to build_prompt
        full_prompt = build_prompt(
            args.title, args.description, args.diff, standards_content
        )
        review_comment = call_gemini_api(api_key, full_prompt)
        print(review_comment)  # Output review comment to stdout

    except Exception as e:
        print(f"Script failed during prompt building or API call: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
