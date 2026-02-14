
import json
import re

def _extract_json(text: str) -> dict | None:
    """Extract JSON object from a response that may contain extra text.

    Handles nested structures (arrays, nested objects) and markdown fences.
    """
    if not text:
        return None

    # Strip markdown code fences if present
    cleaned = re.sub(r'```(?:json)?\s*', '', text).strip()
    cleaned = cleaned.rstrip('`').strip()

    # predefined replacements for common LLM json errors
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)  # remove trailing commas

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Use bracket counting to find the outermost {...} object
    start = cleaned.find('{')
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    # Last ditch effort: try to fix unquoted keys or single quotes
                    try:
                         # Very basic repair for simple cases
                         import ast
                         return ast.literal_eval(candidate)
                    except:
                        return None
    return None

def test_extraction(name, input_str, expected_success):
    print(f"--- Testing {name} ---")
    print(f"Input: {input_str!r}")
    result = _extract_json(input_str)
    print(f"Result: {result}")
    
    if expected_success and result:
        print("✅ Success")
    elif not expected_success and result is None:
        print("✅ Success (correctly failed)")
    elif expected_success and result is None:
        print("❌ Failed (expected valid JSON)")
    else:
        print("❌ Failed (expected None)")
    print()

def main():
    # 1. Clean JSON
    test_extraction("Clean JSON", '{"a": 1, "b": 2}', True)
    
    # 2. Markdown fenced
    test_extraction("Markdown", '```json\n{"a": 1}\n```', True)
    
    # 3. Trailing comma
    test_extraction("Trailing Comma", '{"a": 1,}', True)
    
    # 4. Trailing comma in list
    test_extraction("Trailing Comma List", '{"a": [1, 2,]}', True)
    
    # 5. Missing quotes keys (AST fallback)
    test_extraction("Missing Quotes", "{'a': 1}", True) # ast.literal_eval handles this
    
    # 6. Garbage + JSON
    test_extraction("Garbage Prefix", 'Here is the json: {"a": 1}', True)
    
    # 7. Totally invalid
    test_extraction("Invalid", 'NOT JSON AT ALL', False)
    
    # 8. Empty
    test_extraction("Empty", '', False)

if __name__ == "__main__":
    main()
