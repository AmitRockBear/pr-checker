# .github/scripts/ai_pr_review.py

import os
import sys
import argparse
import json
import requests
import re  # Import regular expressions
from typing import Dict, Any, List, Optional, TypedDict


# --- Type Hinting for Violations ---
class BlockViolation(TypedDict):
    file: str
    line: int  # Target line number within the file
    message: str  # The full violation message including fixSuggestion block (formatted for comment)


# --- Configuration ---
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent"
REQUEST_TIMEOUT = 180  # Increased timeout slightly

# --- Prompt Template (Updated for JSON Output) ---
PROMPT_TEMPLATE = """
**Role:** You are an expert AI assistant specializing in code review, analysis, and adherence to coding standards. Your primary goal is to meticulously identify coding standard violations in Pull Request changes.

**Task:** Analyze the provided Pull Request (PR) details (title, description, file diffs) and a set of coding standards. Generate a single JSON object containing two main keys: "summary" and "blockViolations". Your analysis must be thorough, aiming to identify *all* violations according to the provided standards. Pay *critical attention* to correctly identifying the line number in the *final* version of the file where each violation occurs.

**Input:**

1.  **PR Title:** {pr_title}
2.  **Original PR Description:**
{pr_description}
3.  **File Diffs (Unified Format):**
    ```diff
{file_diffs}
    ```
4.  **Coding Standards (Markdown Content):**
    ```markdown
{coding_standards_md}
    ```

**Output Requirements:**

Generate **ONLY** a valid JSON object adhering *exactly* to the following structure. Do not include any text before or after the JSON object (e.g., no "```json" wrappers).

```json
{{
  "summary": {{
    "description": "string", // Refined, concise description of the PR's purpose and changes based on description and diffs.
    "changes": [ // Array of objects, one per modified file.
      {{
        "filePath": "string", // Path of the modified file.
        "changeSummary": "string" // 1-2 sentence summary of changes in this file.
      }}
      // ... more files
    ], // If no files changed, provide an empty array: []
    "newFeatures": [ // Array of strings describing new features/enhancements.
      "string"
      // ... more features
    ], // If no new features, provide an empty array: []
    "bugFixes": [ // Array of strings describing added exception handling.
      "string" // e.g., "Added try/except block in file X for handling Y."
      // ... more bug fixes
    ] // If no new exception handling, provide an empty array: []
  }},
  "blockViolations": [ // Array of blockViolation objects.
    {{
      "file": "string", // Path to the violated file.
      "line": "integer", // **CRITICAL:** The EXACT line number in the file *after* the changes where the violation *primarily* occurs. MUST be an integer.
      "violations": [ // Array of strings describing the violation(s) in detail.
        "string" // State the specific rule being violated from the coding standards. Include the example from the coding standards if relevant and helpful for context.
        // ... more violations for the same line/block
    ]
    }}
    // ... more blockViolation objects for other locations
  ] // If no blockViolation found, provide an empty array: []
}}

**Detailed Instructions & Analysis Strategy:**

1.  **Understand the Goal:** First, understand the PR's overall purpose from the title, description, and the nature of the code changes.
2.  **Parse the Diff:** Carefully analyze the `File Diffs`. Pay attention to:
    *   Lines starting with `+`: These are added lines and are the primary target for finding new violations.
    *   Lines starting with `-`: These are removed lines. Violations are generally *not* reported on removed lines, but they provide context for changes.
    *   Lines starting with ` ` (space): These are context lines. A violation might occur on a context line if the *changes* around it make it violate a standard it previously didn't.
    *   Hunk Headers (`@@ -old_start,old_count +new_start,new_count @@`): These are crucial for determining correct line numbers.
3.  **Identify Violations - Be Meticulous:**
    *   For *each rule* defined in the `Coding Standards`, systematically check *every added line (`+`)* and *relevant context line (` `)* in the diffs.
    *   Do not stop after finding the first few violations; aim for *completeness*. Re-read the diffs and standards if necessary.
    *   A single line might violate multiple rules. Include all applicable violations for that line within the `violations` array for that specific entry.
4.  **Determine the Correct Line Number:**
    *   **THIS IS CRITICAL:** When you identify a violation on a specific line within a diff hunk:
        *   Identify the line number in the *new* version of the file.
        *   Use the hunk header (`@@ ... +new_start,new_count ... @@`). `new_start` is the line number in the new file corresponding to the *first* line of the hunk (whether context, added, or deleted).
        *   Count down from `new_start`, incrementing the line number *only* for lines starting with `+` or ` ` (space). Do *not* increment the count for lines starting with `-`.
        *   The resulting number is the value for the `"line"` field in the JSON. It **must** correspond to the line number in the final state of the file after the PR is merged.
        *   If a violation spans multiple lines, report the line number where the violation *starts* or is most prominent.
5.  **Populate the JSON:**
    *   Fill the `summary` object based on your understanding of the PR.
    *   For each violation found, create a `blockViolation` object with the correct file path, the precisely calculated line number (as an integer), and a detailed description of the rule(s) violated.
    *   Ensure the final output is *only* the JSON object, with no surrounding text or markdown formatting.
    *   Ensure all string values within the JSON are correctly escaped.
    *   Ensure the JSON is valid and well-formed.
    *   Ensure the JSON DOES NOT contain invalid escape character in strings (e.g., `\n` should be `\\n`).
    *   Ensure the JSON does not contain any trailing commas.
    *   Ensure the JSON does not contain any unnecessary whitespace or formatting.
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
            "generationConfig": {
                "responseMimeType": "application/json",
            },
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

        candidate = response_json["candidates"][0]
        content = candidate.get("content")
        if not content or not content.get("parts"):
            # Check finish reason in candidate if available
            finish_reason = candidate.get("finishReason")
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

        # Clean potential markdown code block fences if the model adds them despite instructions
        cleaned_text = re.sub(
            r"^\s*```json\s*", "", generated_text.strip(), flags=re.IGNORECASE
        )
        cleaned_text = re.sub(r"\s*```\s*$", "", cleaned_text)

        return cleaned_text

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        # Add more specific error details if available from response
        if "response" in locals() and response is not None:
            print(f"Response status: {response.status_code}", file=sys.stderr)
            print(f"Response body: {response.text}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, IndexError) as e:
        print(f"Error processing Gemini API response: {e}", file=sys.stderr)
        # Add more specific error details if available from response_json
        if "response_json" in locals() and response_json is not None:
            print(
                f"API Response JSON: {json.dumps(response_json, indent=2)}",
                file=sys.stderr,
            )
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """Parses the AI's JSON response into summary and violations."""
    summary_output = ""
    violations_output: List[BlockViolation] = []
    parsed_json: Dict[str, Any] = {}

    try:
        parsed_json = json.loads(response_text)

        # --- Extract Summary ---
        summary_data = parsed_json.get("summary", {})
        description = summary_data.get("description", "No description provided.")
        changes_list = summary_data.get("changes", [])
        features_list = summary_data.get("newFeatures", [])
        fixes_list = summary_data.get("bugFixes", [])

        # Format summary into Markdown string
        summary_parts = [f"**Description:**\n{description}\n"]

        changes_table = "**Changes:**\n"
        if changes_list:
            changes_table += "| File Path | Change Summary |\n|---|---|\n"
            for change in changes_list:
                changes_table += f"| `{change.get('filePath', 'N/A')}` | {change.get('changeSummary', 'N/A')} |\n"
        else:
            changes_table += "No file changes detected.\n"
        summary_parts.append(changes_table)

        features_section = "**New Features:**\n"
        if features_list:
            for feature in features_list:
                features_section += f"* {feature}\n"
        else:
            features_section += "No new features identified.\n"
        summary_parts.append(features_section)

        fixes_section = "**Bug Fixes:**\n"
        if fixes_list:
            for fix in fixes_list:
                fixes_section += f"* {fix}\n"
        else:
            fixes_section += "No new exception handling identified for bug fixes.\n"
        summary_parts.append(fixes_section)

        summary_output = "\n".join(summary_parts)

        # --- Extract Violations ---
        block_violations_data = parsed_json.get("blockViolations", [])
        for block_violation in block_violations_data:
            try:
                file = block_violation.get("file")
                line = block_violation.get("line")
                violations_desc = block_violation.get("violations", [])

                if file and isinstance(line, int) and violations_desc:
                    # Format the message for the GitHub comment body
                    # Create a message by joining the violations and separating them with newlines
                    message = "\n".join(violations_desc)
                    violations_output.append(
                        {"file": file, "line": line, "message": message}
                    )
                else:
                    print(
                        f"Warning: Skipping violation due to missing/invalid fields: {block_violation}",
                        file=sys.stderr,
                    )
            except Exception as e:
                print(
                    f"Error processing individual violation: {e}\nViolation data: {block_violation}",
                    file=sys.stderr,
                )

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode AI response as JSON: {e}", file=sys.stderr)
        print(f"Raw response received:\n---\n{response_text}\n---", file=sys.stderr)
        # Return empty/default structure to avoid crashing downstream
        return {"summary": "Error: Could not parse AI response.", "violations": []}
    except Exception as e:
        print(f"Error processing parsed JSON data: {e}", file=sys.stderr)
        print(f"Parsed JSON: {parsed_json}", file=sys.stderr)
        # Return empty/default structure
        return {"summary": "Error: Could not process parsed AI data.", "violations": []}

    return {"summary": summary_output, "violations": violations_output}


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
