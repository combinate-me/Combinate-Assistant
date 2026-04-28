---
name: token-efficiency
description: Operate in token-efficient mode. Invoke this skill when the user wants cost-effective Claude usage, asks to conserve tokens, says "be efficient", or wants to minimize API costs. Reduces unnecessary tool calls, avoids redundant reads, and keeps output concise without sacrificing quality. v1.0.0
metadata:
  version: 1.0.0
  category: 01-General
---

# Token Efficiency Mode

Every tool call costs tokens. Every token costs money. Operate with the minimum tool calls needed for the same quality result.

## Before Calling Any Tool

Ask yourself these three questions:

1. **Is this information already in the conversation?** Check IDE selection, prior tool results, CLAUDE.md, rules, and recent messages before reaching for a tool.
2. **Am I using the cheapest tool for this job?** Grep is cheaper than Read. Read with offset/limit is cheaper than full Read. Dedicated tools are cheaper than Bash.
3. **Can I combine this with another call?** Parallel independent calls in one message. Combine grep patterns with `|` instead of multiple searches.

If the answer to #1 is yes, skip the tool call entirely.

## Tool Call Rules

### Read
- Never read a full file to find one value. Use Grep instead.
- Never re-read a file you just edited. Edit/Write confirms success.
- Never re-read a file already in conversation context.
- When you must read, use offset/limit to target the specific section.
- Never read a file the user already pasted or selected in the IDE.

### Grep / Glob
- Go directly to named files. If the user said "check app.dart", do not Glob for it.
- Combine related patterns: `pattern1|pattern2|pattern3` in one Grep call.
- Use `output_mode: "content"` with tight `-A`/`-B` context instead of reading matched files separately.
- Use `head_limit` to cap results when you only need the first few matches.

### Bash
- Never use Bash for grep, find, cat, head, tail, sed, awk, or echo. Use dedicated tools.
- Reserve Bash for commands that have no dedicated tool equivalent (build, test, git, curl).

### Agent
- Never spawn an Agent for a single-file task. Use Grep/Read directly.
- Never spawn an Agent to do something you can do in one tool call.
- Use Agent only when the task genuinely requires multi-step exploration across many files.

### Figma MCP
- Never use `get_design_context` for UI checks. It costs 50-150K tokens.
- Use `get_metadata` (~3-8K tokens) for measurements and hierarchy.
- Use `get_screenshot` (~2-4K tokens) for visual reference.
- Only use `get_design_context` when Code Connect mappings are explicitly needed.

## Output Rules

- Lead with the answer. Skip preamble, transitions, and restatements.
- Use tables for structured comparisons. Use code blocks for code. Use bullet points for lists.
- Do not summarize what you just did unless the user asks.
- Do not explain your reasoning unless the user asks.
- Do not list things that are correct. Only report what needs attention.
- One-sentence answers are fine when one sentence is sufficient.

## Parallel Execution

- Always batch independent tool calls into a single message.
- If you need to read 3 unrelated files, send all 3 Read calls at once.
- If you need to Grep for 3 different patterns in different directories, send all 3 at once.
- Never chain independent calls sequentially.

## What NOT to Do

- Do not explore "just in case". Search with intent.
- Do not read context files (me.md, work.md, team.md) unless the task requires that context.
- Do not read SKILL.md files for skills that are not relevant to the current task.
- Do not add error handling, comments, or types to code you did not change.
- Do not propose improvements beyond what was asked.
- Do not create files that are not strictly necessary.
