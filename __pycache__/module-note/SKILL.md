    ---
    name: module-note
    description: Aggregate related file notes into one module-level summary
    context: fork
    allowed-tools: Bash, Read, Glob, Grep, Write
    arguments: [module name from module_candidates.json or manifest.json]
    ---

    # Module Note

You are producing one module-level summary.

## Goal
Summarize one module by aggregating existing file notes, not by rereading the entire source tree.

## Constraints
- Prefer reading file notes from `./code-reading-notes/10_file_notes/`.
- Only reread source code when file notes are insufficient.
- Do not read more than 3 raw source files during this skill.
- Focus on module boundaries, responsibilities, internal flow, and external interfaces.

## Required tasks
1. Read:
   - `./code-reading-notes/manifest.json`
   - `./code-reading-notes/00_repo_scan/module_candidates.json`
   - relevant file notes under `./code-reading-notes/10_file_notes/`
2. Resolve the module from `$ARGUMENTS` or select the next unfinished module.
3. Produce:
   `./code-reading-notes/20_module_notes/module_<MODULE_NAME>.md`
4. Update:
   - `manifest.json`
   - `TODO.md`
   - `progress.md`

## Required output structure
# 模块：<模块名>
## 1. 模块定位
## 2. 包含文件
## 3. 模块内部逻辑
## 4. 对外接口
## 5. 设计亮点
## 6. 学习总结
## 7. 面试表达

## Stop condition
Stop after one module note is produced.
