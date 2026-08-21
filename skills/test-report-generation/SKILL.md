---
name: test-report-generation
description: Use when the user wants a formal test report after implementation, wants automated validation summarized, or asks to convert raw validation evidence into the repository test report format. Trigger phrases: test report, validation report, 生成测试报告, 输出测试结果.
---

# Test Report Generation

Convert validation evidence into the repository test report format.

This skill follows `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `report-template.md`

## Inputs

- app name (required)
- task type (required)
- validation evidence (required)

## Steps

1. Read the latest validation evidence.
2. Normalize it into repository categories.
3. Identify blocking errors, if any.
4. Identify owner attention points.
5. Produce the report in repository format.

## Output

A short report in `docs/ai-sdlc/06-test-report-format.md` format.

## Rules

- Report only the latest validated result.
- Do not invent missing evidence.
- If validation is incomplete, say exactly what is missing.
