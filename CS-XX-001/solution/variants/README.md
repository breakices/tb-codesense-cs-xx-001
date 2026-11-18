# 可接受变体

三个实现都与参考修复功能等价，写法不同，都通过全部 41 个单测。前两个在本目录，第三个是 `tests/calibration/equivalent.patch`。

| 实现 | 三次得分 | 三次通过单测 | 证据 |
|---|---|---|---|
| variant_a.patch | [1, 1, 1] | [41, 41, 41] | tests/assets/selfcheck/linux-amd64/variant_a-run*.json |
| variant_b.patch | [1, 1, 1] | [41, 41, 41] | tests/assets/selfcheck/linux-amd64/variant_b-run*.json |
| equivalent.patch | [1, 1, 1] | [41, 41, 41] | tests/assets/selfcheck/linux-amd64/equivalent-run*.json |

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

## equivalent：内部全部用精确值，结算时补差

- 不新增任何舍入函数，舍入都写成内联的 quantize，显式传 ROUND_HALF_UP。
- 行金额属性返回未舍入的精确值，合计逐行舍入后相加，税额合计定义为含税合计减不含税合计。
- 价格明细不拆分，仍按单价逐条舍入。改的是 `EventHandler.calculate_payment_event_subtotal`：结清一个订单行的那一批，取订单行金额减去此前各批按明细算出的金额。
- 等价的依据：每批金额仍是分；各批之和恒等于订单行金额；上线前已有的订单，明细本来就加得回行金额，补差为零，结算结果与原来相同。
