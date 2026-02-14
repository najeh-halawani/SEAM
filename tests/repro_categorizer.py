
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.categorizer import _extract_json

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
