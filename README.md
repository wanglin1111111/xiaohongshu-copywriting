# 小红书高质量文案创作技能

> 基于实际发布经验与社区反馈持续优化

## 核心理念

真实 > 营销感。小红书社区对AI生成内容和营销号语气极度敏感。

## 特性

- ✅ 事实核查清单：防止CVPR/SIGGRAPH类混淆错误
- ✅ 语气控制：去除AI味，像真人说话
- ✅ 领域适配：3D/AI/半导体/消费电子等专业领域模板
- ✅ 发布前自检：3个核心问题快速排雷
- ✅ 避坑指南：基于真实评论区反馈总结的常见错误
- ✅ 品牌内容营销全链路：需求洞察、投入优先级、内容策略、达人筛选、效果评估、AI+HI 分工

## 使用场景

- 科技产品发布会文案
- 技术分析内容
- 行业趋势解读
- 产品测评文案
- 品牌种草与达人投放策略
- 内容需求洞察与效果复盘

## 文件结构

```
xiaohongshu-copywriting/
├── README.md      ← 项目说明
├── SKILL.md       ← 核心技能文件
├── references/
│   └── brand-marketing-playbook.md  ← 品牌内容营销方法论
├── scripts/
│   └── validate.py                  ← 品牌 brief + 笔记格式校验器
├── tests/
│   ├── sample_good.md               ← 合格样例（exit 0）
│   ├── sample_bad.md                ← 不合格样例（exit 1）
│   └── sample_failure.md            ← 失败态样例（三类异常+下一步）
└── LICENSE        ← MIT许可证
```

## 校验

```bash
python scripts/validate.py tests/sample_good.md    # 期望 exit 0
python scripts/validate.py tests/sample_bad.md     # 期望 exit 1
python scripts/validate.py tests/sample_failure.md # 期望 exit 0
```

## 版本

v1.1.0 (2026-11-03) - 新增品牌内容营销模块（需求洞察/投入优先级/内容策略/达人筛选/效果评估/AI+HI 分工），原有技术/创作者文案规则保留
v1.0.0 (2026-06-28) - 基于影眸科技发布会文案的真实反馈迭代
