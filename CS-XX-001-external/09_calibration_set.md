# 标杆四件套与等价实现索引

补丁和逐条结果单都在题包里，这里是索引。得分取自任务镜像内的预检，每份连跑 3 次，三次一致。

| 样例 | 补丁 | 结果单 | 预期得分 | 实际得分 | 通过单测 |
|---|---|---|---|---|---|
| 满分标杆 | `tests/calibration/full_score.patch` | `tests/calibration/full_score_result.md` | 1 | 1 | 41 / 41 |
| 等价变体 | `tests/calibration/equivalent.patch` | `tests/calibration/equivalent_result.md` | 1 | 1 | 41 / 41 |
| 缺陷样例 | `tests/calibration/defective.patch` | `tests/calibration/defective_result.md` | 0 | 0 | 31 / 41 |
| 蒙对样例 | `tests/calibration/guessed.patch` | `tests/calibration/guessed_result.md` | 0 | 0 | 22 / 41 |
| 等价实现 A | `solution/variants/variant_a.patch` | `solution/variants/README.md` | 1 | 1 | 41 / 41 |
| 等价实现 B | `solution/variants/variant_b.patch` | `solution/variants/README.md` | 1 | 1 | 41 / 41 |

缺陷样例埋了三处缺陷，每处对应的失败单测见结果单。蒙对样例只做草稿说的两处改动，题面两个症状都消失，得 0 分。
