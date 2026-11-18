# CS-XX-001 自检结论

当前修订版本：1.1.1。Golden/NOP 证据以 41-test 版本为准，历史 38-test 文件已移入外部历史归档。v6 Opus 运行属于 1.1.0 候选，1.1.1 的边界修订后需要重新校准。

任务镜像中的冻结证据在 `tests/assets/selfcheck/linux-amd64/`。1.1.1 对旧购物车测试的强化在本机环境重新跑了当前 patch 样例，证据在 `tests/assets/selfcheck/local-current-1.1.1/`。

运行环境：

```
date_utc: 2026-11-18T15:33:02Z
host_kernel: Linux 5.15.152-amd64 x86_64
docker: 28.5.2
image: cs-xx-001:1.0.0 sha256:375ed9bd8ee332d897b3ddf743d2f3799c4c3132e961ef8878379444c6456d78 (environment snapshot unchanged for task 1.1.1)
image_platform: linux/amd64
interpreter: 3.12.14 Linux-5.15.152-amd64-x86_64-with-glibc2.36 django 5.1.15 pytest 8.4.2
snapshot_commit_in_image: d34ac017e72423af0e99980377d8ef441a2f6c6b
snapshot_tree_in_image: bdea6eaad6894e6167d11d03ae43019d10127467
```

## 汇总

| 提交 | 三次得分 | 三次通过单测 | 逐条结果三次一致 | 失败的单测 |
|---|---|---|---|---|
| nop | 0 0 0 | 25 25 25 / 41 | 是 | U1、U2、U3、U4、U5、U6、U7、U8、U9、U10、U11、U12、U13、U14、U19、U35 |
| golden | 1 1 1 | 41 41 41 / 41 | 是 | 无 |
| full_score | 1 1 1 | 41 41 41 / 41 | 是 | 无 |
| equivalent | 1 1 1 | 41 41 41 / 41 | 是 | 无 |
| defective | 0 0 0 | 31 31 31 / 41 | 是 | U15、U16、U17、U18、U22、U23、U24、U27、U40、U41 |
| guessed | 0 0 0 | 22 22 22 / 41 | 是 | U7、U8、U9、U10、U12、U13、U14、U15、U16、U17、U18、U19、U22、U23、U24、U27、U39、U40、U41 |
| variant_a | 1 1 1 | 41 41 41 / 41 | 是 | 无 |
| variant_b | 1 1 1 | 41 41 41 / 41 | 是 | 无 |

## 1. 陷阱可复现

结论：通过。两个反例程序在任务镜像里触发陷阱，输出见 `solution/counterexamples/README.md`。
`ce1_default_rounding.py` 展示 `Decimal.quantize` 与 `DecimalField` 落库的默认舍入是银行家舍入；`ce2_draft_consequences.py` 在只做草稿两处改动的仓库上观测到 7 项缺陷中的 7 项，在参考修复上是 0 项。前四项和第七项是整改前成立、被草稿的改法破坏的关系；第七项是搜索索引里的价格。
陷阱是确定性的。重复运行的记录：

```
ce1 run 1 sha256: 500748aca68998bc
ce1 run 2 sha256: 500748aca68998bc
ce1 run 3 sha256: 500748aca68998bc
ce2 on the draft-only tree, run 1: defects observed: 7 of 7, sha256 42c6a97640a7299a
ce2 on the draft-only tree, run 2: defects observed: 7 of 7, sha256 42c6a97640a7299a
ce2 on the draft-only tree, run 3: defects observed: 7 of 7, sha256 42c6a97640a7299a
```

## 2. 双向预检

结论：通过。Golden 三次得分 1 1 1，NOP 三次得分 0 0 0。

- 两路都从同一个任务镜像新起容器，一次运行一个容器，用完即删，互不共享文件。
- 快照标识是镜像内 `/workspace/repo` 的 git 树对象，每份日志的 `tree before` 一行记录了它，两路相同。
- Golden 路在容器内应用 `solution/golden/golden.patch`，日志的 `tree when scored` 一行记录应用后的树对象和改动文件数。
- NOP 路不应用任何补丁，日志里 `no patch applied`，`tree when scored` 的改动文件数是 0。
- 判分命令是 `docker exec -u root <容器> sh /tests/test.sh`，隐藏测试以只读方式挂在 `/tests`。
- 全部 41 个声明的单测都被收集并执行，没有跳过，没有收集错误。
- NOP 失败的 16 条：U1、U2、U3、U4、U5、U6、U7、U8、U9、U10、U11、U12、U13、U14、U19、U35。其中针对预设 badpattern 的有 U10、U14。
- NOP 通过的 25 条是整改前就成立的关系和回归项。其中 U15、U16、U17、U18、U22、U23、U24、U27、U39、U40、U41 这 11 条会被只做草稿两处的改法破坏，见蒙对检验。
- NOP 的一条目标断言的失败证据，U1：`AssertionError: assert Decimal('0.00') == Decimal('0.20') | +  where Decimal('0.00') = <Basket: Open basket (owner: None, lines: 1)>.total_tax | +  and   Decimal('0.20') = D('0.20') @ test_money_contr`
- U27/U28 直接 seed 历史两位小数 `BasketLine` 记录价后再 reload，覆盖旧购物车的兼容性比较；订单历史金额由 U25/U26 的直接持久化夹具覆盖。
- 完整输出：`nop-run{1,2,3}.log/.json`、`golden-run{1,2,3}.log/.json`。

## 3. 变体自检

结论：通过。`solution/variants/variant_a.patch` 与 `variant_b.patch` 三次都得 1 分，41 个单测全部通过。等价论证见 `solution/variants/README.md`。

## 4. 蒙对检验

