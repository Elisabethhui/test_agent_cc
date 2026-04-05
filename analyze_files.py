#!/usr/bin/env python3
"""
Script to analyze .py files in cc-mini/src/core/ and generate .md files.
Processes files serially (one at a time).
"""

import os
import sys
import ast
from datetime import datetime

BASE_DIR = "/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/"
OUTPUT_DIR = "/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/code_analyses/"

# Directories to skip
SKIP_DIRS = {"venv", "tests", "assets", "__pycache__"}


def analyze_file(filepath):
    """Analyze a Python file and return analysis results."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    num_lines = len(lines)
    num_non_empty = sum(1 for line in lines if line.strip())
    
    tree = ast.parse(content)
    
    functions = []
    classes = []
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'lineno': node.lineno,
                'args': len(node.args.args),
                'returns': node.returns is not None
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'lineno': node.lineno,
                'bases': [b.id if isinstance(b, ast.Name) else "..." for b in node.bases]
            })
        elif isinstance(node, ast.Import):
            imports.append({
                'module': node.names[0].name if node.names else "unknown"
            })
        elif isinstance(node, ast.ImportFrom):
            imports.append({
                'module': node.module or "unknown",
                'names': [alias.name for alias in node.names]
            })
    
    return {
        'filepath': os.path.relpath(filepath, BASE_DIR),
        'filename': os.path.basename(filepath),
        'content': content,
        'num_lines': num_lines,
        'num_non_empty': num_non_empty,
        'num_functions': len(functions),
        'num_classes': len(classes),
        'num_imports': len(imports),
        'functions': functions,
        'classes': classes,
        'imports': imports,
        'first_func': functions[0]['name'] if functions else None,
        'first_class': classes[0]['name'] if classes else None,
        'est_ncb': num_lines,
        'est_loc': num_lines
    }


def generate_markdown(analysis):
    """Generate markdown documentation from analysis."""
    md_lines = [
        f"# Analysis: {analysis['filename']}",
        "",
        f"> **Location:** {analysis['filepath']}",
        "",
        "## Statistics",
        "",
        f"- **Total Lines:** {analysis['num_lines']}",
        f"- **Non-Empty Lines:** {analysis['num_non_empty']}",
        f"- **Functions:** {analysis['num_functions']}",
        f"- **Classes:** {analysis['num_classes']}",
        f"- **Imports:** {analysis['num_imports']}",
        ""
        "",
        "## Structure",
        "",
        "**First Function:** `{0}`".format(analysis['first_func'] or 'None'),
        "**First Class:** `{0}`".format(analysis['first_class'] or 'None'),
        ""
    ]
    
    if analysis['num_functions'] > 0:
        md_lines.append("### Functions")
        md_lines.append("")
        for i, func in enumerate(analysis['functions'][:5]):
            md_lines.append(f"- `{func['name']}` (line {func['lineno']}, {func['args']} args{'', func['returns'] and ', returns' or ''})")
        if len(analysis['functions']) > 5:
            md_lines.append(f"- and {len(analysis['functions']) - 5} more...")
        md_lines.append("")
    
    if analysis['num_classes'] > 0:
        md_lines.append("### Classes")
        md_lines.append("")
        for i, cls in enumerate(analysis['classes'][:5]):
            bases = ', '.join(cls['bases']) if cls['bases'] else 'object'
            md_lines.append(f"- `{cls['name']}` (line {cls['lineno']}, bases: {bases})")
        if len(analysis['classes']) > 5:
            md_lines.append(f"- and {len(analysis['classes']) - 5} more...")
        md_lines.append("")
    
    if analysis['num_imports'] > 0:
        md_lines.append("### Imports")
        md_lines.append("")
        for imp in analysis['imports'][:5]:
            if imp['module'] == "unknown":
                names = imp['names'] if isinstance(imp.get('names'), list) else [imp.get('names', '')]
                md_lines.append(f"- import {names[-1] if names else ''}")
            else:
                names = imp.get('names', [])
                md_lines.append(f"- from {imp['module']} import {', '.join(names)}")
        if len(analysis['imports']) > 5:
            md_lines.append(f"- and {len(analysis['imports']) - 5} more...")
        md_lines.append("")
    
    return '\n'.join(md_lines)


def main():
    """Main function to process all Python files."""
    print("Scanning for .py files...")
    
    py_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    
    print(f"Found {len(py_files)} Python files to process.")
    print("Processing serially...")
    
    for filepath in py_files:
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.relpath(filepath, BASE_DIR)}")
        print('='*60)
        
        analysis = analyze_file(filepath)
        md_content = generate_markdown(analysis)
        
        output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(filepath))[0] + ".md")
        
        print(f"Writing markdown to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Completed: {os.path.relpath(filepath, BASE_DIR)}")
    
    print("\n" + "="*60)
    print("All files processed!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
