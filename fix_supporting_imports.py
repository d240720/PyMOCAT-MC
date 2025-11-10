#!/usr/bin/env python3
"""
Fix all imports in supporting functions to use absolute imports.
"""

import os
import re

def fix_file_imports(filepath):
    """Fix imports in a single file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Replace relative imports with absolute imports
        # Pattern: from .module_name import function_name
        content = re.sub(r'from\s*\.\s*([a-z_]+)\s+import', r'from \1 import', content)

        # Write back
        with open(filepath, 'w') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

# Process all supporting function files
supporting_dir = 'python_implementation/supporting_functions'
files_processed = 0
files_fixed = 0

for filename in os.listdir(supporting_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(supporting_dir, filename)
        files_processed += 1

        if fix_file_imports(filepath):
            files_fixed += 1
            print(f"✓ Fixed {filename}")
        else:
            print(f"✗ Failed {filename}")

print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")