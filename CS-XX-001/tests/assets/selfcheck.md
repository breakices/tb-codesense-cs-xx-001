# CS-XX-001 1.1.2 自检

以 `linux/amd64` 任务镜像执行 8 类提交，每类 3 次，验证入口为 `sh /tests/test.sh`。每次从同一未修复快照启动独立容器。全部容器使用 `--network none` 和只读的 `/tests` 挂载。Golden 先执行 `sh /solution/solve.sh`；NOP 直接评分。每个 JSON 都包含 41 个已执行的具名单测及逐条结果。同名前缀的压缩包保留每次的原始 stdout、stderr、JUnit 记录和 reward。

[本次运行环境](selfcheck/linux-amd64-1.1.2/ENVIRONMENT.txt) · [汇总及输入文件哈希](selfcheck/linux-amd64-1.1.2/SUMMARY.json) · [24 份原始运行记录](selfcheck/linux-amd64-1.1.2/) · [复验脚本](selfcheck/run_linux.py)

参考解、满分标杆、等价样例和两个变体各通过 41/41，奖励均为 1。未修改起点通过 23/41，缺陷样例通过 31/41，蒙对样例通过 21/41，三者奖励均为 0。

三次运行均为有效评分，未出现跳过和收集错误。按编号比较三次结果，逐项通过/失败状态与整题得分均一致。原样提交通不过的目标单测是 U10、U14、U24。U14 检查运费折扣在分位的四舍五入，实际断言为 `assert Decimal('0.62') == Decimal('0.63')`。草稿引入 10 项原样提交可通过的回归，涉及 U15、U16、U17、U18、U22、U23、U27、U39、U40、U41。

草稿补丁三次均复现全部七个业务缺陷，参考解三次均为 0/7。2026 年 11 月的历史模型答卷另按版本归档。[标杆与逐项判分单](../../../CS-XX-001-external/09_calibration_set.md) · [反例日志](../../../CS-XX-001-external/04_trap_counterexamples.md) · [模型错误证据](../../../CS-XX-001-external/05_model_failure_evidence.md) · [基线记录](../../../CS-XX-001-external/06_baseline.md)

盲测时，作答环境只包含题面和初始代码。复验脚本在挂载评分材料前检查 `/tests` 和 `/solution` 均不存在。[复验脚本](selfcheck/run_linux.py)
