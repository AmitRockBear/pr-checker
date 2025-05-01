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
Generate a response titled "**Summary**" containing the following four sections precisely as described:

1.  **Description:**
    * Review the `{pr_description}` and analyze the code changes in `{file_diffs}`.
    * Write a refined and concise description of the PR's purpose and the changes implemented. Synthesize the original intent with the actual code changes.
    * Ensure this description accurately reflects the overall contribution of the PR based on the code diffs.

2.  **Changes:**
    * Analyze the `{file_diffs}` to identify all files that have been modified.
    * Generate a Markdown table with exactly two columns: "File Path" and "Change Summary".
    * For each modified file, create a row in the table:
        * The "File Path" column should contain the full path of the modified file.
        * The "Change Summary" column should contain a brief, high-level summary (1-2 sentences) describing the *main purpose* of the changes within that specific file.
    * Ensure the table is formatted correctly using Markdown table syntax.
    * If no files were changed, state: "No file changes detected."

3.  **New Features:**
    * Based on the `{pr_description}` and `{file_diffs}`, identify and list any *new* features, functionalities, or significant enhancements introduced.
    * Present these as a bulleted list.
    * If none are identified, state: "No new features identified."

4.  **Bug Fixes:**
    * Analyze `{file_diffs}` for the *addition* of exception handling mechanisms (e.g., new `try`/`catch`, specific error checks).
    * List instances where such new exception handling was introduced.
    * Present these as a bulleted list.
    * Focus *only* on newly added exception/error handling for this section.
    * If none are identified, state: "No new exception handling identified for bug fixes."

---

**Part 2: Coding Standards Violations**
Generate a separate section titled "**Coding Standards Violations**".

* Carefully review the rules defined in the `{coding_standards_md}` input.
* Analyze the code additions and modifications within the `{file_diffs}` against these standards.
* Identify any specific lines or blocks of code in the diffs that appear to violate the provided coding standards.
* For each identified violation, provide a clear comment in a bulleted list format:
    * **File:** `{File Path where violation occurred}`
    * **Line(s):** `{Approximate line number(s) in the diff where violation occurred}`
    * **Violation:** `{Brief description of the violated standard from the standards document}`
    * **Code:**
        ```code
        {Relevant line(s) of code from the diff}
        ```
* If no violations are found after checking the diffs against the standards document, state: "No coding standards violations identified in the changed code."

**Instructions:**

* First, generate the complete "Summary" (Part 1) with its four sections in the specified order.
* Then, insert a separator (`---`).
* Finally, generate the complete "Coding Standards Violations" section (Part 2).
* Base your analysis primarily on the provided `{file_diffs}` and `{coding_standards_md}`. Use `{pr_title}` and `{pr_description}` for context.
* Format the "Changes" section in the Summary as a valid Markdown table.
* Use bullet points for lists within "New Features", "Bug Fixes", and "Coding Standards Violations".
* Be objective and specific, especially when detailing violations. Reference the standard and the code.
* Do not include any preamble or concluding remarks outside the specified structure.

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

    full_prompt = None  # Initialize variable
    try:
        # Pass the read content to build_prompt
        full_prompt = build_prompt(
            args.title, args.description, args.diff, standards_content
        )
    except Exception as e:
        print(f"Script failed during prompt building: {e}", file=sys.stderr)
        sys.exit(1)

    # Only proceed if prompt building was successful
    if full_prompt:
        try:
            review_comment = call_gemini_api(api_key, full_prompt)
            print(review_comment)  # Output review comment to stdout
        except Exception as e:
            # call_gemini_api already prints detailed errors and exits,
            # but we catch here just in case something unexpected happens
            # before or after the call within this try block.
            print(f"Script failed during API call execution: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
