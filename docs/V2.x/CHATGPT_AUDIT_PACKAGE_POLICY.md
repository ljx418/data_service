# ChatGPT Audit Package Policy

## Rule

每次需要把文档交给 ChatGPT 或其他外部 ChatBox 审计前，必须使用独立审计包目录：

```text
docs/V2.x/chatgpt_audit_package/
```

## Required Workflow

1. 审计前先清空 `docs/V2.x/chatgpt_audit_package/`。
2. 只复制本轮需要审计的文档到该目录。
3. 不在该目录保留旧审计轮次文件。
4. 不把该目录内文件视为源文档；源文档仍以 `docs/V2.x/` 下正式文档为准。
5. 审计回复中的修订意见必须回写到正式源文档，而不是只改审计包副本。

## Purpose

- 避免 ChatGPT 审计时混入旧阶段、旧版本或无关文件。
- 让人类、Agent 和外部 ChatBox 能明确知道本轮审计输入。
- 降低文档版本混淆、虚假通过和重复审计风险。
