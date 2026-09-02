# 贡献指南

感谢你愿意让 RedTeam Elite Pack 变得更好。这个项目最需要的是**真实、可复现的实测数据**——你在任何模型上跑出的 ASR，都比十行代码更有价值。

---

## 最欢迎的贡献类型

| 类型 | 说明 | 难度 |
|---|---|---|
| 🧪 **补测模型** | 在更多模型上跑 `--poc all --chain all`，提交 `results/` 下的数据 | ⭐ |
| 🔍 **修正误报** | detector 是关键词匹配，误报难免；发现误报请提 Issue 并附证据 | ⭐ |
| 🎯 **新增攻击** | 往 `src/attack_pack.json` 加条目，或从 garak 提取新探针 | ⭐⭐ |
| 🐛 **Bug 修复** | 引擎、退避逻辑、报告生成 | ⭐⭐ |
| 📖 **文档** | 补充 runbook、翻译、修正过时描述 | ⭐ |

---

## 新增一条攻击

最小条目（`src/attack_pack.json` 的 `attacks` 数组内）：

```json
{
  "id": "your_attack_id",
  "category": "jailbreak",
  "name": "攻击名称（中文）",
  "severity": "critical",
  "source_probe": "garak.module.ProbeName",
  "owasp": ["LLM01", "ASI01"],
  "validated_asr": 0.0,
  "validated_model": "待测",
  "detector": {
    "type": "keyword",
    "hit": ["关键词1", "关键词2"]
  },
  "exploitable": true,
  "prompts": ["你的攻击 prompt"]
}
```

字段约定：

- `owasp` 必填，取值来自 `LLM01–10` / `ASI01–10`（见 `docs/OWASP_MAPPING.md`）
- `severity`：`critical` / `high` / `medium` / `low`
- `validated_asr`：**首次提交填 `0.0` 并把 `validated_model` 标为 `待测`**；只有在真实目标上跑过 ≥3 次采样后才更新为实测值
- `detector.hit` 关键词请保守——宁可漏报，不要误报

若要从 garak 批量提取，改 `src/build_pack.py` 的 `targets` 字典后重跑即可：

```bash
python3 src/build_pack.py
python3 tools/build_pack_v2.py --garak-prompts /path/to/garak_prompts.json
```

---

## 提交实测数据

把扫描产物放到 `results/<模型名>/`，目录内建议包含：

```
results/your-model/
├── profile.json        # 引擎原始输出
├── report.md           # format_report 生成的可读报告
├── summary.json        # 结构化聚合数据
└── poc-evidence/       # poc_suite 的证据 JSON（可选）
```

生成方式：

```bash
python3 src/redteam_engine.py --model <model> --key $KEY --generations 3 --out results/your-model
python3 src/format_report.py results/your-model/profile.json
```

**请在 PR 说明中注明**：模型全名、端点类型（官方/中转/自托管）、采样次数、测试日期。

---

## 提交前自检清单

- [ ] 代码中**不含任何真实 API key / token / 密码**
- [ ] 未提交 `or_key.txt`、`.env` 等被 `.gitignore` 排除的文件
- [ ] 新增攻击已填 `owasp` 标签
- [ ] 若修改了判定逻辑，已说明对历史 ASR 数据的影响
- [ ] Python 脚本保持**零第三方依赖**（仅标准库）
- [ ] **若改动影响用户可见行为**（命令、路径、目录结构、功能），
      `README.md`（英文）与 `README_CN.md`（中文）**都已同步更新**

---

## 关于双语 README

仓库维护两份 README，内容必须保持一致：

| 文件 | 定位 |
|---|---|
| `README.md` | **英文主文件** —— GitHub 索引与落地页读取它，面向国际检索 |
| `README_CN.md` | 完整中文版 —— 面向中文社区（CSDN / FreeBuf / 知乎读者） |

两份顶部都挂了语言切换链接。修改其中一个时请同步另一个——尤其注意**命令行示例、目录结构树、ASR 数据**这三处最容易走偏。

`docs/` 下的深度文档目前以中文为主，**欢迎提交英文翻译**，这是当前最缺的贡献类型之一。

---

## 行为准则

本项目遵循 [Contributor Covenant](https://www.contributor-covenant.org/) 精神。请保持技术讨论聚焦、尊重、基于证据。
