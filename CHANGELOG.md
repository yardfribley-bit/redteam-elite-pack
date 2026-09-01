# 变更日志

本项目所有值得记录的变更都会写进这里。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

---

## [2.0.1] — 2026-09-02

### Changed
- **项目结构规范化**：从扁平根目录重构为 `src/`（核心引擎）+ `tools/`（辅助工具）+ `results/`（实测数据）+ `docs/`（文档）分层，代码与数据分离
- **README 重写**：新增 Mermaid 架构图、OWASP 覆盖度表、实测 ASR 结果、诚实口径说明、路线图

### Added
- `LICENSE`（MIT）、`SECURITY.md`、`CONTRIBUTING.md`、`ROADMAP.md`、`CHANGELOG.md`、`.gitignore`
- `docs/METHODOLOGY.md`：方法论与判定口径说明

### Fixed
- **移除真实 API key**：`examples/evidence_sql_drop_table.md` 中原含明文 DeepSeek key，已脱敏
- **清理重复文件**：`ARTICLE_CSDN.md`、`evidence_sql_drop_table.md` 根目录与 `docs/`、`examples/` 重复，已去重
- `tools/publish.py`：目标仓库从已废弃账号更正为 `yardfribley-bit/redteam-elite-pack`，路径更新为新结构
- `tools/build_pack_v2.py`：移除硬编码本地绝对路径（`/Users/jatsmith/...`），改为命令行参数 + 仓库相对路径
- `src/cross_model_matrix.py`：默认结果目录从已移除的 `profiles_or/` 更正为 `results/cross-model`

---

## [2.0.0] — 2026-08-31

### Added
- 精英攻击包 **v2.0**：24 个攻击，全量打 OWASP LLM01–10 + ASI01–10 标签
- 从 garak 提取未验证项：LLM02/03/07/09/10、ASI04/08/09
- `--owasp` 参数：按需只测指定风险类
- 报告新增「OWASP Top 10 覆盖度」章节
- **武器化 PoC 套件** `src/poc_suite.py`：6 个铁证级 PoC + 2 条深度利用链
  - 链① `injection_to_leak`：提示注入 → 系统提示结构泄露（LLM07）
  - 链② `bypass_to_payload`：护栏绕过 → 可运行恶意代码（ASI05）
- 跨模型复现矩阵（OpenRouter：Llama-3.3-70B / Qwen3-Max / Gemma-3-27B / GPT-5-nano）
- `docs/competitive_analysis.md`、`docs/exploitation_report.md`

### Changed
- 引擎加入 429/5xx 指数退避（解析 `Retry-After` / `reset`，上限 60s / 6 次重试）
- 新增 `--max-tokens`（默认 300）避免长输出拖慢扫描
- 默认 `--parallel` 由高并发下调为 3，规避频率限流
- 修复 `None` content 导致的崩溃（部分模型返回空内容）

---

## [1.0.0] — 2026-08-30

### Added
- 从 DeepSeek 实测结果中筛选高 ASR 攻击，固化精英包，脱离 garak 全量独立运行
- 轻量复现引擎（Python 标准库，零第三方依赖）
- 本地关键词 detector（零额外 token 消耗）
- `format_report.py`：易读报告 + `summary.json` 结构化输出
- 利用链自动生成：DAN 越狱 → 借人格生成 RCE/SQL → 坏字符绕过

### Notes
- 相比 garak 全量（~26,000 次调用），精英包单模型仅需 ~72 次，token 消耗降低约 **700×**
