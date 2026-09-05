# GitHub Copilot Instructions

## Core Philosophy
- Prefer the simplest solution that correctly solves the problem. Simple, direct, boring code beats clever code.
- Do not over-engineer. Avoid unnecessary abstractions, design patterns, wrapper classes, config layers, or "future-proofing" that isn't explicitly requested.
- Do not introduce new dependencies, frameworks, or libraries unless explicitly asked to.

## Scope of Changes
- Only modify the code directly relevant to the task at hand.
- Do NOT refactor, reformat, rename, or "clean up" adjacent or unrelated code, even if it looks improvable.
- Do NOT touch files outside the scope of the current request unless required for the task to function.
- If a change requires touching adjacent code to work correctly, explain why before doing it.

## Error Handling
- Write code with a "catch everything that can fail" mentality.
- Wrap operations that can fail (I/O, network calls, parsing, external calls, DB queries, etc.) in try-catch blocks.
- Log errors with enough context to debug (operation being performed, relevant identifiers/inputs, and the error itself).
- Never silently swallow exceptions — at minimum, log them. Re-throw or handle gracefully depending on context.
- Fail loudly in logs, fail gracefully in behavior (no unhandled crashes where avoidable).

## General Behavior
- Ask for clarification instead of guessing when requirements are ambiguous.
- Do not assume missing context — flag it instead of filling gaps with assumptions.
- Keep commit-sized, minimal diffs.

## project instructions
- use the command "py" to run python code.
- use uv instead of pip for dependencies