# V2.111-V2.115 Gap Analysis

## 1. 当前缺口

| 缺口 | 当前状态 | 风险 | 处理策略 |
| --- | --- | --- | --- |
| OCR/media 真实执行 | V2.106-V2.110 仅有 readiness/matrix | 媒体资料被误写 accepted | V2.111 执行 provider 或 structured unavailable |
| OCR 真实样本资格 | 当前 workspace 可能只有可直接抽取文本的 PPT/PDF，缺真实文本型图片/扫描件 | 直接文本抽取被误写为 OCR accepted | V2.111 先生成 `ocr_sample_qualification.json`；缺样本时 OCR 保持 structured unavailable |
| Source trace 全链路 | 缺 import/query/source trace 完整证据 | 文件存在被误当 source evidence | V2.112 三段链路缺一不可 |
| UI 截图证据 | `/knowledge` panel 已接入但截图缺失 | HTML/report 替代真实体验 | V2.113 headless 截图或 browser blocker |
| 多项目安全 build | 队列已有，safe runtime 不完整 | 执行危险命令或有界冒充全量 | V2.114 allowlist/sandbox/timeout/cache |
| Final release gate | 当前 `structured_unavailable` | false-green 出门 | V2.115 聚合重跑并保留 blockers |

## 2. 关键技术风险

### R1：OCR/Office/Browser 依赖缺失

风险：本地环境可能没有 tesseract、LibreOffice、Chromium。

策略：不自动安装；输出 structured unavailable、provider health、next action。

如果 workspace 没有真实可 OCR 文本样本，即使 conversion/text extraction 可用，也不得将 OCR 行 accepted。

### R2：外部项目 build script 不可信

风险：执行 `/mnt/c/workspace/*` 下脚本可能修改文件、访问网络或泄露环境变量。

策略：默认只执行 allowlisted safe commands；未批准命令只进入 queue/diagnosis，不执行。

### R3：Evidence mixed-run

风险：OCR、source trace、UI、build artifacts 来自不同 run，被 final gate 混合 accepted。

策略：每个 artifact 必须包含 run_id、input_hashes、workspace_fingerprint；final gate 拒绝 mixed-run。

### R4：UI 截图影响用户电脑

风险：可见浏览器抢焦点或弹窗影响用户。

策略：优先 headless；若必须 visible browser，先停下来告知用户。

### R5：文档 claim 替代 code/source evidence

风险：drawio、HTML、docs/present 被当作实现证据。

策略：final gate 只接受 command/API/MCP/UI artifact evidence；docs 只作为 spec review 输入。

## 3. 备选技术路线

| 路线 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- |
| A：模块化单体内实现 | 复用 workspace runtime、source trace、portfolio artifacts；部署简单 | 需要严格包边界 | 推荐 |
| B：独立 worker 服务 | sandbox 边界更强 | 部署、权限、artifact lineage 复杂 | 暂不采用 |
| C：只做文档阻断不执行 | 最安全、实现快 | 无法推进 final accepted | 仅作为 provider 不可用 fallback |

## 4. 文档阶段结论

当前缺口可以通过 V2.111-V2.115 阶段计划消减；无需扩大到 full call graph、runtime topology、data/control flow 或 type inference。
