# 模型错误模式的真实答卷证据

## FM1

搜索索引里的商品价格没有处理。单价保留四位小数以后，ProductIndex.prepare_price 写进索引的是 1.1880，商品页显示的是 1.19。价格筛选、价格区间和按价格排序用的数与顾客看到的数不再一致。答卷改了定价、购物车、订单、运费和展示，没有打开 search 应用。

- 模型：opus5.5
- 采集日期：2026-11-18
- 命中特征：改一查十：与症状没有调用关系、仓库自带测试不覆盖的远处使用点
- 对应单测：U39
- 证据：

  - `2026-11-18 采集，模型 claude-opus-5-5，Claude Code 2.1.318，任务镜像内盲测。5 份有效答卷中的 4 份：tests/assets/baseline_runs/opus5.5/ 下 rs41-opus55-v5-02、rs41-opus55-v5-04、rs41-opus55-v5b-01、rs41-opus55-v5b-02，四份 answer.patch 都不包含 src/oscar/apps/search/search_indexes.py`
  - `同一批的第 5 份答卷 rs41-opus55-v5-05 自己改了这个文件，注释为 Index the price as shown to customers (rounded to whole pence)`
  - `只做草稿两处改动的 tests/calibration/guessed.patch 同样触发`

## FM2

运费的百分比折扣仍按默认的银行家舍入取整。答卷没有打开 offer/benefits.py，ShippingPercentageDiscountBenefit.shipping_discount 里的 quantize(D("0.01")) 保持原样。运费 2.50 的 25% 折扣额算出 0.62，应为 0.63。

- 模型：opus5.5
- 采集日期：2026-11-18
- 命中特征：改一查十：同一条舍入规则散落在多个模块，漏掉离症状较远的一处
- 对应单测：U14
- 证据：

  - `2026-11-18 采集，模型 claude-opus-5-5，Claude Code 2.1.318，任务镜像内盲测。5 份有效答卷中的 2 份：rs41-opus55-v5-02 与 rs41-opus55-v5b-02，result.json 中 U14 的实际输出为 assert Decimal('0.62') == Decimal('0.63')`
  - `两份 answer.patch 都不包含 src/oscar/apps/offer/benefits.py`
  - `第 3 版题面下的 opus55-v3-04、opus55-v3-05 也是同一处，见 tests/assets/earlier_calibration/`

## FM3

把单价改成四位小数以后，没有处理订单的价格明细和按明细逐件累加的分批结算。100 件 0.01 的订单行金额是 1.20，按 30 件、70 件两批结算得到 0.30 加 0.70，合计 1.00。

- 模型：opus5.5；另有 haiku、sonnet、opus 档位的本机试答
- 采集日期：2026-11-17 至 2026-11-18
- 命中特征：修症状的改动破坏题面没有点名的下游环节
- 对应单测：U21、U22、U23、U24、U41
- 证据：

  - `2026-11-18 采集，模型 claude-opus-5-5，Claude Code 2.1.318，任务镜像内盲测，第 3 版题面：5 份答卷全部如此，见 tests/assets/earlier_calibration/opus55-v3-0*.result.json，U22 的实际输出为 assert Decimal('1.00') == Decimal('1.20')`
  - `2026-11-17 采集，本机 Claude Code 子代理试答，题面初稿：mac-probe-haiku、mac-probe-sonnet、mac-probe-opus 三份都未通过 U22 到 U24 与 U41，mac-probe-opus 另未通过 U21`
  - `当前题面下的 5 份有效答卷都处理了这一处`

## FM4

购物车行的价格变动提示直接比较四位小数的现价和两位小数的记录价，价格没变也提示从 £1.19 降到 £1.19。

- 模型：opus5.5；另有 haiku、sonnet、opus 档位的本机试答
- 采集日期：2026-11-17 至 2026-11-18
- 命中特征：精度改动使已有的相等比较失效
- 对应单测：U27、U40
- 证据：

  - `2026-11-18 采集，模型 claude-opus-5-5，第 3 版题面：答卷 opus55-v3-05，见 tests/assets/earlier_calibration/opus55-v3-05.result.json`
  - `2026-11-17 采集，本机 Claude Code 子代理试答，题面初稿：mac-probe-haiku、mac-probe-sonnet、mac-probe-opus 三份都未通过 U27 与 U40`
  - `只做草稿两处改动的 tests/calibration/guessed.patch 同样触发`

## FM5

照草稿在合计处统一舍入一次。两行各 0.036 时，页面上每行显示 0.04，合计显示 0.07；订单行之和与订单合计也差一分。

- 模型：opus5.5；另有 haiku 档位的本机试答
- 采集日期：2026-11-17 至 2026-11-18
- 命中特征：采信草稿里的错误说法：先加总再舍入与逐项舍入再相加不等价
- 对应单测：U15、U16、U17、U18
- 证据：

  - `2026-11-18 采集，模型 claude-opus-5-5，Claude Code 2.1.318，任务镜像内盲测，第 1 版题面：答卷 v1-opus55-01 未通过 U15 到 U18，见 tests/assets/earlier_calibration/v1-opus55-01.result.json`
  - `2026-11-17 采集，本机 Claude Code 子代理试答，题面初稿：mac-probe-haiku 未通过 U16`
  - `只做草稿两处改动的 tests/calibration/guessed.patch 同样触发`

## FM6

展示金额的模板过滤器没有处理。四位小数的金额直接交给 Babel，按默认的银行家舍入量化，0.7050 显示成 £0.70，而合计是 £0.71。

- 模型：haiku、sonnet、opus 档位的本机试答
- 采集日期：2026-11-17
- 命中特征：改一查十：舍入规则在展示层的使用点
- 对应单测：U10
- 证据：

  - `2026-11-17 采集，本机 Claude Code 子代理试答，题面初稿：mac-probe-haiku、mac-probe-sonnet、mac-probe-opus 三份都未通过 U10，见 tests/assets/earlier_calibration/mac-probe-*.result.json`
  - `只做草稿两处改动的 tests/calibration/guessed.patch 同样触发`
