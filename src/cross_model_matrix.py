#!/usr/bin/env python3
"""
跨模型 OWASP 复现矩阵：扫描 results/cross-model/*/profile.json，把每个模型按
LLM01-10 / ASI01-10 的命中情况拼成一张对比表，并标出"所有模型都未复现"的硬骨头。

用法: python3 src/cross_model_matrix.py --profiles results/cross-model --out results/cross-model/cross_model_repro.md

注意：脚本默认从仓库根目录解析结果目录，因此请在仓库根目录执行。
"""
import argparse, json, os, glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LLM_LABELS = {
    "LLM01": "提示注入", "LLM02": "敏感信息泄露", "LLM03": "供应链",
    "LLM04": "数据/模型投毒", "LLM05": "输出处理不当", "LLM06": "过度代理",
    "LLM07": "系统提示泄露", "LLM08": "向量/嵌入弱点", "LLM09": "虚假信息",
    "LLM10": "无界消耗",
}
ASI_LABELS = {
    "ASI01": "目标/指令篡改", "ASI02": "工具滥用", "ASI03": "记忆投毒*",
    "ASI04": "Agent供应链", "ASI05": "非预期代码执行", "ASI06": "级联错误",
    "ASI07": "流氓Agent*", "ASI08": "人-Agent信任", "ASI09": "资源耗尽",
    "ASI10": "多Agent失配*",
}
# 模型目录 -> 展示名（顺序即列顺序）
MODEL_ORDER = [
    ("deepseek_v3_0324", "DeepSeek v3"),
    ("meta-llama__llama-3.3-70b-instruct", "Llama-3.3-70B"),
    ("qwen__qwen3-max", "Qwen3-Max"),
    ("google__gemma-3-27b-it", "Gemma-3-27B"),
    ("openai__gpt-5-nano", "GPT-5-nano"),
]

def load_model(d):
    pj = os.path.join(d, "profile.json")
    if not os.path.exists(pj):
        return None
    prof = json.load(open(pj))
    attacks = {}
    all_resp_empty = True
    for r in prof["results"]:
        tags = r.get("owasp", [])
        attacks[r["id"]] = {"asr": r.get("asr", 0.0), "broke": r.get("broke", 0),
                             "name": r.get("name", ""), "owasp": tags}
        for s in r.get("samples", []):
            if str(s.get("resp", "")).strip():
                all_resp_empty = False
    return {"model": prof.get("model"), "attacks": attacks, "empty": all_resp_empty}

def best_for_cat(attacks, cat):
    """返回该 OWASP 类别下 ASR 最高的攻击 (asr, name) 或 None"""
    cands = [a for a in attacks.values() if cat in a["owasp"] and a["asr"] > 0]
    if not cands:
        return None
    b = max(cands, key=lambda x: x["asr"])
    return (b["asr"], b["name"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", default=os.path.join(REPO_ROOT, "results", "cross-model"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    models = []
    for d, label in MODEL_ORDER:
        m = load_model(os.path.join(a.profiles, d))
        if m:
            models.append((label, m))
    if not models:
        print("no profiles found"); return
    present = [l for l, _ in models]
    print("loaded models:", present)

    def table(fam, labels):
        L = [f"### {fam} Top 10", ""]
        head = "| 风险 | " + " | ".join(present) + " | 代表攻击(最强模型) |"
        L.append(head)
        L.append("|---" + "|---" * len(present) + "|---|")
        hard = []  # 所有模型都未复现
        for cid, name in labels.items():
            row = [f"{cid} {name}"]
            best_overall = None
            any_hit = False
            for _, m in models:
                if m.get("empty"):
                    row.append("无效*")
                    continue
                b = best_for_cat(m["attacks"], cid)
                if b:
                    any_hit = True
                    row.append(f"**{b[0]*100:.0f}%**")
                    if best_overall is None or b[0] > best_overall[0]:
                        best_overall = b
                else:
                    row.append("—")
            rep = best_overall[1] if best_overall else "—"
            L.append("| " + " | ".join(row) + f" | {rep} |")
            if not any_hit:
                hard.append(f"{cid} {name}")
        L.append("")
        return L, hard

    L = ["# 跨模型 OWASP 十大安全风险复现矩阵（OpenRouter 实测）", ""]
    L.append(f"- 模型: {', '.join(present)}")
    L.append(f"- 攻击包: 24 精英攻击 × 5 代 = 245 调用/模型；判定 = 本地关键词 detector（ASR 含拒答回声，详见口径说明）")
    L.append("")
    t1, h1 = table("OWASP LLM", LLM_LABELS)
    t2, h2 = table("OWASP Agentic (ASI)", ASI_LABELS)
    L += t1 + t2
    L.append(f"**所有模型都未复现（硬骨头）：LLM → {', '.join(h1) or '无'}；ASI → {', '.join(h2) or '无'}**")
    L.append("")
    L.append("> 口径与诚实提醒：ASR 由本地关键词 detector 给出，命中样本里可能含「模型拒答但回声了敏感词」的误报，"
             "因此带 **加粗%** 仅表示 detector 命中率，不等同于铁证级攻破。铁证需人工核对 report.md 证据。"
             "*ASI03/07/10 需 agent 运行时，本引擎未含对应攻击，故恒为 —；「无效*」= 该模型本次调用全部返回空响应"
             "（区域限制/内容过滤，如 GPT-5-nano），不计入有效结果。")
    md = "\n".join(L)
    out = a.out or os.path.join(a.profiles, "cross_model_repro.md")
    open(out, "w").write(md)
    print(md)
    print(f"\n-> {out}")

if __name__ == "__main__":
    main()
