# 陷阱反例、运行日志与复现率

1.1.2 的反例在 Linux/amd64 的任务镜像中执行，环境为 Python 3.12.16、Django 5.1.15。每组输入独立运行三次，同组日志的 SHA-256 一致。程序和命令见[反例目录](../CS-XX-001/solution/counterexamples/)。

| 程序和输入 | 三次观测 | 日志（第 1 次） |
|---|---|---|
| ce1，Decimal 和 Django 字段量化 | 六种情形中，默认舍入与 ROUND_HALF_UP 的结果均不同 | [ce1](../CS-XX-001/tests/assets/selfcheck/linux-amd64-1.1.2/ce1-run1.log) |
| ce2，初始快照加草稿补丁 | 每次复现 7/7 个缺陷 | [草稿](../CS-XX-001/tests/assets/selfcheck/linux-amd64-1.1.2/ce2-guessed-run1.log) |
| ce2，初始快照加参考补丁 | 每次观测 0/7 个缺陷 | [参考解](../CS-XX-001/tests/assets/selfcheck/linux-amd64-1.1.2/ce2-golden-run1.log) |

第二组的七个观测分别检查价格提示、分批结算、购物车显示合计、订单行合计、四位单件税额、含税金额在购物车／订单／页面的一致性，以及搜索索引价格。ce2 的返回码约定为发现缺陷时退出 0，全部观测正常时退出 1。正式判分另走 `tests/test.sh`。

[其余重复运行日志](../CS-XX-001/tests/assets/selfcheck/linux-amd64-1.1.2/) · [早期开发期的上游 4.2.2 本地对照](../CS-XX-001/solution/counterexamples/ce2_upstream_4.2.2_local.log)
