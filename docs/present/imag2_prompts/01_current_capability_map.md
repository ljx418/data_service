# imag2 Prompt 01：当前能力分类图

生成一张横向 16:9 中文信息图，用于技术审计报告。主题是“data_service 当前可完成功能”。视觉风格要求：清晰、专业、少装饰、白底、深灰文字、使用四种状态色块。

必须包含四列：

1. 已验收：
   - 文档导入、摘要、GraphRAG/LLMWiki/Distill 工作区产物
   - Knowledge Console 静态入口
   - MCP/HTTP public surface inventory
   - V2.86-V2.95 focused tests：27 passed
   - protected legacy diff clean

2. 受限完成：
   - Restore runtime：pytest 可复跑，但 venv 创建失败
   - Route A：结构已实现，缺用户代表性真实资料
   - Quality decision：结构已实现，缺人工 reviewer decision
   - External project E2E：data_service 可跑，外部三项目缺路径
   - Release gate：能聚合阻断，不能 final accepted

3. 规划中：
   - 默认 shell CLI gap closure
   - Route A 真实资料自动化脱敏与审计包
   - 质量人工决策工作台
   - 外部项目路径配置与定期 E2E
   - dependency hygiene gate

4. No-Go：
   - 不声明完整恢复复杂项目设计意图
   - 不声明 full call graph、runtime topology、data/control flow、type inference
   - 不把 docs claim 当 code fact
   - 不把 needs_review / structured_unavailable / structured_blocker 写成 accepted
   - 不用 Full Corpus 替代 Route A

底部加一条醒目但克制的结论：阶段实现范围通过；最终发布仍为 structured_blocker。

不要使用虚构 Logo，不要使用过度科技感背景，不要把阻断项画成成功项。
