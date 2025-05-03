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
REQUEST_TIMEOUT = 600  # Increased timeout slightly

# --- Prompt Template (Updated for JSON Output) ---
PROMPT_TEMPLATE = """
<Role>
You are an expert AI assistant specializing in code review, analysis, and adherence to coding standards. Your primary goal is to meticulously identify coding standard violations in Pull Request changes.
</Role>

<Input>
    <PullRequest>
        <Title>{pr_title}</Title>
        <Description>{pr_description}</Description>
        <FileDiffs>
            {file_diffs}
        </FileDiffs>
        {coding_standards_md}
    </PullRequest>
</Input>


<Output>
{{
  "summary": {{
    "description": "string",
    "changes": [ // Array of objects, one per modified file.
      {{
        "filePath": "string",
        "changeSummary": "string" 
      }}
      // ... more files
    ], // If no files changed, provide an empty array: []
    "newFeatures": [ // Array of strings describing new features/enhancements.
      "string"
      // ... more features
    ], // If no new features, provide an empty array: []
  }},
  "blockViolations": [ // Array of blockViolation objects.
    {{
        "file": "string", // Path to the violated file in which the line added is in.
        "line": "integer", // **CRITICAL:** The EXACT line number in the file *after* the changes where the violation *primarily* occurs. MUST be an integer.
        "violations": [ // Array of strings describing the violation(s) in  detail of a specific line.
            "string" // State the specific rule being violated from the coding standards. Include the example from the coding standards if relevant and helpful for context.
            // ... more violations for the same line/block
        ]
    }}
    // ... more blockViolation objects for other locations
  ] // If no blockViolation found, provide an empty array: []
}}
</Output>

<Instructions>

1. Analyze the provided Pull Request (PR) details (Title, Description, FileDiffs) and CodingStandards Rules. The input can be found above under the Input xml element.

2. Generate a Description for the Pull Request: Provide a concise, refined explanation of the PR’s purpose and changes. Use insights from the PR's Title, Description, FileDiffs. The description should consist of 20-80 words and no more than 80 words. The output should be under the JSON key 'summary.description'.

3. Generate change summaries for the pull request: Go over the Pull Request and for each file modified (you can find this information under FileDiffs). Analyze the changes and provide a concise description of key changes made in that file. The description should consist of 20-80 words and no more than 80 words. The output should be an array of JSON objects of the structure {{ filePath: String, changeSummary: String }}, one object for every modified file. If there are no changes, return an empty array []. The output should be under the JSON key 'summary.changes'.

4. Generate new features summaries for the pull request: Identify any new features or enhancements added in the PR (e.g. New components or modules, new endpoints or APIs, new configuration or environment options, new user interactions or UI behavior, database schema additions, business logic additions, feature flags, tests for new functionality). Analyze the new feature and provide a concise description of the feature. The description should consist of 20-80 words and no more than 80 words. The output should be an array of String, one for each new feature. If there are no new features, return an empty array []. The output should be under the JSON key 'summary.newFeatures'.

5. Generate blockViolations of CodingStandards for the pull request: For each line of code added in the Pull Request (lines starting with `+`, These are added lines), go over ALL the CodingStandards Rules (every rule has a special <Rule_X> tag where X represents a number starting from 1. Each rule consists of <Description_X>, <BadCodeExample_X>, <GoodCodeExample_X> tags, X is a numbering that matches the numbering of <Rule_X>, the <Description_X> describes the rule we call it the 'rule's description', <BadCodeExample_X> consists of a code example that violates the the 'rule's description', <GoodCodeExample_X> consists of a code example that follows the 'rule's description') and report ALL the violations (rules the line added does not follow) these added line introduces. After reporting all the violations for the line added, analyse the violations and the line added and suggest a fix that will solve all the violations found for the line added. The suggested fix should be in code in the same coding language of the file (you can infer the coding language from the extension of the file). Feel free to use the rule's code examples. Your analysis must be thorough, aiming to identify *all* violations according to the provided CodingStandards. Pay *critical attention* to correctly identifying the line number in the *final* version of the file where each violation occurs. The output should be a an array of JSON objects (one for each new line added where a violation has occured) of the structure:
{{
    "file": "string", // Path to the violated file in which the line added is in.
    "line": "integer", // **CRITICAL:** The EXACT line number in the file *after* the changes where the violation *primarily* occurs. MUST be an integer.
    "violations": [ // Array of strings describing the violation(s) in  detail of a specific line.
        "string" // State the specific rule being violated from the coding standards. Include the example from the coding standards if relevant and helpful for context.
        // ... more violations for the same line/block
    ],
    "suggestedFix": "string" // Suggested fix that will solve all the violations found for this specific line of code under this file. The suggested fix should be in code in the same coding language of the file. 
}}

6. Go over the results generated in instructions 2, 3, 4, 5 and generate an output according to the output schema provided above under the Output xml element. When generating the output make sure to generate **ONLY** a valid JSON object adhering *exactly* to the Output structure. Do not include any text before or after the JSON object (e.g., no "```json" wrappers).

</Instructions>
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
                "maxOutputTokens": 8192,
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

        summary_output = "\n".join(summary_parts)

        # --- Extract Violations ---
        block_violations_data = parsed_json.get("blockViolations", [])
        for block_violation in block_violations_data:
            try:
                file = block_violation.get("file")
                line = block_violation.get("line")
                violations_desc = block_violation.get("violations", [])
                suggested_fix = block_violation.get("suggestedFix", "Could not come up with a suggested fix.")

                if file and isinstance(line, int) and violations_desc:
                    # Format the message for the GitHub comment body
                    # Create a message by joining the violations and separating them with newlines
                    message = "- "
                    message += "\n - ".join(violations_desc)
                    message += "\n **Suggested Fix:**"
                    message += f"\n\n ```code\n{suggested_fix}\n```"
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
