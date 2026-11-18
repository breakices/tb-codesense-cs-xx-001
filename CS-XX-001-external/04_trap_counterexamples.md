# 陷阱反例、运行日志与复现率

反例程序和日志在题包的 `solution/counterexamples/`，说明见该目录的 `README.md`。这里是索引和结论。

| 文件 | 内容 |
|---|---|
| `ce1_default_rounding.py` | 语言和框架的默认舍入是银行家舍入：`Decimal.quantize` 不传 `rounding`、`DecimalField` 落库 |
| `ce1_default_rounding.log` | 上一个程序在任务镜像里的输出 |
| `ce2_draft_consequences.py` | 对一个仓库做七项观测，统计有缺陷的项数 |
| `ce2_draft_only.log` | 在只做草稿两处改动的仓库上，任务镜像内：defects observed: 7 of 7 |
| `ce2_reference.log` | 在参考修复上，任务镜像内：defects observed: 0 of 7 |
| `ce2_upstream_4.2.2_local.log` | 在上游 4.2.2 上，本机运行，仅作旁证：defects observed: 7 of 7 |
| `repeat_check.log` | 两个程序在任务镜像里各连跑 3 次的输出摘要 |

## 七项观测

1 到 4 和第 7 项是整改前成立、被草稿的改法破坏的关系：页面各行与合计、订单行与订单合计、分批结算与订单行、价格没变时的提示、搜索索引里的价格与页面上的价格。
5 和 6 是默认舍入不是四舍五入的两处：第四位小数上的单件税额、分位上的含税金额。

## 复现率

陷阱是确定性的。两个程序在任务镜像里各连跑 3 次，输出逐字相同，触发率 3/3：

```
ce1 run 1 sha256: 500748aca68998bc
ce1 run 2 sha256: 500748aca68998bc
ce1 run 3 sha256: 500748aca68998bc
ce2 on the draft-only tree, run 1: defects observed: 7 of 7, sha256 42c6a97640a7299a
ce2 on the draft-only tree, run 2: defects observed: 7 of 7, sha256 42c6a97640a7299a
ce2 on the draft-only tree, run 3: defects observed: 7 of 7, sha256 42c6a97640a7299a
```
