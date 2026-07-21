from pymupdf4llm import to_markdown
import sys

try:
    md = to_markdown(sys.argv[1])
    print(f"Extracted {len(md)} chars.")
    print("First 500 chars:")
    print(md[:500])
    print("\nLast 500 chars:")
    print(md[-500:])
except Exception as e:
    print(f"Error: {e}")
