# 路线图

项目按「先把验证闭环跑通 → 再扩覆盖面 → 最后工程化接入」推进。欢迎在 Issue 里投票或认领。

---

## ✅ 已完成

### v2.0 — OWASP 对齐 + 武器化（当前）
- [x] 精英攻击包 v2.0：24 个攻击，全量打 **OWASP LLM01–10 + ASI01–10** 标签
- [x] 从 garak 提取未验证项，补齐 LLM02/03/07/09/10、ASI04/08/09 探针
- [x] 零依赖扫描引擎（`--owasp` 过滤、429/5xx 指数退避、`--max-tokens`）
- [x] 报告新增「OWASP Top 10 覆盖度」章节 + `summary.json` 结构化输出
- [x] **武器化 PoC 套件**：6 个铁证级 PoC + 2 条深度利用链
  - 链① `injection_to_leak`：提示注入 → 系统提示结构泄露（LLM07）
  - 链② `bypass_to_payload`：护栏绕过 → 可运行恶意代码（ASI05）
- [x] 跨模型复现矩阵（OpenRouter 4 模型）
- [x] 项目结构规范化：`src/` `tools/` `results/` `docs/` 分层 + 完整文档体系

### v1.0 — 精英包 + 轻量引擎
- [x] DeepSeek 实测筛选出高 ASR 攻击，脱离 garak 独立运行
- [x] 本地关键词 detector（零额外 token）
- [x] 利用链自动生成

---

## 🚧 进行中 / 计划中

### v2.1 — 覆盖面补齐
- [ ] 补测未验证项：LLM02（敏感信息泄露）、LLM03（供应链）、LLM07、LLM09、LLM10
- [ ] 补测 Agentic 未验证项：ASI04、ASI08、ASI09
- [ ] 引入 **LLM-as-judge 二次复核**，自动剔除「拒答回声」误报
- [ ] detector 支持正则与多关键词组合逻辑（AND/OR/NOT）

### v2.2 — 自托管靶机链路
- [ ] 自托管 runbook：4090 + vLLM 起 Qwen3-14B / DeepSeek-Distill
- [ ] 一键脚本：拉镜像 → 起端点 → 接攻击包 → 出报告
- [ ] 支持量化模型（AWQ/GPTQ）靶机的显存/上下文建议表

### v3.0 — Agent 与工程化
- [ ] agent harness 接入，覆盖 **ASI03 / ASI07 / ASI10**（工具调用 / 记忆投毒 / 多 agent 通信）
- [ ] 多轮对话攻击（当前仅单轮）
- [ ] 导出 **SARIF** 与 JSON Schema，接入 CI 安全门禁
- [ ] 结果可视化面板（跨模型 ASR 趋势）

---

## 💡 长期构想

- 建立**公开的模型安全基线榜**：社区提交各模型 ASR，形成可持续追踪的横向对比
- 攻击包版本化与签名，便于复现历史结论
- 与 garak / PyRIT 生态互操作（导入导出探针）

---

## 🙋 认领

想在某条上贡献？开个 Issue 说明你打算做哪一条即可，我们会同步进展避免重复劳动。参见 [CONTRIBUTING.md](CONTRIBUTING.md)。
