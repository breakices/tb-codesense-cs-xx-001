# CS-XX-001 1.1.2 自检

以 `linux/amd64` 任务镜像执行 8 类提交，每类 3 次，验证入口为 `sh /tests/test.sh`。每次从同一未修复快照启动独立容器。全部容器使用 `--network none` 和只读的 `/tests` 挂载。Golden 先执行 `sh /solution/solve.sh`；NOP 直接评分。每个 JSON 都包含 41 个已执行的具名单测及逐条结果。同名压缩包保留每次的原始 stdout、stderr、JUnit 记录和 reward。

[本次运行环境](selfcheck/linux-amd64-1.1.2/ENVIRONMENT.txt) · [汇总及输入文件哈希](selfcheck/linux-amd64-1.1.2/SUMMARY.json) · [24 份原始运行记录](selfcheck/linux-amd64-1.1.2/) · [复验脚本](selfcheck/run_linux.py)

## 工程自检

| 提交 | 三次整题得分 | 每次通过数 | 每次实际失败的单测 |
|---|---|---|---|
| [原样提交 NOP](selfcheck/linux-amd64-1.1.2/nop-run1.json) | 0 / 0 / 0 | 23 / 41 | U1、U2、U3、U4、U5、U6、U7、U8、U9、U10、U11、U12、U13、U14、U19、U24、U28、U35 |
| [参考修复 Golden](selfcheck/linux-amd64-1.1.2/golden-run1.json) | 1 / 1 / 1 | 41 / 41 | 无 |
| [满分标杆](selfcheck/linux-amd64-1.1.2/full_score-run1.json) | 1 / 1 / 1 | 41 / 41 | 无 |
| [等价实现](selfcheck/linux-amd64-1.1.2/equivalent-run1.json) | 1 / 1 / 1 | 41 / 41 | 无 |
| [缺陷样例](selfcheck/linux-amd64-1.1.2/defective-run1.json) | 0 / 0 / 0 | 31 / 41 | U15、U16、U17、U18、U22、U23、U24、U27、U40、U41 |
| [蒙对样例](selfcheck/linux-amd64-1.1.2/guessed-run1.json) | 0 / 0 / 0 | 21 / 41 | U7、U8、U9、U10、U12、U13、U14、U15、U16、U17、U18、U19、U22、U23、U24、U27、U28、U39、U40、U41 |
| [变体 A](selfcheck/linux-amd64-1.1.2/variant_a-run1.json) | 1 / 1 / 1 | 41 / 41 | 无 |
| [变体 B](selfcheck/linux-amd64-1.1.2/variant_b-run1.json) | 1 / 1 / 1 | 41 / 41 | 无 |

三次运行均为有效评分，未出现跳过和收集错误。按编号比较三次结果，逐项通过/失败状态与整题得分均一致。原样提交通不过的目标单测是 U10、U14、U24。U14 检查运费折扣在分位的四舍五入，实际断言为 `assert Decimal('0.62') == Decimal('0.63')`。草稿引入 10 项原样提交可通过的回归，涉及 U15、U16、U17、U18、U22、U23、U27、U39、U40、U41。

四份校准补丁的结果单记录 41 条断言各自的判定，缺陷补丁和草稿补丁还按语义错误列出了命中单测。两个其他等价变体的实现差异见变体说明。

[满分标杆](../calibration/full_score_result.md) · [等价样例](../calibration/equivalent_result.md) · [缺陷样例](../calibration/defective_result.md) · [蒙对样例](../calibration/guessed_result.md) · [变体说明](../../solution/variants/README.md)

## 本版关键验收

- U7 在 17.5% 税率下直接检查 £0.03 商品的单件税额 £0.0053，并核对 200 件的含税合计 £7.06。U8 从父商品报价入口直接检查税额。
- U22 等分批用例检查落库明细、每批金额、累计金额和最终结清。对 30 件税前单价 £0.03 的订单，旧版等价样例曾结算 £1.16、−£0.08，共 £1.08。新版样例按分分摊，分批结果详见等价样例结果单。
- U5 保留英国定价策略既有的促销金额基数。税前 £9.99 的商品三件、折扣 15% 时，折扣额 £5.3946 在默认配置下从税前合计 £29.97 扣除，结果为 £24.58。
- U27、U28 从历史持久化价格验证告警，以顾客可见的分位金额变化为准。U25、U26 从订单记录和已有结算事件验证剩余应收金额。

## 模型校准与交付隔离

1.1.2 尚无五模型校准数据。旧 38 项版本的五份 Opus 答卷中三份全过，原答卷按后来增加的 41 项重判后有一份全过。另有四份针对 1.1.0 的有效新答卷，其中三份全过。历史答卷、失败模式与日期见 [基线材料](../../../CS-XX-001-external/06_baseline.md) 和 [错误模式证据](../../../CS-XX-001-external/05_model_failure_evidence.md)。这些记录均早于本次验收条件。

发布库含参考补丁和评分材料。正式盲测仅向模型提供题面和未修复源码，模型退出后由隔离的评分器加载本目录。本版复验脚本先在未挂载评分材料的镜像内检查 `/tests`、`/solution` 均不存在。旧版镜像隔离记录见 [历史检查](selfcheck/linux-amd64/isolation.log)。

历次样例自检的 [旧 Linux 结果](selfcheck/linux-amd64/) 和 [1.1.1 本机结果](selfcheck/local-current-1.1.1/) 保留供版本追溯。[反例程序与既有复现记录](../../solution/counterexamples/README.md) 展示了草稿里的默认舍入以及七个下游观测点。
