# V2.101-V2.105 PRD：Workspace 项目组合知识化

## 1. 阶段定位

V2.101-V2.105 承接 V2.96-V2.100 的验收结论：当前系统已经具备代码资产、文档 ingest、query、source trace、MCP/CLI/HTTP 和 `/knowledge` 静态控制台基础，但还不能把 `/mnt/c/workspace/*` 下的多个项目和纯资料目录自动组织成可验收的项目组合知识库。

本阶段目标是补齐三个剩余产品能力：

1. 按 workspace 文件夹维度发现和分类项目。
2. 将项目 docs 与纯文档/多媒体资料目录转成可追溯知识库原料。
3. 让 `/knowledge` 具备项目组合知识化的真实验收面板，而不是只作为泛化控制台入口。

本阶段仍然不得声明：

- 已完整恢复复杂项目设计意图。
- 已具备 full call graph、runtime topology、data/control flow 或完整 type inference。
- 图片、扫描 PDF、图片型 PPT 已被理解，除非存在真实 OCR/视觉解析证据。
- 文件夹存在、README 存在或 UI 截图存在即可 accepted。
- `needs_review`、`structured_unavailable`、`structured_blocker` 可计入 accepted。

## 2. GitHub CLI 开源方案参考

本阶段借鉴 GitHub CLI 的产品和架构形态，而不是复制其业务功能或 Go 实现。

参考事实：

- GitHub CLI 官方仓库将 `gh` 定位为把 GitHub 工作流带到终端和代码旁边的命令行工具：https://github.com/cli/cli
- GitHub CLI 手册将命令组织为 core commands、Actions commands 和 additional commands：https://cli.github.com/manual/gh
- `gh alias` 支持为常用命令建立快捷方式或组合命令：https://cli.github.com/manual/gh_alias
- `gh extension` 通过 `gh-*` 可执行文件扩展命令，并明确扩展不能覆盖 core commands、未由 GitHub 背书：https://cli.github.com/manual/gh_extension
- GitHub 官方博客说明 `gh api` 可作为通用 API façade，处理认证、参数序列化、JSON 解码、分页、缓存和 jq 输出：https://github.blog/engineering/engineering-principles/scripting-with-github-cli/

转化到 data_service 的设计原则：

- CLI 入口薄，命令族清晰，`portfolio` 作为独立命令组。
- build/read 语义稳定，不在 UI 或命令输出中制造未持久化事实。
- 支持扩展式 adapter，但默认不执行外部不可信插件。
- 对缺依赖、缺 OCR、缺路径、缺人工确认输出结构化状态，而不是让命令静默成功。
- 提供类似 `gh api` 的 HTTP/MCP/CLI parity：Agent 可选择任一入口获取同一 persisted artifact。

## 3. 当前事实基线

| 能力 | 当前事实 | 本阶段目标 |
| --- | --- | --- |
| 项目代码理解 | `code import/snapshot/inventory/symbols/overview/context-pack` 已存在 | 对 `/mnt/c/workspace/*` 自动发现代码项目并生成有界项目级 artifacts；context pack/overview 作为可用时的增强证据，不是默认全量承诺 |
| 文档 ingest | `DataService` 支持目录递归和多格式文本抽取；MCP source import 只接受文件 | 对项目 docs 和纯资料目录生成 source candidate matrix 与 build run |
| 多媒体资料 | PPTX/PDF/DOCX/YAML 抽取器存在；当前本机 OCR、pdftoppm、soffice 不可用 | 文本可抽取资料进入知识库，图片/扫描件输出 `ocr_required` 或 `structured_unavailable` |
| `/knowledge` | 可打开静态控制台，但不能完成项目组合知识化验收 | 增加项目组合状态面板、建库状态、缺口与 next actions |
| 外部 workspace | `/mnt/c/workspace` 下存在多个项目和纯文档目录 | 真实扫描 workspace，避免只用 mock 或本仓小样本 |

## 4. 阶段目标

| 阶段 | 名称 | 目标体验 |
| --- | --- | --- |
| V2.101 | Workspace Portfolio Discovery | 维护者能看到 `/mnt/c/workspace` 下每个一级目录是代码项目、文档项目、媒体资料库、忽略项还是待审项 |
| V2.102 | Project Knowledge Builder | Agent 能对可读代码项目生成 snapshot、inventory、symbols、project brief 或可用 context refs，并绑定 docs/media readiness 证据 |
| V2.103 | Document and Media Intake | 维护者能看到 PDF/PPTX/DOCX/YAML/图片/扫描件的可抽取性、OCR 缺口和入库状态 |
| V2.104 | Knowledge Console Portfolio Panel | `/knowledge` 能真实展示项目组合、建库状态、不可用原因、查询入口和证据路径 |
| V2.105 | Portfolio Release Gate | 系统聚合项目发现、文档建库、媒体 readiness、UI 截图和 false-green audit，给出能否出门的状态 |

## 5. 目标用户体验

### 5.1 维护者

维护者应能在 `/knowledge` 或 HTML 报告中看到：

