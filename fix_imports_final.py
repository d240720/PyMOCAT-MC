#!/usr/bin/env python3
"""
Fix all malformed imports in supporting functions.
"""

import os
import re

def fix_malformed_imports(filepath):
    """Fix malformed import statements."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Fix missing 'from' keyword
        # Pattern: module_name import function_name -> from module_name import function_name
        content = re.sub(r'^([a-z_]+)\s+import\s+', r'from \1 import ', content, flags=re.MULTILINE)

        with open(filepath, 'w') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

# Process all supporting function files
supporting_dir = 'python_implementation/supporting_functions'
files_fixed = 0

print("Fixing malformed imports...")

for filename in os.listdir(supporting_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(supporting_dir, filename)

        if fix_malformed_imports(filepath):
            files_fixed += 1
            print(f"✓ Fixed {filename}")

print(f"\nFixed {files_fixed} files")