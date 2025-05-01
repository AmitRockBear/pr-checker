# .github/scripts/ai_pr_review.py

import os
import sys
import argparse
import json
import requests
import re  # Import regular expressions
from typing import Dict, Any, List, Optional, TypedDict


# --- Type Hinting for Violations ---
class Violation(TypedDict):
    file: str
    line: int  # Target line number within the file
    message: str  # The full violation message including code block


# --- Configuration ---
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
REQUEST_TIMEOUT = 180  # Increased timeout slightly

# --- Prompt Template (No changes needed here) ---
PROMPT_TEMPLATE = """
**Role:** You are an expert AI assistant specializing in code review, analysis, and adherence to coding standards.

**Task:** Analyze the provided Pull Request (PR) details (title, description, file diffs) and a set of coding standards. Generate two distinct outputs structured EXACTLY as requested below:
1.  A concise "Summary" section.
2.  A "Coding Standards Violations" section.

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
Generate a response starting *exactly* with "**Summary**" on its own line, followed by the content containing these four sections:

1.  **Description:**
    * Review the `{pr_description}` and analyze the code changes in `{file_diffs}`.
    * Write a refined and concise description of the PR's purpose and the changes implemented.
    * Ensure this description accurately reflects the overall contribution based on the code diffs.

2.  **Changes:**
    * Analyze `{file_diffs}` for modified files.
    * Generate a Markdown table with columns "File Path" and "Change Summary".
    * For each modified file, add a row summarizing the main purpose of changes (1-2 sentences).
    * If no files changed, state: "No file changes detected."

3.  **New Features:**
    * Identify and list *new* features/enhancements from `{pr_description}` and `{file_diffs}` as a bulleted list.
    * If none, state: "No new features identified."

4.  **Bug Fixes:**
    * Analyze `{file_diffs}` for *added* exception handling (e.g., new `try`/`catch`).
    * List instances as a bulleted list.
    * If none, state: "No new exception handling identified for bug fixes."

---
**(Exactly one separator line like this)**
---

**Part 2: Coding Standards Violations**
Generate a section starting *exactly* with "**Coding Standards Violations**" on its own line.

* Review rules in `{coding_standards_md}` against `{file_diffs}`.
* Identify violations in additions/modifications.
* For EACH violation, provide a bullet point `*` followed *exactly* by:
    * **File:** `path/to/violated/file.ext` (Just the path)
    * **Line(s):** `N` (A single line number in the changed file where the violation primarily occurs)
    * **Violation:** `Brief description of the standard violated.`
    * **Code:**
        ```code
        Relevant line(s) of code from the diff showing the violation
        ```
* If no violations are found, state *only*: "No coding standards violations identified in the changed code."

**Instructions:**
* Adhere strictly to the specified output structure and headers ("**Summary**", "**Coding Standards Violations**", `---` separator, bullet points, bolded fields).
* Output only the requested sections, nothing else.
* The "Line(s):" field MUST contain a single integer representing the line number in the file where the violation occurs.

**Generate the structured Summary and Coding Standards Violations now.**
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
    payload = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            # Optional: Add safety settings if needed
            # "safetySettings": [
            #     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            #     # ... other categories
            # ]
        }
    )
    api_url = f"{GEMINI_API_ENDPOINT}?key={api_key}"

    try:
        response = requests.post(
            api_url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        response_json: Dict[str, Any] = response.json()

        # Enhanced error checking for blocked content or missing fields
        if not response_json.get("candidates"):
            finish_reason = response_json.get("promptFeedback", {}).get("blockReason")
            if finish_reason:
                raise ValueError(
                    f"Gemini API call failed or blocked. Reason: {finish_reason}"
                )
            else:
                raise ValueError(
                    "Gemini API response missing 'candidates' field and no block reason found."
                )

        content = response_json["candidates"][0].get("content")
        if not content or not content.get("parts"):
            # Check finish reason in candidate if available
            finish_reason = response_json["candidates"][0].get("finishReason")
            if finish_reason and finish_reason != "STOP":
                raise ValueError(
                    f"Gemini API candidate finished unexpectedly. Reason: {finish_reason}"
                )
            raise ValueError(
                "Gemini API response missing 'content' or 'parts' field in candidate."
            )

        generated_text = content["parts"][0].get("text")
        if generated_text is None:  # Check for None explicitly
            raise ValueError("Gemini API response missing 'text' field in part.")

        return generated_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        # ... (rest of existing error handling) ...
        sys.exit(1)
    except (ValueError, KeyError, IndexError) as e:
        print(f"Error processing Gemini API response: {e}", file=sys.stderr)
        # ... (rest of existing error handling) ...
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """Parses the AI's response into summary and violations."""
    summary = ""
    violations: List[Violation] = []

    # Split based on the main sections and separator
    parts = re.split(r"\n---\n", response_text, maxsplit=1)

    summary_section = ""
    violations_section = ""

    if len(parts) > 0:
        # Find **Summary** reliably, handling potential leading/trailing whitespace
        summary_match = re.search(
            r"^\s*\*\*Summary\*\*\s*\n(.*?)$", parts[0], re.DOTALL | re.MULTILINE
        )
        if summary_match:
            summary_section = summary_match.group(1).strip()
        else:
            # Fallback: assume the first part is the summary if title is missing
            print(
                "Warning: Could not find '**Summary**' header. Assuming first part is summary.",
                file=sys.stderr,
            )
            summary_section = parts[0].strip()

    if len(parts) > 1:
        # Find **Coding Standards Violations** reliably
        violations_match = re.search(
            r"^\s*\*\*Coding Standards Violations\*\*\s*\n(.*?)$",
            parts[1],
            re.DOTALL | re.MULTILINE,
        )
        if violations_match:
            violations_section = violations_match.group(1).strip()
        else:
            # Fallback: assume second part is violations if title missing
            print(
                "Warning: Could not find '**Coding Standards Violations**' header. Assuming second part is violations.",
                file=sys.stderr,
            )
            violations_section = parts[1].strip()

    # Set the summary (even if empty)
    summary = summary_section

    # Check if violations section indicates no violations
    no_violations_msg = "No coding standards violations identified in the changed code."
    if violations_section and no_violations_msg in violations_section:
        pass  # violations list remains empty
    elif violations_section:
        # Parse individual violations - improved regex
        # Look for bullet points starting a violation block
        violation_blocks = re.findall(
            r"^\s*\*\s*(.*?)(?=\n\s*\*|\Z)",
            violations_section,
            re.DOTALL | re.MULTILINE,
        )

        for block in violation_blocks:
            block = block.strip()
            try:
                file_match = re.search(r"\*\*File:\*\*\s*`?([^`\n]+)`?", block)
                lines_match = re.search(
                    r"\*\*Line\(s\):\*\*\s*`?(\d+)\b`?", block
                )  # Expecting single integer
                violation_match = re.search(
                    r"\*\*Violation:\*\*\s*(.*?)(?=\n\s*\*\*Code:\*\*|\Z)",
                    block,
                    re.DOTALL,
                )
                code_match = re.search(
                    r"\*\*Code:\*\*\s*\n```(?:code)?\n(.*?)\n```", block, re.DOTALL
                )

                if file_match and lines_match and violation_match:
                    file = file_match.group(1).strip()
                    line = int(lines_match.group(1).strip())
                    violation_desc = violation_match.group(1).strip()
                    code_snippet = code_match.group(1).strip() if code_match else "N/A"

                    # Format the message for the comment body
                    message = (
                        f"**Violation:** {violation_desc}\n\n"
                        f"**Code:**\n```code\n{code_snippet}\n```"
                    )

                    violations.append({"file": file, "line": line, "message": message})
                else:
                    print(
                        f"Warning: Could not parse violation block:\n---\n{block}\n---",
                        file=sys.stderr,
                    )

            except Exception as e:
                print(
                    f"Error parsing violation block: {e}\nBlock:\n---\n{block}\n---",
                    file=sys.stderr,
                )

    return {"summary": summary, "violations": violations}


# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Generate AI PR Review using Gemini.")
    parser.add_argument("--title", required=True, help="Pull Request title")
    parser.add_argument("--description", required=True, help="Pull Request description")
    parser.add_argument("--diff", required=True, help="File diffs content")
    parser.add_argument(
        "--standards-file", required=True, help="Path to coding standards markdown file"
    )

    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    standards_content = ""
    try:
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

    full_prompt = None
    try:
        full_prompt = build_prompt(
            args.title, args.description, args.diff, standards_content
        )
    except Exception as e:
        print(f"Script failed during prompt building: {e}", file=sys.stderr)
        sys.exit(1)

    if full_prompt:
        try:
            raw_review_comment = call_gemini_api(api_key, full_prompt)

            # Parse the raw response
            parsed_data = parse_ai_response(raw_review_comment)

            # Output the structured data as JSON
            print(json.dumps(parsed_data, indent=2))  # Output JSON

        except Exception as e:
            # Errors during API call or parsing are caught
            print(f"Script failed during API call or parsing: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
