# 标杆四件套与等价实现索引

在同一初始快照上分别应用每份补丁。整题奖励以完整测试的逐项结果计算；标杆运行与模型盲测分开记录。1.1.2 的实际得分、通过数和重复运行记录见[Linux 自检证据](../CS-XX-001/tests/assets/selfcheck/linux-amd64-1.1.2/)。

| 样例 | 补丁 | 判定说明 | 1.1.2 通过单测（三次一致） | 实际奖励 |
|---|---|---|---|---|
| 满分标杆 | [full_score.patch](../CS-XX-001/tests/calibration/full_score.patch) | [逐项判分单](../CS-XX-001/tests/calibration/full_score_result.md) | 41 / 41 | 1 |
| 等价变体 | [equivalent.patch](../CS-XX-001/tests/calibration/equivalent.patch) | [逐项判分单](../CS-XX-001/tests/calibration/equivalent_result.md) | 41 / 41 | 1 |
| 缺陷样例 | [defective.patch](../CS-XX-001/tests/calibration/defective.patch) | [逐项判分单](../CS-XX-001/tests/calibration/defective_result.md) | 31 / 41 | 0 |
| 蒙对样例 | [guessed.patch](../CS-XX-001/tests/calibration/guessed.patch) | [逐项判分单](../CS-XX-001/tests/calibration/guessed_result.md) | 21 / 41 | 0 |
| 等价实现 A | [variant_a.patch](../CS-XX-001/solution/variants/variant_a.patch) | [实现说明](../CS-XX-001/solution/variants/README.md) | 41 / 41 | 1 |
| 等价实现 B | [variant_b.patch](../CS-XX-001/solution/variants/variant_b.patch) | [实现说明](../CS-XX-001/solution/variants/README.md) | 41 / 41 | 1 |

1.1.1 的等价变体会在前一批已超收的情况下产生负数尾款。1.1.2 替换了这份补丁，验收同时检查落库明细、每一批的结算和累计金额。历史标杆得分只能按其当时的验收范围解读。
