#!/usr/bin/env python3
"""xiaohongshu-copywriting 校验器。

用法：
  python validate.py <draft.md>
  python validate.py            # 默认 ../tests/sample_good.md

判据：
  - 品牌内容策略 brief：六个主题齐全；四问；六筛子；三档；双钩子；
    达人三项；热度≠价值/不制造新焦虑；2.5x/+80%/-50% 必须标“益普索单案例/方向参考/不能当 KPI”。
  - 小红书笔记草案（可选）：标题 ≤20、正文 300-600、标签 5-8、无违禁词、有资料来源。
  - 失败态样例：输入异常/依赖不可达/权限被拒 三节，每节含“下一步”。
退出码：0=全部通过；1=有错误；2=只有警告。
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ERRORS = []
WARNINGS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def parse_sections(text):
    sections = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = {"title": m.group(1), "body": []}
            sections.append(cur)
            continue
        if cur is not None:
            cur["body"].append(line)
    for s in sections:
        s["body"] = "\n".join(s["body"])
    return sections


def find_section(sections, *keys):
    for s in sections:
        if any(k in s["title"] for k in keys):
            return s
    return None


FAILURE_CLASSES = [
    ("输入异常", re.compile(r"(输入|入参|参数).*?(异常|为空|空值|截断|缺失|格式|无效)")),
    ("依赖不可达", re.compile(r"(依赖|外部服务|网络|接口|API|脚本|引用文件).*?(不可达|缺失|失败|超时|不可用|不存在)")),
    ("权限被拒", re.compile(r"(权限|授权|凭据|鉴权|沙箱).*?(被拒|不足|拒绝|失效|缺失|只读)")),
]


def check_failure_sample(sections):
    for label, pat in FAILURE_CLASSES:
        sec = next((s for s in sections if pat.search(s["title"])), None)
        if not sec:
            err(f"失败态缺节：{label}")
        elif "下一步" not in sec["body"]:
            err(f"失败态「{label}」没有「下一步」")


def check_brief(text, sections):
    required = [
        ("需求洞察", ("需求洞察",)),
        ("投入优先级", ("投入优先级",)),
        ("内容策略", ("内容策略",)),
        ("达人筛选", ("达人筛选",)),
        ("效果评估", ("效果评估",)),
        ("AI + HI 分工", ("AI", "HI")),
    ]
    for label, keys in required:
        if not find_section(sections, *keys):
            err(f"缺少主题：{label}")

    q = find_section(sections, "四问", "一句话")
    qtext = q["body"] if q else text
    if not all(k in qtext for k in ("场景", "内容", "传递", "加码")):
        err("缺少「一句话四问」（场景→内容→传递→加码）")

    filters = ["话题内容", "重复", "互动", "品牌定位", "产品适配", "合规"]
    if sum(1 for f in filters if f in text) < 5:
        err("六个筛子不足 5 个（话题内容/重复/互动/品牌定位/产品适配/合规）")

    if not all(x in text for x in ("持续经营", "继续探索", "暂缓投入")):
        err("缺少投入三档：持续经营/继续探索/暂缓投入")

    if not all(x in text for x in ("功能钩子", "情绪钩子")):
        err("缺少双钩子：功能钩子 + 情绪钩子")

    if not all(x in text for x in ("内容特征", "粉丝画像", "需求匹配")):
        err("达人筛选缺少三项：内容特征/粉丝画像/需求匹配")

    for line in text.splitlines():
        if "粉丝量" in line and not re.search(r"失效|删掉|不看|不是|不做|不把|权重", line):
            err(f"仍把粉丝量当筛选指标：{line.strip()}")

    if re.search(r"2\.5|＋?\+?80|−50|-50", text):
        if "益普索" not in text or not re.search(r"单案例|方向参考|不能|不宜|打折", text):
            err("引用了 2.5x/+80%/-50%，但未标「益普索单案例/方向参考/不能当 KPI」")

    for sec in sections:
        if re.search(r"反模式|禁止|不要", sec["title"]):
            continue
        for line in sec["body"].splitlines():
            if re.search(r"热度就是价值|追热点排产|制造新焦虑|粉丝量优先", line):
                err(f"反模式出现在正文：{line.strip()}")


def check_note(sections):
    note = find_section(sections, "小红书笔记")
    if not note:
        warn("未找到「小红书笔记草案」，跳过笔记格式检查")
        return
    body = note["body"]

    tm = re.search(r"###\s*标题\s*\n+(.+?)(?:\n|$)", body)
    bm = re.search(r"###\s*正文\s*\n(.*?)(?=\n###\s*标签|\Z)", body, re.S)
    gm = re.search(r"###\s*标签\s*\n(.*?)(?=\n##|\Z)", body, re.S)

    if not tm:
        err("笔记缺「### 标题」")
        title = ""
    else:
        title = tm.group(1).strip()
        if len(re.sub(r"\s", "", title)) > 20:
            err(f"标题超过 20 字：{title}")

    if not bm:
        err("笔记缺「### 正文」")
        text = ""
    else:
        text = re.sub(r"\s", "", bm.group(1))
        if not (300 <= len(text) <= 600):
            err(f"正文长度 {len(text)} 字，要求 300-600")

    if not gm:
        err("笔记缺「### 标签」")
        tags = []
    else:
        tags = re.findall(r"#\S+", gm.group(1))
        if not (5 <= len(tags) <= 8):
            err(f"标签数 {len(tags)}，要求 5-8")
        if len(tags) != len(set(tags)):
            err("标签有重复")

    banned = ["绝对", "100%", "根治", "秒杀", "国家级", "顶级", "史上", "万能", "永久", "零风险", "保证", "第一", "唯一"]
    blob = " ".join([title, bm.group(1) if bm else "", gm.group(1) if gm else ""])
    for w in banned:
        if w in blob:
            err(f"笔记含违禁/绝对化词：{w}")

    if bm and not re.search(r"资料：|来源：", bm.group(1)):
        err("笔记缺资料来源（资料：/来源：）")


def main():
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
    else:
        p = Path(__file__).resolve().parent.parent / "tests" / "sample_good.md"
    if not p.exists():
        print(f"FAIL 文件不存在：{p}")
        sys.exit(1)

    text = p.read_text(encoding="utf-8")
    sections = parse_sections(text)

    is_failure = any(pat.search(s["title"]) for _, pat in FAILURE_CLASSES for s in sections)
    if is_failure:
        check_failure_sample(sections)
    else:
        check_brief(text, sections)
        check_note(sections)

    for e in ERRORS:
        print(f"FAIL {e}")
    for w in WARNINGS:
        print(f"WARN {w}")
    print(f"SUMMARY errors={len(ERRORS)} warnings={len(WARNINGS)} file={p.name}")

    if ERRORS:
        sys.exit(1)
    if WARNINGS:
        sys.exit(2)
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
