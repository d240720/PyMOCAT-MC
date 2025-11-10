#!/usr/bin/env python3
"""
Analyze import dependencies in supporting functions to identify circular imports.
"""

import os
import re
from collections import defaultdict, deque

def extract_imports(filepath):
    """Extract import statements from a Python file."""
    imports = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Find all import statements
        import_patterns = [
            r'from\s+([a-z_]+)\s+import',
            r'from\s+\.([a-z_]+)\s+import',
            r'import\s+([a-z_]+)'
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return imports

def analyze_dependencies():
    """Analyze import dependencies in supporting functions."""

    supporting_dir = 'python_implementation/supporting_functions'
    dependencies = defaultdict(set)

    # Get all Python files
    python_files = [f for f in os.listdir(supporting_dir)
                   if f.endswith('.py') and f != '__init__.py']

    print("Analyzing import dependencies...\n")

    for filename in python_files:
        filepath = os.path.join(supporting_dir, filename)
        module_name = filename[:-3]  # Remove .py extension

        imports = extract_imports(filepath)

        # Filter to only include other supporting function modules
        local_imports = [imp for imp in imports
                        if f"{imp}.py" in python_files]

        dependencies[module_name] = set(local_imports)

        if local_imports:
            print(f"{module_name} imports: {', '.join(local_imports)}")

    return dependencies

def find_circular_dependencies(dependencies):
    """Find circular dependencies using DFS."""

    def has_cycle(node, visited, rec_stack, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack, path):
                    return True
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
                return True

        rec_stack.remove(node)
        path.pop()
        return False

    cycles = []
    visited = set()

    for node in dependencies:
        if node not in visited:
            has_cycle(node, visited, set(), [])

    return cycles

if __name__ == "__main__":
    deps = analyze_dependencies()
    cycles = find_circular_dependencies(deps)

    print(f"\nFound {len(cycles)} circular dependencies:")
    for i, cycle in enumerate(cycles, 1):
        print(f"{i}. {' -> '.join(cycle)}")

    # Count total dependencies
    total_deps = sum(len(dep_set) for dep_set in deps.values())
    print(f"\nTotal internal dependencies: {total_deps}")

    # Most connected modules
    by_deps = sorted(deps.items(), key=lambda x: len(x[1]), reverse=True)
    print("\nMost connected modules:")
    for module, dep_set in by_deps[:5]:
        print(f"  {module}: {len(dep_set)} dependencies")