# V2.101-V2.105 Gap Analysis

## 1. 当前架构与目标架构差异

| 当前状态 | 目标状态 | Gap |
| --- | --- | --- |
| 只能手动对单项目执行 code import/snapshot/overview | 自动发现 workspace 下多个项目并分类 | 缺 workspace portfolio scanner 和 classifier |
| DataService ingest 支持目录，但没有按项目组合编排 | 项目 docs 和纯资料目录可形成 source candidate matrix | 缺 docs/media intake orchestration |
| OCR provider 代码存在，但当前环境 OCR 不可用 | 图片/扫描件 readiness 可见并可审计 | 缺 media readiness matrix 和 `/knowledge` 呈现 |
| `/knowledge` 是通用控制台 | `/knowledge` 可展示项目组合真实状态 | 缺 portfolio panel 和 persisted artifact read |
| V2.96 release gate 仍非全绿 | 新阶段只解决 portfolio 知识化，不伪造旧阶段 final accepted | 需要明确边界，避免把 portfolio accepted 当 final release accepted |

## 2. 主要风险

- False-green：目录扫描成功被写成项目理解 accepted。
- False-green：UI 截图替代建库和 query/source trace evidence。
- False-green：图片、扫描 PDF、图片型 PPT 无 OCR 证据却 accepted。
- False-green：docs claim 被当作 code fact。
- Scope creep：把本阶段扩展为完整多模态项目理解平台。
- Side effect：扫描时修改外部项目或写入外部项目目录。

## 3. 缓解策略

- project registry 每行必须有 detected markers 和 evidence refs。
- code project accepted 必须绑定 codebase import、snapshot、inventory/symbols、project brief 或 overview artifacts。
- doc/media 如果声明 ingest accepted，必须绑定 extractor/build/query/source trace 或 OCR evidence；readiness-only 只能保持 non-accepted。
- 有界 scan/build 是默认可复跑路线；超出有界范围的项目必须记录为 `needs_review` 和 next action，不能 silent skip。
- `/knowledge` 只读取 API persisted artifacts。
- 所有 external path 用脱敏 path_ref，不暴露本机绝对路径。
- release gate 使用最差高风险状态。

## 4. 文档阶段判定

当前 V2.101-V2.105 文档目标可支撑下一阶段自动化开发指导，但不能证明任何 V2.101-V2.105 功能已实现。

## 5. 高风险目标与备选技术路线

### 5.1 风险：多媒体资料全绿验收依赖 OCR/provider

当前文档可以支撑“自动识别、分类、记录 readiness、保留 `ocr_required` 或 `structured_unavailable`”的实现，但不能仅靠文档保证图片、扫描 PDF、图片型 PPT 的内容级理解全绿。若用户要求 `portfolio_final_status=accepted`，必须选择额外技术路线。

| 路线 | 方案 | 优点 | 缺点 | 出门影响 |
| --- | --- | --- | --- | --- |
| A：结构化不可用优先 | 不安装 OCR；图片/扫描件统一输出 `ocr_required` 或 `structured_unavailable` | 实现风险最低，不污染环境，false-green 风险低 | 不能声明多媒体内容已完整入库 | `implementation_status=accepted` 可达成；`portfolio_final_status=accepted` 可能不可达成 |
| B：本地 OCR/provider | 接入本机 Tesseract、poppler、LibreOffice/soffice 等可复跑依赖 | 可提升图片、扫描 PDF、PPT 转换覆盖率，数据不离本机 | 环境依赖重，安装与版本漂移风险高 | provider health 通过后可推动更多媒体行 accepted |
| C：外部视觉/OCR 服务 | 通过显式配置的外部 OCR/视觉 API 处理图片资料 | 覆盖率高，部署快 | 需要网络、费用、隐私和脱敏审批 | 只有完成隐私/脱敏/调用证据后才能 accepted |

默认文档基线选择路线 A。路线 B 或 C 需要在进入实现前单独形成 provider readiness plan、隐私/脱敏约束和验收命令。
