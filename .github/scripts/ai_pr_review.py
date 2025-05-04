# .github/scripts/ai_pr_review.py

import os
import sys
import argparse
import json
import requests
import re  # Import regular expressions
from typing import Dict, Any, List, Optional, TypedDict

LLM_API_KEY_ENV_NAME = "GEMINI_API_KEY"

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
        "fileName": "string",   // The name of the file. DO NOT INCLUDE THE WHOLE PATH. For example, for a change in file with path '/a/b/c/d/code.py' the value should be 'code.py'
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

3. Generate change summaries for the pull request: Go over the Pull Request and for each file modified (you can find this information under FileDiffs). Analyze the changes and provide a concise description of key changes made in that file. The description should consist of 20-80 words and no more than 80 words. The output should be an array of JSON objects of the structure {{ fileName: String, changeSummary: String }}, one object for every modified file. If there are no changes, return an empty array []. The output should be under the JSON key 'summary.changes'.

4. Generate new features summaries for the pull request: Identify any new features or enhancements added in the PR (e.g. New components or modules, new endpoints or APIs, new configuration or environment options, new user interactions or UI behavior, database schema additions, business logic additions, feature flags, tests for new functionality). Analyze the new feature and provide a concise description of the feature. The description should consist of 20-80 words and no more than 80 words. The output should be an array of String, one for each new feature. If there are no new features, return an empty array []. The output should be under the JSON key 'summary.newFeatures'.

