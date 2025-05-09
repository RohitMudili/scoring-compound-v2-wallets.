import json
from pathlib import Path

def inspect_json_file(file_path):
    print(f"Inspecting file: {file_path}")
    try:
        # First, read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"File size: {len(content)} bytes")
            print(f"First 200 characters: {content[:200]}")
            
            # Try to parse as JSON
            try:
                data = json.loads(content)
                print(f"\nSuccessfully parsed JSON")
                print(f"Data type: {type(data)}")
                if isinstance(data, dict):
                    print("Keys:", list(data.keys()))
                    for key, value in data.items():
                        print(f"\nKey: {key}")
                        print(f"Value type: {type(value)}")
                        if isinstance(value, list) and value:
                            print(f"First item type: {type(value[0])}")
                            if isinstance(value[0], dict):
                                print("First item keys:", list(value[0].keys()))
                elif isinstance(data, list):
                    print(f"List length: {len(data)}")
                    if data:
                        print("First item type:", type(data[0]))
                        if isinstance(data[0], dict):
                            print("First item keys:", list(data[0].keys()))
            except json.JSONDecodeError as e:
                print(f"\nError decoding JSON: {str(e)}")
                # Print the problematic part of the content
                line_no = e.lineno
                col_no = e.colno
                print(f"\nError at line {line_no}, column {col_no}")
                lines = content.split('\n')
                if line_no <= len(lines):
                    print(f"Problematic line: {lines[line_no-1]}")
                    print(" " * (col_no-1) + "^")
    except Exception as e:
        print(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    file_path = Path("data/raw/compoundV2_transactions_ethereum_chunk_93.json")
    inspect_json_file(file_path) 