# imag2 Prompt 02：目标体验组图

生成一张 16:9 中文产品体验故事板，用于说明 data_service 的目标形态。风格要求：企业级维护者控制台、清晰流程、每一步都是可审计动作。

画面分为 6 个连续步骤，从左到右：

1. 维护者打开 Knowledge Console：首页显示 workspace、release gate、阻断状态。
2. 导入或绑定真实文档资料：docs/V2.x、workspace 产物、Route A 资料包。
3. 系统构建知识产物：Summary、LLMWiki、GraphRAG、Distill、Source Trace。
4. Agent 读取 MCP/HTTP surface：获取项目事实、任务导航、证据 refs、needs_review。
5. 审计者查看质量决策与外部项目 E2E：人工 decision、路径绑定、structured_unavailable。
6. Release Gate 输出：accepted / needs_review / structured_unavailable / structured_blocker，一眼看出是否能出门。

每步下方标注“输入、处理、输出证据”。必须体现“证据驱动、少人工但保留高风险人工确认”的目标体验。

不要表现成最终 release 已成功；最终门禁应显示“当前阻断项仍需补证”。
