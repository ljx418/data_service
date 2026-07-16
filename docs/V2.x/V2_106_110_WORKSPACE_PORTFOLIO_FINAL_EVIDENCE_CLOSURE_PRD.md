# V2.106-V2.110 PRD：Workspace Portfolio Final Evidence Closure

## 1. 阶段定位

V2.101-V2.105 已完成 workspace portfolio 的有界实现，并通过 focused tests、真实 `/mnt/c/workspace` E2E、PRD/spec review 和 false-green audit。当前状态是：

```text
implementation_status=accepted
portfolio_final_status=structured_unavailable
```

V2.106-V2.110 的目标是把未闭环项转成可复跑、可审计、可明确阻断的 final evidence closure，而不是扩大项目理解承诺。

本阶段仍然不得声明：

- 已完整恢复复杂项目设计意图。
- 已具备 full call graph、runtime topology、data/control flow 或 type inference。
- OCR 缺失的图片、扫描 PDF、图片型 PPT 已被理解。
- 未构建项目已被 accepted。
- UI 截图、HTML report 或 scan-only evidence 可替代 build/source trace evidence。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不可计入 accepted。

## 2. 当前事实基线

| 项 | 当前状态 | 下一阶段目标 |
| --- | --- | --- |
| V2.101-V2.105 coverage matrix | 已回填实现状态，但需持续与证据绑定 | 形成 V2.106 closure 输入，不再显示已实现实体为 planned |
| Workspace scan | 18 个项目/目录，9 个 ignored | 保持真实扫描，支持 full build governance |
| Project build | 1 个真实代码项目 accepted，17 个项目 needs_review | 建立多项目 build 调度、缓存、失败隔离和增量复跑计划 |
| Media/OCR | `ocr_required_count=86`，OCR provider structured_unavailable | 规划 OCR/provider 检测、媒体证据、失败分类和补证路径 |
| Document ingest/source trace | 未覆盖全部 source candidates | 规划 accepted 文档从 import 到 query/source trace 的证据闭环 |
| `/knowledge` UI evidence | HTTP 200，headless screenshot structured_unavailable | 规划可复跑 headless 截图或结构化阻断 |
| Release gate | implementation accepted，portfolio final non-accepted | 规划 final release gate 的 accepted/blocker 判定 |

## 3. 阶段目标

| 阶段 | 名称 | 目标体验 |
| --- | --- | --- |
| V2.106 | Coverage Matrix and Architecture State Closure | 维护者能看到当前实现、缺口、证据路径和下一阶段输入一致 |
| V2.107 | OCR and Media Evidence Closure | 维护者能看到每个媒体资料的 OCR/provider 状态、失败分类和补证路径 |
| V2.108 | Full Workspace Project Build Governance | Agent 能调度多个 workspace 项目构建，并获得缓存、超时、失败隔离和 next action |
| V2.109 | Document Ingest / Query / Source Trace Closure | 审计者能复核每个 accepted 文档资料的 import、query、source trace 证据链 |
| V2.110 | Portfolio Final Release Gate | 系统能判断 portfolio 是否 final accepted；如不能，给出阻断原因和最小补证路径 |

## 4. 目标用户体验

### 4.1 维护者

维护者应能在 `/knowledge` 或 HTML report 中看到：

- 哪些 V2.101-V2.105 能力已经 accepted。
- 哪些项目仍未构建，为什么不能 accepted。
- 哪些媒体资料需要 OCR/provider 或人工确认。
- 哪些文档资料已完成 ingest/query/source trace，哪些仍只是 readiness。
- final release gate 为什么通过或阻断。

### 4.2 Coding Agent

Coding Agent 应能：

- 读取 project build backlog 和 source trace backlog。
- 针对一个未构建项目获得明确 build command、cache policy、timeout policy 和 failure diagnosis。
- 在 OCR、source trace 或 UI evidence 不足时输出 `needs_review` 或 `structured_unavailable`。
- 不把 docs claim 当作 code fact。

### 4.3 审计者

审计者应能：

- 复跑真实 `/mnt/c/workspace` E2E。
- 检查 accepted 行是否具备 artifact refs、command refs、source refs、query/source trace refs 或 structured blocker。
- 确认 release gate 没有把 `needs_review`、`structured_unavailable` 计入 accepted。

## 5. In Scope

- V2.101-V2.105 文档状态回填和架构状态同步。
- OCR/provider readiness、media evidence contract、失败分类和补证路径。
- 多项目 build governance contract：队列、缓存、超时、失败隔离、增量复跑。
- Document ingest/query/source trace closure contract。
- Headless UI evidence 或结构化不可用。
- Portfolio final release gate、false-green audit、PRD/spec review。

## 6. Out of Scope

- 自动安装 OCR、LibreOffice、Chrome、Chromium 或系统依赖。
- 自动修改被扫描项目。
- 自动删除、移动或重写 workspace 下任何文件。
- 承诺完整项目理解、完整调用图、运行时拓扑、数据流、控制流或类型推断。
- 默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## 7. 完成定义

文档阶段完成必须满足：

1. PRD、目标架构、开发验收计划、覆盖矩阵、测试映射、里程碑、gap analysis、pre-implementation audit、document audit、drawio 全部落盘。
2. drawio 不超过 8 页，中文书写，展示目标体验、当前到目标架构、代码实体分层、数据/证据流、开发验收计划、出门条件、No-Go。
3. 每个阶段都有 artifact contract、public surface 计划、focused test 名称、真实 E2E 输入、PRD/spec review 和 false-green audit。
4. 明确 `portfolio_final_status` 不能在高风险项未闭环时 accepted。
5. 当前文档只可声明 `pass for implementation guidance`，不得声明 V2.106-V2.110 已实现。
