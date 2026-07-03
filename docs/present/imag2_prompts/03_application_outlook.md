# imag2 Prompt 03：应用前景与生态连接图

生成一张 16:9 中文架构前景图，主题是“data_service 作为 Agent 长期记忆与项目验收层”。风格要求：技术架构图，浅色背景，模块分层清楚。

中心模块：data_service Evidence-backed Knowledge Layer。

左侧输入：
- 本地代码仓库
- docs/V2.x / 产品规格 / 验收文档
- workspace 多项目产物
- 用户代表性资料包 Route A
- 人工质量决策

中间能力：
- 文档导入与 normalized source
- 摘要、LLMWiki、GraphRAG、Distill
- Source trace 与 evidence refs
- MCP/HTTP/CLI 公开接口
- Release gate / false-green audit

右侧应用场景：
- Coding Agent 长期项目记忆
- 维护者首页与状态面板
- 迁移/重构验收
- 多项目 E2E 审计
- 企业知识库与合规证据包
- 与 MCP、GraphRAG、LlamaIndex/LangGraph memory 生态对接

右下角列出未实现或需后续补强：
- 默认 shell CLI gap closure
- Route A 真实资料自动脱敏流程
- 外部项目路径治理
- 人工审批与 dependency hygiene 自动门禁

不能画成已具备全部生态集成；需要用虚线表示“可扩展方向”。
