# 可接受变体

三个实现都与参考修复功能等价，写法不同，都通过全部 41 个单测。前两个在本目录，第三个是 `tests/calibration/equivalent.patch`。

| 实现 | 三次得分 | 三次通过单测 | 证据 |
|---|---|---|---|
| variant_a.patch | [1, 1, 1] | [41, 41, 41] | tests/assets/selfcheck/linux-amd64-1.1.2/variant_a-run*.json |
| variant_b.patch | [1, 1, 1] | [41, 41, 41] | tests/assets/selfcheck/linux-amd64-1.1.2/variant_b-run*.json |
| equivalent.patch | [1, 1, 1] | [41, 41, 41] | tests/assets/selfcheck/linux-amd64-1.1.2/equivalent-run*.json |

## variant_a：沿用上游修复的写法

- 舍入函数改名为 `round_half_up_two_dec`，新增 `round_half_up_four_dec`，`round_half_up` 作为带弃用提示的别名保留。等价：别名的返回值与原函数相同。
- 税额计算提取成 `FixedRateTax.calculate_tax`，两条报价路径共用。
- 行金额属性保持上游修复后的形态，合计在 `_get_total` 里逐行舍入后相加。
- 折后运费的不含税金额保留四位小数，由订单合计计算和落库时舍入到分；展示过滤器在没有自定义格式时预先四舍五入，所以页面显示与落库一致。
- 落库金额在 `OrderCreator` 里通过字段名表统一舍入。
- 价格明细：先为每一件算出按分的单价，使其合计等于订单行金额，再把相邻相同的单价合并成一条。等价：各条明细之和等于订单行金额，结算逻辑不变。

## variant_b：金额模块加模型层归一

- 新增 `oscar/core/money.py`，提供 `cents`、`unit`、`allocate` 和 `StoredAmountsMixin`。
- 税额计算用 `localcontext` 把舍入方式设为 `ROUND_HALF_UP` 后调用 `quantize(exponent)`。
- 购物车行的两个折后金额属性直接返回分。
- 落库金额不在 `OrderCreator` 里处理，而是在订单、订单行、价格明细、附加费四个模型的 `save()` 里归一到分，不改字段定义。
- 价格明细用 `allocate` 把订单行金额摊成至多两种相差一分的单价。
- 展示过滤器用 `localcontext` 让 Babel 以四舍五入量化。

## equivalent：按折扣组占比分配订单行金额

- 固定税率策略按四位小数取单件税额。折后行金额保留计算精度，购物车按行舍入后求和，含税与不含税合计之差是税额合计。
- 新订单保留各折扣组的顺序。按各组占行金额的比例计算累计份额，取整到分后用相邻份额之差作为每组金额，含税与不含税分别计算。
- 组内将整数分均摊到每件，余下的分加在最后几件上，以相同单价合并明细。每批发货按已存明细结算。对正价订单，每一批均为非负金额，各批合计与订单行一致。已有订单仍按原明细结算。