5. Generate blockViolations of CodingStandards for the pull request: FOR EACH LINE OF CODE added in the Pull Request (lines starting with `+`, These are added lines), go over ALL the CodingStandards Rules (every rule has a special <Rule_X> tag where X represents a number starting from 1. Each rule consists of <Description_X>, <BadCodeExample_X>, <GoodCodeExample_X> tags, X is a numbering that matches the numbering of <Rule_X>, the <Description_X> describes the rule we call it the 'rule's description', <BadCodeExample_X> consists of a code example that violates the the 'rule's description', <GoodCodeExample_X> consists of a code example that follows the 'rule's description') and report ALL the violations (rules the line added does not follow) these added line introduces. After reporting all the violations for the line added, analyse the violations and the line added and suggest a fix that will solve all the violations found for the line added, MAKE SURE to not violating any of the Rules in CodingStandards with the suggested fix. The suggested fix should be in code (DO NOT wrap the code with triple backticks (```) or the coding language, e.g. do not write ```javascript ``` nor ```python ```) in the same coding language of the file (you can infer the coding language from the extension of the file) and should NOT include any comments. Feel free to use the rule's code examples. MAKE SURE TO CHECK FOR VIOLATIONS FOR EVERY SINGLE LINE OF CODE ADDED. Your analysis must be thorough, aiming to identify ALL violations according to the provided CodingStandards. Pay CRITICAL ATTENTION to correctly identifying the line number in the FINAL version of the file where each violation occurs. The output should be an array of JSON objects (one for each new line added where a violation has occured) of the structure:
{{
    "file": "string", // Path to the violated file in which the line added is in.
    "line": "integer", // **CRITICAL:** The EXACT line number in the file where the violation PRIMARILY occurs. MUST be an integer.
    "violations": [ // Array of strings describing the violation(s) in  detail of a specific line.
        "string" // State the specific rule being violated from the coding standards. Include the example from the coding standards if relevant and helpful for context.
        // ... more violations for the same line/block
    ],
    "suggestedFix": "string" // Suggested fix that will solve all the violations found for this specific line of code under this file. The suggested fix should be in code in the same coding language of the file. 
}}

6. Go over the results generated in instructions 2, 3, 4, 5 and generate an output according to the output schema provided above under the Output xml element. When generating the output make sure to generate **ONLY** a valid JSON object adhering *exactly* to the Output structure. Do not include any text before or after the JSON object (e.g., no "```json" wrappers).

</Instructions>
"""

def build_prompt(title: str, description: str, diff: str, standards: str) -> str:
    """Builds the full prompt string for the LLM."""
    try:
        return PROMPT_TEMPLATE.format(
            pr_title=title,
            pr_description=description,
            file_diffs=diff,
            coding_standards_md=standards,
        )
    except Exception as e:
        print(f"Script failed during prompt building: {e}", file=sys.stderr)
        sys.exit(1)  

def call_gemini_api(api_key: str, prompt: str) -> str:
    """Calls the Gemini API and returns the generated text."""
    headers = {"Content-Type": "application/json"}
    payload = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json"
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

def generate_summary_comment_description_part(description):
    return f"**Description:**\n{description}\n"

def generate_summary_comment_changes_part(changes_list):
    changes_part_title = "**Changes:**\n"
    if not changes_list:
        changes_part_description = "No file changes detected.\n"
        return changes_part_title + changes_part_description

    table_header = "| File Name | Change Summary |\n|---|---|\n"
    table_rows = "".join([
        f"| `{change.get('fileName', 'N/A')}` | {change.get('changeSummary', 'N/A')} |\n"
        for change in changes_list
    ])    
    table = table_header + table_rows

    return changes_part_title + table

def generate_summary_comment_new_features_part(features_list):
    features_part_title = "**New Features:**\n"
    if not features_list:
        features_part_description = "No new features identified.\n"
    else:
        features_part_description = "".join([f"* {feature}\n" for feature in features_list])
    return features_part_title + features_part_description

def generate_summary_comment(summary_data):
    description = summary_data.get("description", "No description provided.")
    description_part = generate_summary_comment_description_part(description)
    
    changes_list = summary_data.get("changes", [])
    changes_part = generate_summary_comment_changes_part(changes_list)
    
    features_list = summary_data.get("newFeatures", [])
    new_features_part = generate_summary_comment_new_features_part(features_list)
    
    summary_parts_list = [description_part, changes_part, new_features_part]

    return "\n".join(summary_parts_list)

def generate_block_violation_comment_violations_part(violations_list):
    violations_part_title = "**Violations:**\n"
    if not violations_list:
        violations_part_description = "No violations found.\n"
    else:
        violations_part_description = "".join(f"\n * {violation}" for violation in violations_list)
    return violations_part_title + violations_part_description + "\n\n"

def generate_block_violation_comment_suggested_fix_part(suggested_fix):
    suggested_fix_part_title = "**Suggested Fix:**\n"
    suggested_fix_part_code_suggestion = f"```code\n{suggested_fix.strip()}\n```"
    return suggested_fix_part_title + suggested_fix_part_code_suggestion

def generate_block_violation_comment(block_violation):
    try:
        file = block_violation.get("file")
        line = block_violation.get("line")
        violations_list = block_violation.get("violations", [])
        if not file or not isinstance(line, int) or not violations_list:
            return

        violations_part = generate_block_violation_comment_violations_part(violations_list)
        
        suggested_fix = block_violation.get("suggestedFix", "Could not come up with a suggested fix.")
        suggested_fix_part = generate_block_violation_comment_suggested_fix_part(suggested_fix)
        
        message = violations_part + suggested_fix_part
        
        return { "file": file, "line": line, "message": message }
    except Exception as e:
        print(
            f"Error processing individual violation: {e}\nViolation data: {block_violation}",
            file=sys.stderr,
        )   

def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """Parses the AI's JSON response into summary and violations."""
    try:
        parsed_json = json.loads(response_text)

        summary_data = parsed_json.get("summary", {})
        summary_output = generate_summary_comment(summary_data)

        block_violations = parsed_json.get("blockViolations", [])
        violations_output = [
            block_violation_comment
            for block_violation in block_violations
            if (block_violation_comment := generate_block_violation_comment(block_violation)) is not None
        ]
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

def parse_args():
    parser = argparse.ArgumentParser(description="Generate AI PR Review.")
    parser.add_argument("--title", required=True, help="Pull Request title")
    parser.add_argument("--description", required=True, help="Pull Request description")
    parser.add_argument("--diff", required=True, help="File diffs content")
    parser.add_argument(
        "--standards-file", required=True, help="Path to coding standards file"
    )

    return parser.parse_args()

def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(
            f"Error: Coding standards file not found at '{file_path}'",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(
            f"Error reading coding standards file '{file_path}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)

def main():
    args = parse_args()

    api_key = os.environ.get(LLM_API_KEY_ENV_NAME)
    if not api_key:
        print(f"Error: {LLM_API_KEY_ENV_NAME} environment variable not set.", file=sys.stderr)
        sys.exit(1)

    standards_content = read_file(args.standards_file)
    full_prompt = build_prompt(
            args.title, args.description, args.diff, standards_content
        )

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
