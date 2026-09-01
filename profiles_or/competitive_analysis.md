# 竞品 / 同行调研：谁在做「OWASP LLM + Agentic 红队」这件事

> 调研时间：2026-09-01 ｜ 目的：给自己将在 CSDN / FreeBuf 发的文章做差异化定位
> 范围：GitHub 开源工具 + CSDN/FreeBuf/Unit42/Huawei 中文实战文章 + 统计类报告
> 我们自己的基线：RedTeam Elite Pack（从 garak 提炼的精英攻击包 v2.0，24 攻击/49 prompt）+ OpenRouter 跨 4 模型真实复现（带 ASR）+ 2 条可武器化利用链（injection→LLM07 泄露、bypass→恶意代码）

---

## 0. TL;DR（一句话结论）

**市面上「覆盖型扫描器」和「方法论教程」已经很多，但「裸模型端点 + 实测 ASR + 可武器化利用链」三者合一的可复现 PoC 包几乎是空的。** 这就是我们的差异化切口——不卖"能跑 100 个探针"，而是证明"这几个攻击在 4 个主流模型上真的打穿了，并且能串成有业务危害的利用链"。

---

## 1. 谁在做同类事（按形态分类）

### 1.1 全量 LLM 扫描器（开源，探针最多）
| 工具 | 来源 | 形态 | 与我们重叠度 |
|---|---|---|---|
| **garak** | NVIDIA | 命令行，数百个 probe，覆盖 OWASP LLM 大类 | 高（我们攻击包就是从它提炼的） |
| **PyRIT** | Microsoft | 红队框架，攻击策略+打分 | 中（框架，不是现成攻击包） |
| **promptfoo** | promptfoo Inc. | LLM 安全/红队 eval，yaml 配置 | 中 |
| **awesome-llm-security** | 社区 | 资源清单，非工具 | 低（索引） |

> 这类工具的共同点：**求覆盖、求探针数量**，输出是 pass/fail 矩阵；基本不直接给"这条攻击在哪些模型真实打穿 + 证据样本 + 可复用利用链"。

### 1.2 OWASP 合规套件（最接近我们的竞品）
- **Okareo `compliance-owasp`** — https://github.com/okareo-ai/compliance-owasp ｜ 文档 https://docs.okareo.ai/red-teaming/owasp
  - 覆盖 **全部 20 类（LLM01–10 + ASI01–10）**，55 个离散场景；含**对抗 driver 人格（多轮）+ 模型判定 judge + 代码判定 + Jupyter notebook + CLI runner**。
  - 亮点：明确区分 single-turn / multi-turn 评测模式；LLM07 系统提示提取、LLM09、LLM10 都有专门场景。
  - **关键差异**：它面向"已注册的 Agent 靶标" + Okareo SaaS 部署目标，不是裸模型端点；偏"合规证据"而非"武器化利用"。
- 博客定位原话：*Most teams hand-build a few prompt-injection prompts, run them once, and call it coverage. Or they license a closed-box scanner that returns a verdict but doesn't produce evidence.* —— 它卖的是"可审计证据"，不是攻击本身。

### 1.3 Agentic 专用基准（需 agent 运行时 / 工具调用环）
| 工具 | 来源 | 覆盖 | 形态 |
|---|---|---|---|
| **AgentThreatBench** | 英国 AISI，已并入 `inspect_evals` | ASI01/ASI06（记忆投毒、目标劫持、数据外泄）3 任务，200+ payload | `pip install inspect-evals`，需工具调用 loop |
| **AgentShield** | doronp | Agentic 基准 | 开源 |
| **PurpleLlama / CyberSecEval** | Meta | 提示注入 + 代码安全，正讨论并入 AgentThreatBench | 开源 |

> 这类工具**必须跑真实 agent（有 planner/tools/memory）**，不是 chat/completions 端点能复现的。我们的轻量引擎（仅 chat/completions）天然不覆盖 ASI03/07/10，与它们的定位不同——它们测"agent 运行时"，我们测"模型本身的可利用性"。

### 1.4 中文实战文章（CSDN / FreeBuf / 厂商报告）
- **CSDN `a13662080711`《OWASP LLM Top10 全链路实战》**：从威胁建模→分层漏洞测试→工具检测→复现→加固，带 Python 检测脚本（Base64 绕过、Trivy 供应链扫描）。偏**方法论 + 教学**，不给跨模型 ASR。
- **CSDN `cailiangfei`（独角鲸网络安全实验室）《AI红队实战全教程：OWASP LLM Top10 攻击 Payload 与工具链》**：直接给可复制的攻击 Payload（覆盖系统提示、分隔符绕过、RAG 投毒）+ 工具安装清单。偏 **Payload 合集**。
- **FreeBuf《AI红队实战手册》**：在 Llama3-8B 上跑过 garak，给了实操记录。
- **Unit42（Palo Alto）**：专题讲 DeepSeek 越狱（Bad Likert Judge / Crescendo / Deceptive Delight 三种技术）。
- **华为云**：DeepSeek Agent 注入、以及"通过训练数据投毒做 SQL 注入"（vanna + DeepSeek）的实战。
- **BytePulse（CSDN）**：DeepSeek 红队报告。
- **ringsafe / redfoxsec**：方法论指南。