- workspace 下有哪些项目和资料目录。
- 每个目录为什么被分类为代码项目、文档项目、媒体资料库或 ignored。
- 哪些项目已生成 code asset artifacts。
- 哪些 docs 已入库，哪些文件因格式、大小、OCR 或依赖缺失未入库。
- 下一步需要人类提供什么：OCR provider、外部路径、资料确认或忽略规则。

维护者首屏体验以 `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_PROTOTYPE_UX_SPEC.md` 为准，必须包含 Portfolio Status Header、Project Registry Summary、Build Run Summary、Media Readiness Summary 和 Next Actions List。

### 5.2 Coding Agent

Coding Agent 应能：

- 通过 CLI/MCP/HTTP 触发 portfolio scan/build/read/report。
- 读取每个项目的 artifact refs、source refs、evidence refs、unresolved 和 next actions。
- 将项目理解限制在 evidence-backed code artifacts、project brief、可用 context refs 和结构化缺口内，不把 docs claim 当成 code fact。
- 在 OCR、PPT 转换或路径不可用时保留结构化阻断。

### 5.3 审计者

审计者应能：

- 复跑 `/mnt/c/workspace` 真实扫描。
- 对照 project registry、source candidate matrix、media readiness 和 build runs 检查状态。
- 确认 `/knowledge` 面板展示的是 persisted artifact，不是硬编码文案。
- 确认 accepted 项均有真实命令/API/MCP/截图证据。

## 6. In Scope

- `/mnt/c/workspace/*` 或 configured allowed roots 的只读扫描。
- 项目/资料目录分类规则与 evidence。
- code project 的 code asset build 编排。
- docs 与纯资料目录的 source candidate matrix。
- PDF/PPTX/DOCX/YAML/HTML/MD/TXT/JSON/CSV 的文本抽取 readiness。
- 图片、扫描 PDF、图片型 PPT 的 OCR readiness 与 structured unavailable。
- `/knowledge` portfolio panel 的真实验收路径。
- CLI/MCP/HTTP build/read parity。
- HTML acceptance report、headless screenshot 和 false-green audit。

## 7. Out of Scope

- 自动安装 OCR、LibreOffice、系统依赖或外部二进制。
- 自动修改被扫描项目。
- 自动删除或移动 workspace 下任何文件。
- 将图片视觉理解、版式理解或复杂 PPT 图表理解作为默认能力。
- 将 GitHub CLI extension 的不可信外部执行模型直接引入本项目。
- 默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## 8. 完成定义

文档阶段完成必须满足：

1. 三个剩余功能均映射到具体目标实体、artifact、public surface、focused tests 和验收门槛。
2. drawio 不超过 8 页，中文书写，展示当前架构到目标架构、代码实体关系、开发验收计划、里程碑、出门条件和 No-Go。
3. 明确哪些能力可 accepted，哪些只能 `needs_review`、`structured_unavailable` 或 `structured_blocker`。
4. 明确 GitHub CLI 参考来源和转化原则。
5. 明确 `/knowledge` 必须读取 persisted artifacts，不能硬编码验收结论。
6. 原型 UX spec 必须说明维护者首页、项目组合列表、项目详情、媒体 readiness 和 release gate 的用户路径与截图要求。

## 8.1 出门状态边界

本阶段实现和验收必须区分两个状态：

- `implementation_status`：V2.101-V2.105 的 workspace scan、project classification、project build orchestration、document/media intake、`/knowledge` portfolio panel、release gate 是否完成实现并通过 focused tests、真实 workspace E2E、PRD/spec review 和 false-green audit。
- `portfolio_final_status`：workspace 中所有高风险项目、资料和媒体行是否都具备真实 accepted evidence，且没有 `needs_review`、`structured_unavailable` 或 `structured_blocker`。

如果当前 workspace 内存在图片、扫描 PDF 或图片型 PPT，而本机 OCR/provider 不可用，则本阶段仍可在功能实现和 false-green audit 通过后声明 `implementation_status=accepted`，但不得声明 `portfolio_final_status=accepted`。release gate 必须保留 `ocr_required`、`structured_unavailable` 或 `needs_review`，并给出补证路径。

## 9. 文档基线

本阶段文档基线包括：

- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_PRD.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_TARGET_ARCHITECTURE.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_PROTOTYPE_UX_SPEC.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_IMPLEMENTATION_BLUEPRINT_AND_ACCEPTANCE_SPEC.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_PHASE_READINESS_AND_SCHEMA_CONTRACTS.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_FULL_COVERAGE_MATRIX.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_TEST_AND_E2E_MAPPING.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_GAP_ANALYSIS.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_MILESTONES_AND_EXIT_GATES.md`
- `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_TARGET_STATE.drawio`

实现阶段完成允许声明：

- V2.101-V2.105 文档完整支撑范围内的 project discovery、project build orchestration、document/media intake、portfolio panel、release gate 已实现并通过 focused tests。

实现阶段仍不允许声明：

- 任意 workspace 下所有项目均被完整理解。
- 图片和扫描件在 OCR 不可用时已被理解。
- UI 截图替代真实建库证据。
- 所有项目组合出门验收全绿，除非所有高风险项都有真实 accepted evidence。