结论：通过。`tests/calibration/guessed.patch` 三次都得 0 分，通过 22 / 41。它的语义错误被目标单测捕获：U7、U8、U9、U10、U12、U13、U14、U15、U16、U17、U18、U19、U22、U23、U24、U27、U39、U40、U41。逐条说明见 `guessed_result.md`。

## 5. 误杀检验

结论：通过。`tests/calibration/equivalent.patch` 三次都得 1 分。加上两个变体，共有三个写法不同的实现通过全部单测。

## 6. 满分基准

结论：通过。`tests/calibration/full_score.patch` 三次都得 1 分。

## 7. 缺陷识别

结论：通过。`tests/calibration/defective.patch` 三次都得 0 分。缺陷 1 被 U27、U40 捕获。缺陷 2 被 U22、U23、U24、U41 捕获。缺陷 3 被 U15、U16、U17、U18 捕获。与 `defective_result.md` 一致。

## 8. 判分确定性

结论：通过。上表 8 个提交各连跑 3 次，整题得分和逐条结果全部一致。判分不调用模型，不联网，不依赖时间和随机数。测试数据的编号来自进程内计数器，每次运行相同。

## 9. 模型错误模式取证

结论：已取证 6 条，每条附真实答卷片段，答卷在 `tests/assets/baseline_runs/` 与 `tests/assets/earlier_calibration/`，条目见 task.toml 的 `model_failure_modes`。当前题面下有真实失败答卷的是 FM1 和 FM2；FM3 到 FM6 的答卷来自定稿之前的题面，各条的采集日期和模型写在条目里。

- FM1：搜索索引里的商品价格没有处理。单价保留四位小数以后，ProductIndex.prepare_price 写进索引的是 1.1880，商品页显示的是 1.19。价格筛选、价格区间和按价格排序用的数与顾客看到的数不再一致。答卷改了定价、购物车、订单、运费和展示，没有打开 search 应用。 命中 U39。
- FM2：运费的百分比折扣仍按默认的银行家舍入取整。答卷没有打开 offer/benefits.py，ShippingPercentageDiscountBenefit.shipping_discount 里的 quantize(D("0.01")) 保持原样。运费 2.50 的 25% 折扣额算出 0.62，应为 0.63。 命中 U14。
- FM3：把单价改成四位小数以后，没有处理订单的价格明细和按明细逐件累加的分批结算。100 件 0.01 的订单行金额是 1.20，按 30 件、70 件两批结算得到 0.30 加 0.70，合计 1.00。 命中 U21、U22、U23、U24、U41。
- FM4：购物车行的价格变动提示直接比较四位小数的现价和两位小数的记录价，价格没变也提示从 £1.19 降到 £1.19。 命中 U27、U40。
- FM5：照草稿在合计处统一舍入一次。两行各 0.036 时，页面上每行显示 0.04，合计显示 0.07；订单行之和与订单合计也差一分。 命中 U15、U16、U17、U18。
- FM6：展示金额的模板过滤器没有处理。四位小数的金额直接交给 Babel，按默认的银行家舍入量化，0.7050 显示成 £0.70，而合计是 £0.71。 命中 U10。

## 10. 基线模型试测

结论：未完成。需求指定五个模型各 5 次，目前只有 Claude Opus 5.5，且 41-test 冻结候选只有 4 次有效新鲜运行。

历史 5 次盲测是在 38 条单测版本上完成的。之后新增 U39 到 U41，并对原答卷重判，没有重新调用模型。U39 是查看答卷后新增的测试，因此历史结果只作为开发集证据。

| 版本候选运行 | 模型 | 通过单测 | 失败项 | 状态 |
|---|---|---|---|---|
| v6m-01 | opus5.5 | 39 / 41 | U14、U39 | 有效 |
| v6r-01 | opus5.5 | 41 / 41 | 无 | 有效 |
| v6r-02 | opus5.5 | 41 / 41 | 无 | 有效 |
| v6n-01 | opus5.5 | 41 / 41 | 无 | 有效 |
| v6a-01 | opus5.5 | 无 | 配额 429 | 无效 |
| v6m-02 | opus5.5 | 无 | 空 agent.json | 无效 |

原始答卷、逐条结果和历史统计在 `tests/assets/baseline_runs/`。当前候选的有效运行记录由 Aaron session 和开发机运行目录保存。因网络或接口错误中断的运行不计入模型结果。

## 11. 隔离检查

结论：通过。任务镜像里没有 `solution/` 与 `tests/` 的任何文件，题面和仓库里没有参考答案、陷阱名称和结论线索。检查输出：

```
image: cs-xx-001:1.0.0
  files named like hidden material: 0
  /tests or /solution present: 0
  files under /workspace containing identifiers of the reference fix or of the tests: 0
  entries directly under /workspace: repo 
image: cs-xx-001-agent:claude-2.1.318
  files named like hidden material: 0
  /tests or /solution present: 0
  files under /workspace containing identifiers of the reference fix or of the tests: 0
  entries directly under /workspace: repo 
instruction.md, occurrences of trap names:
  银行家: 0
  HALF_EVEN: 0
  get_warning: 0
  价格变动: 0
  currency_filters: 0
  Babel: 0
  DecimalField: 0
  先加总: 0
  逐行: 0
  to_cents: 0
```

## 已知限制

1. 基线只有部分模型的结果，难度门槛和区分度指标还不能下结论。
2. 被测模型通过 Claude Code 在任务容器里作答。容器用的是主机网络，模型调用经一条隧道转发，除此之外没有出网路由。
3. 依赖版本以 `tests/requirements.lock` 为准。它是在运行主机的包索引上解析得到的，与公共索引上的同名版本一致。
4. 仓库自带测试在 SQLite 上有少量与本题无关的既有失败，参考修复前后相同。