> 中文文章的整体特征：**碎片化越狱 Prompt 教程 + 全链路原理讲解为主**，多数停在"教你怎么打"，极少附带"跨多模型实测通过率 + 可复用 PoC + 利用链危害证明"。

### 1.5 统计 / 营销类报告
- **Axis Intelligence《LLM Jailbreak Statistics 2026》**：引用 Hagendorff et al.（Nature Communications, 2026-02）大型推理模型**自主越狱 9 个生产模型 97.14% 成功率**（25,200 条输入，零人工）；**DeepSeek-V3 危害分最高 90%**，Claude 4 Sonnet 最低 2.86%（差 31 倍）；JBFuzz 平均 99% ASR、单查 <60s。AI 红队市场 2026 年 $2.26B（+28.8%）。
- 这类报告**只给宏观数字，不给可复现攻击**，适合做文章里的"行业背景"段。

---

## 2. 差异化定位矩阵

| 维度 | garak/PyRIT | Okareo compliance-owasp | AgentThreatBench | 中文 CSDN/FreeBuf 教程 | **我们的 RedTeam Elite Pack** |
|---|---|---|---|---|---|
| 覆盖 OWASP 类 | LLM 为主 | **全 20 类** | 仅 Agentic(ASI) | 原理/部分 | LLM 10 + Agentic 7（ASI03/07/10 需运行时，未覆盖） |
| 是否需要 Agent 运行时 | 否 | 是（靶标+SaaS） | **是（必需）** | 否 | 否（裸 chat/completions） |
| 跨模型真实 ASR | 部分 | 按靶标 | 按模型 | 基本无 | **有（DeepSeek/Llama3.3-70B/Qwen3-Max/Gemma3-27B 实测）** |
| 可武器化利用链 | 无 | 无（证据导向） | 场景级 | 无 | **有（injection→LLM07 泄露、bypass→keylogger 代码、SQL echo→真实 SQLi）** |
| 证据样本/可复现 | 日志 | 审计记录 | 评测日志 | Payload 文本 | **JSON 证据 + 一键 PoC 脚本** |
| 开源可跑 | 是 | 是（需 SaaS） | 是（需 loop） | 文本 | **是（自包含 urllib，无依赖）** |

### 我们的 3 个独特卖点
1. **真实 ASR，不是"能跑"**：每个攻击给出 `broke/safe` 计数和命中证据样本，跨 4 个主流模型对比——这是 garak 探针和中文教程普遍缺失的。
2. **利用链证明业务危害**：不止"模型说了一句不该说的"，而是把点串成链——注入逼出系统提示（LLM07）、护栏绕过产出可运行恶意代码、SQL 回显直接可用于打后端库。
3. **自包含、裸端点可跑**：不依赖 Agent 运行时、不绑定 SaaS，一个 `urllib` 脚本 + OpenRouter key 就能复现，最适合写进文章让读者"复制即跑"。

### 一个反差卖点（诚实的假阴性）
我们同时也**公开了打不穿的硬骨头**（LLM07/09/10、ASI08 在 4 个模型全 0%），并说明哪些高 ASR 是"拒答回声"误报。这和 Axis Intelligence 那种"97% 越狱"的营销口径形成反差——**可信度更高，更适合技术读者**。

---

## 3. 文章角度建议（CSDN / FreeBuf）

**推荐标题**：《我们扒了 4 个主流大模型：OWASP LLM Top10 红队实战 + 可武器化利用链》

**核心叙事（区别于"越狱 Prompt 合集"）**：
- 不是教你怎么写越狱词，而是：**从 NVIDIA garak 提炼精英攻击包 → 在 OpenRouter 跨 4 个模型跑真实 ASR → 把命中项串成有业务危害的利用链**。
- 三段式：① 攻击包怎么从 garak 蒸馏出来（方法论）；② 跨模型实测战果表（DeepSeek V3 / Llama3.3-70B / Qwen3-Max / Gemma3-27B，含实锤与误报诚实标注）；③ 两条利用链拆解（injection→系统提示泄露、bypass→键盘记录器源码），配真实证据片段。
- 收尾：哪些打了、哪些没打穿、为什么——给读者可落地的加固清单。

**不要写成**：纯越狱 Prompt 教程（CSDN 已泛滥，易被限流/封）；纯合规套件介绍（Okareo 已占）。

---

## 4. 参考链接
- Okareo compliance-owasp: https://github.com/okareo-ai/compliance-owasp ｜ 文档 https://docs.okareo.ai/red-teaming/owasp
- AgentThreatBench (UK AISI / inspect_evals): https://github.com/UKGovernmentBEIS/inspect_evals ｜ https://ukgovernmentbeis.github.io/inspect_evals/evals/agent_threat_bench
- garak: https://github.com/NVIDIA/garak
- PyRIT: https://github.com/Azure/PyRIT
- promptfoo: https://github.com/promptfoo/promptfoo
- Axis Intelligence Jailbreak Stats 2026: https://axis-intelligence.com/llm-jailbreak-statistics/
- CSDN 全链路实战: https://blog.csdn.net/a13662080711 ｜ CSDN 独角鲸实验室教程: https://cailiangfei.blog.csdn.net/article/details/162543733
- FreeBuf AI红队实战手册 / Unit42 DeepSeek 越狱 / 华为云 DeepSeek 注入（搜索结果见上）
