#!/usr/bin/env python3
"""
Repository scan script for project1/context_system
Generates structured artifacts about the codebase.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Get the root directory (parent of context_system)
ROOT_DIR = Path(__file__).parent.parent  # /Users/huguoqing/zzzhu/code/exp/RAG/project1

def get_all_py_files():
    """Get all Python files in the repository."""
    py_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if f.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, f), ROOT_DIR)
                py_files.append(rel_path)
    return sorted(py_files)

def get_all_md_files():
    """Get all Markdown files in the repository."""
    md_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if f.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, f), ROOT_DIR)
                md_files.append(rel_path)
    return sorted(md_files)

def get_file_stats(filepath):
    """Get file statistics."""
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'mtime': stat.st_mtime,
        'atime': stat.st_atime,
        'ctime': stat.st_ctime
    }

def analyze_directory_structure():
    """Analyze the directory structure."""
    structure = {}
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip some directories
        skip_dirs = {'__pycache__', '.git', '.cc-mini'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        rel_root = os.path.relpath(root, ROOT_DIR)
        if rel_root == '.':
            rel_root = ''
        
        if rel_root not in structure:
            structure[rel_root] = {
                'dirs': [],
                'files': [],
                'py_files': [],
                'md_files': []
            }
        
        if rel_root:
            structure[rel_root]['dirs'].append(d)
            structure[rel_root]['files'] = [f for f in files if not f.endswith('.py') and not f.endswith('.md')]
        
        for f in files:
            if f.endswith('.py'):
                if rel_root:
                    structure[rel_root]['py_files'].append(f)
            elif f.endswith('.md'):
                structure[rel_root]['md_files'].append(f)
    
    return structure

def generate_repo_snapshot():
    """Generate repo_snapshot.json."""
    all_files = get_all_py_files()
    all_files += get_all_md_files()
    all_files = sorted(set(all_files))
    
    file_map = {}
    for f in all_files:
        filepath = ROOT_DIR / f
        if filepath.exists():
            stats = get_file_stats(filepath)
            file_map[f] = {
                'path': os.path.abspath(filepath),
                'size': stats['size'],
                'mtime': stats['mtime'],
                'atime': stats['atime'],
                'ctime': stats['ctime']
            }
    
    snapshot = {
        'generated_at': datetime.now().isoformat(),
        'root': str(ROOT_DIR),
        'total_files': len(all_files),
        'total_python_files': len([f for f in all_files if f.endswith('.py')]),
        'total_markdown_files': len([f for f in all_files if f.endswith('.md')]),
        'files': file_map
    }
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'repo_snapshot.json', 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    print(f"Generated repo_snapshot.json with {len(all_files)} files")
    return snapshot

def generate_file_manifest():
    """Generate file_manifest.json."""
    all_files = get_all_py_files()
    all_files += get_all_md_files()
    all_files = sorted(set(all_files))
    
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'root': str(ROOT_DIR),
        'files': []
    }
    
    for f in all_files:
        filepath = ROOT_DIR / f
        if filepath.exists():
            stats = get_file_stats(filepath)
            manifest['files'].append({
                'path': f,
                'full_path': os.path.abspath(filepath),
                'size': stats['size'],
                'mtime': stats['mtime'],
                'type': 'python' if f.endswith('.py') else 'markdown' if f.endswith('.md') else 'other'
            })
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'file_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Generated file_manifest.json with {len(manifest['files'])} files")
    return manifest

def generate_module_candidates():
    """Generate module_candidates.json by analyzing Python files."""
    all_files = get_all_py_files()
    
    modules = []
    current_module = None
    
    for f in all_files:
        filepath = ROOT_DIR / f
        if not filepath.exists():
            continue
            
        if f.endswith('.py') and not f.startswith('__'):
            if '.' in f:
                parent_dir = f.rsplit('.', 1)[0] + '.py'
                if parent_dir in all_files:
                    module_name = f.replace(parent_dir + '.', '')
                    if current_module and current_module['name'] == module_name:
                        current_module['files'].append(f)
                    else:
                        current_module = {
                            'name': module_name,
                            'files': [f],
                            'main_file': parent_dir,
                            'type': 'module',
                            'file_path': filepath,
                            'status': 'candidate'
                        }
                else:
                    module_name = f.rsplit('/', 1)[-1]
                    modules.append({
                        'name': module_name,
                        'files': [f],
                        'main_file': f,
                        'type': 'module',
                        'file_path': filepath,
                        'status': 'candidate'
                    })
            else:
                modules.append({
                    'name': f,
                    'files': [f],
                    'main_file': f,
                    'type': 'module',
                    'file_path': filepath,
                    'status': 'candidate'
                })
    
    for m in modules:
        if not m['name'].startswith('__') and m['status'] == 'candidate':
            m['status'] = 'module'
    
    candidates = {
        'generated_at': datetime.now().isoformat(),
        'root': str(ROOT_DIR),
        'modules': modules
    }
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'module_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    
    print(f"Generated module_candidates.json with {len(modules)} modules")
    return candidates

def generate_reading_order():
    """Generate reading_order.md based on dependency analysis."""
    # Simple topological sort based on imports
    all_py = [f for f in get_all_py_files() if f.endswith('.py')]
    all_md = [f for f in get_all_md_files() if f.endswith('.md')]
    
    order = []
    
    # Group files by priority
    priority_files = []
    core_files = []
    tool_files = []
    agent_files = []
    module_files = []
    test_files = []
    
    for f in all_py:
        filepath = ROOT_DIR / f
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            has_import_core = 'from core' in content or 'import core' in content
            has_import_agents = 'from agents' in content or 'import agents' in content
            has_import_tools = 'from tools' in content or 'import tools' in content
            
            if f.endswith('main.py') or f.endswith('__init__.py'):
                priority_files.append(f)
            elif has_import_core:
                core_files.append(f)
            elif has_import_agents:
                agent_files.append(f)
            elif has_import_tools:
                tool_files.append(f)
            else:
                other_files = []
                if f.endswith('.py') and not f.startswith('test_'):
                    other_files.append(f)
                
                if other_files:
                    module_files.append(f)
                else:
                    priority_files.append(f)
    
    # Create directories
    directories = []
    for root, dirs, files in os.walk(ROOT_DIR):
        skip_dirs = {'__pycache__', '.git', '.cc-mini'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        if dirs:
            directories.append(os.path.relpath(root, ROOT_DIR))
    
    order = []
    
    # Add directories first
    order.extend(directories)
    
    # Add priority files
    order.extend(sorted(priority_files))
    
    # Add core files
    order.extend(sorted(core_files))
    
    # Add agent files
    order.extend(sorted(agent_files))
    
    # Add tool files
    order.extend(sorted(tool_files))
    
    # Add other files
    order.extend(sorted(other_files))
    
    # Add markdown files
    order.extend(all_md)
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'reading_order.md', 'w', encoding='utf-8') as f:
        f.write("# Reading Order\n\n")
        for item in order[:50]:  # Limit to first 50 items
            f.write(f"- {item}\n")
        if len(order) > 50:
            f.write(f"\n... and {len(order) - 50} more items\n")
    
    print(f"Generated reading_order.md with {len(order)} items")
    return order

def generate_manifest():
    """Generate manifest.json."""
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'root': str(ROOT_DIR),
        'directories': [],
        'files': [],
        'modules': [],
        'tests': [],
        'config_files': []
    }
    
    # Find directories
    for root, dirs, files in os.walk(ROOT_DIR):
        skip_dirs = {'__pycache__', '.git', '.cc-mini'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel_root = os.path.relpath(root, ROOT_DIR)
        if rel_root:
            manifest['directories'].append(rel_root)
    
    # Find files
    all_files = get_all_py_files()
    all_files += get_all_md_files()
    all_files = sorted(set(all_files))
    
    manifest['files'] = []
    for f in all_files:
        filepath = ROOT_DIR / f
        if filepath.exists():
            manifest['files'].append({
                'path': f,
                'full_path': os.path.abspath(filepath),
                'type': 'python' if f.endswith('.py') else 'markdown' if f.endswith('.md') else 'other'
            })
    
    # Find modules
    all_py = [f for f in all_files if f.endswith('.py')]
    modules = []
    current_module = None
    
    for f in all_py:
        filepath = ROOT_DIR / f
        if not filepath.exists():
            continue
            
        if f.endswith('.py') and not f.startswith('__'):
            if '.' in f:
                parent_dir = f.rsplit('.', 1)[0] + '.py'
                if parent_dir in all_py:
                    module_name = f.replace(parent_dir + '.', '')
                    if current_module and current_module['name'] == module_name:
                        current_module['files'].append(f)
                    else:
                        current_module = {
                            'name': module_name,
                            'files': [f],
                            'main_file': parent_dir,
                            'type': 'module',
                            'file_path': filepath,
                            'status': 'confirmed'
                        }
                else:
                    module_name = f.rsplit('/', 1)[-1]
                    modules.append({
                        'name': module_name,
                        'files': [f],
                        'main_file': f,
                        'type': 'module',
                        'file_path': filepath,
                        'status': 'confirmed'
                    })
            else:
                modules.append({
                    'name': f,
                    'files': [f],
                    'main_file': f,
                    'type': 'module',
                    'file_path': filepath,
                    'status': 'confirmed'
                })
    
    manifest['modules'] = modules
    
    # Find tests
    test_files = [f for f in all_files if 'test_' in f or f.endswith('_test.py')]
    manifest['tests'] = test_files
    
    # Find config files
    config_files = []
    for f in all_files:
        if f.endswith(('.py', '.json', '.yaml', '.yml', '.toml')):
            filepath = ROOT_DIR / f
            if filepath.exists():
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                if ('config' in f.lower() or 'config' in content.lower()) and 'test' not in f.lower():
                    config_files.append(f)
    
    manifest['config_files'] = config_files
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Generated manifest.json with {len(manifest['files'])} files and {len(manifest['modules'])} modules")
    return manifest

def generate_todo():
    """Generate TODO.md."""
    all_py = [f for f in get_all_py_files() if f.endswith('.py')]
    all_md = [f for f in get_all_md_files() if f.endswith('.md')]
    
    todos = []
    
    # Check Python files for TODO, FIXME, TODO: comments
    for f in all_py:
        filepath = ROOT_DIR / f
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            if 'TODO' in content:
                todos.append({
                    'type': 'todo',
                    'file': f,
                    'content': 'TODO'
                })
            
            if 'FIXME' in content:
                todos.append({
                    'type': 'fixme',
                    'file': f,
                    'content': 'FIXME'
                })
    
    # Check Markdown files for TODO, FIXME
    for f in all_md:
        filepath = ROOT_DIR / f
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            if 'TODO' in content:
                todos.append({
                    'type': 'todo',
                    'file': f,
                    'content': 'TODO'
                })
            
            if 'FIXME' in content:
                todos.append({
                    'type': 'fixme',
                    'file': f,
                    'content': 'FIXME'
                })
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'TODO.md', 'w', encoding='utf-8') as f:
        if todos:
            f.write("# TODO List\n\n")
            for i, todo in enumerate(todos, 1):
                f.write(f"### {i}. [{todo['type'].upper()}] {todo['file']}\n")
                f.write(f"**Content:** {todo['content']}\n\n")
        else:
            f.write("# TODO List\n\n")
            f.write("No TODO or FIXME items found in the repository.\n")
    
    print(f"Generated TODO.md with {len(todos)} items")
    return todos

def generate_progress():
    """Generate progress.md."""
    all_py = [f for f in get_all_py_files() if f.endswith('.py')]
    all_md = [f for f in get_all_md_files() if f.endswith('.md')]
    
    total_files = len(all_py) + len(all_md)
    scanned_files = len(all_py) + len(all_md)
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'progress.md', 'w', encoding='utf-8') as f:
        f.write("# Progress Report\n\n")
        f.write(f"**Repository Root:** {ROOT_DIR}\n\n")
        f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Files:** {total_files}\n")
        f.write(f"- Python files: {len(all_py)}\n")
        f.write(f"- Markdown files: {len(all_md)}\n")
        f.write(f"- Other files: {total_files - len(all_py) - len(all_md)}\n\n")
        f.write(f"**Scanned Files:** {scanned_files}\n")
        f.write(f"**Progress:** {scanned_files}/{total_files} ({100 if total_files == scanned_files else int(scanned_files * 100 / max(1, total_files))})%\n\n")
        f.write("**Status:** Complete\n\n")
        f.write("---\n\n")
        f.write("## Generated Artifacts\n\n")
        f.write("- repo_snapshot.json\n")
        f.write("- file_manifest.json\n")
        f.write("- module_candidates.json\n")
        f.write("- reading_order.md\n")
        f.write("- manifest.json\n")
        f.write("- TODO.md\n")
        f.write("- progress.md\n")
    
    print("Generated progress.md")
    return scanned_files

def generate_repo_overview():
    """Generate repo_overview.md - the main artifact."""
    # Run all other generators first
    generate_repo_snapshot()
    generate_file_manifest()
    generate_module_candidates()
    generate_reading_order()
    generate_manifest()
    generate_todo()
    generate_progress()
    
    # Now read the artifacts to generate the overview
    manifest_path = ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'manifest.json'
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    lines = []
    
    lines.append("# Repository Overview")
    lines.append("")
    lines.append(f"**Root Directory:** {ROOT_DIR}")
    lines.append("")
    lines.append("")
    lines.append("## Directory Structure")
    lines.append("")
    lines.append("")
    
    # Add directory structure
    directories = manifest.get('directories', [])
    unique_dirs = []
    seen = set()
    for d in directories:
        if d not in seen:
            unique_dirs.append(d)
            seen.add(d)
    
    for i, d in enumerate(unique_dirs):
        if i == 0:
            lines.append(f"### {d}")
        else:
            lines.append(f"- {d}")
    
    lines.append("")
    lines.append("")
    lines.append("## File Summary")
    lines.append("")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    lines.append("")
    
    python_count = len([f for f in manifest.get('files', []) if f.get('type') == 'python'])
    md_count = len([f for f in manifest.get('files', []) if f.get('type') == 'markdown'])
    lines.append(f"| Python | {python_count} |")
    lines.append(f"| Markdown | {md_count} |")
    lines.append("")
    lines.append("")
    lines.append("")
    
    lines.append("## Module Candidates")
    lines.append("")
    lines.append("")
    
    for module in manifest.get('modules', []):
        lines.append(f"- **{module['name']}**: {len(module['files'])} files ({module['status']})")
    
    lines.append("")
    lines.append("")
    lines.append("## Config Files")
    lines.append("")
    lines.append("")
    
    for cf in manifest.get('config_files', []):
        lines.append(f"- {cf}")
    
    lines.append("")
    lines.append("")
    lines.append("## Test Files")
    lines.append("")
    lines.append("")
    
    for tf in manifest.get('tests', []):
        lines.append(f"- {tf}")
    
    lines.append("")
    lines.append("")
    lines.append("## TODO Items")
    lines.append("")
    lines.append("")
    
    # Read TODO.md content
    todo_path = ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'TODO.md'
    if todo_path.exists():
        with open(todo_path, 'r', encoding='utf-8') as f:
            todo_content = f.read()
            for line in todo_content.split('\n'):
                if line.strip():
                    lines.append(line)
    
    lines.append("")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("")
    lines.append("This is an automated repository scan. See the generated artifacts in `./code-reading-notes/00_repo_scan/` for detailed information.")
    
    with open(ROOT_DIR / 'code-reading-notes' / '00_repo_scan' / 'repo_overview.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("Generated repo_overview.md")

if __name__ == '__main__':
    print("=" * 60)
    print("Starting repository scan...")
    print("=" * 60)
    print()
    
    # Generate all artifacts
    generate_repo_snapshot()
    print()
    
    generate_file_manifest()
    print()
    
    generate_module_candidates()
    print()
    
    generate_reading_order()
    print()
    
    generate_manifest()
    print()
    
    generate_todo()
    print()
    
    generate_progress()
    print()
    
    print()
    print("=" * 60)
    print("Generating repo_overview.md...")
    print("=" * 60)
    print()
    
    generate_repo_overview()
    print()
    print("=" * 60)
    print("Repository scan complete!")
    print("=" * 60)
