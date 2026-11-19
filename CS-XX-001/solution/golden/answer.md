# 参考答案：CS-XX-001 含税金额精度整改

参考修复是 `solution/golden/golden.patch`，对快照的 10 个文件做了修改。下面先给结论，再逐处说明，最后是运行证据。

## 1. 结论

同事的草稿只覆盖了题面两个症状所在的位置，而且草稿里的三个说法都不成立：

1. `quantize` 不传 `rounding` 时用的是 decimal 上下文的默认方式 `ROUND_HALF_EVEN`，不是四舍五入。
2. 在 `Basket._get_total` 返回前统一舍入，是先加总再舍入。页面上每一行各自显示。Golden 将显示的分位行额加总，确保顾客可以逐行核对。两行各 0.036 时前者得到 0.07，后者 0.08。
3. 下游不会自然变对。运费折扣、订单落库、页面展示各有自己的舍入；订单的价格明细按分保存单价，分批结算靠它逐件累加；购物车行的价格变动提示直接比较现价和记录价；搜索索引直接取四位小数的单价，而商品页显示的是取到分的价格。单价精度一变，这几处都会出错。

题面还要求原来对得上的金额要仍然对得上，上线前已在系统里的购物车和订单要能走完流程。已有购物车保存历史两位记录价，顾客看到的分位价格发生变化时才发出提示，包括旧记录 £0.70、现价 £0.7050 显示为 £0.71 的情况，已有订单的总额、订单行、价格明细和已结算金额保持不变。
只做草稿两处的改法会让症状消失，同时破坏这些义务：页面各行与合计差一分，分批结算的金额加不回订单行，价格没变的商品被提示价格变动，搜索索引里的价格与页面上的价格不再相同。

参考补丁在 16 处改动中列出 11 个需要验收的行为点。其余 5 处（CP5、CP6、CP7、CP12、CP14）记录 Golden 的实现选择；在 1.1.2 的 22 组[撤除实验](../../tests/assets/selfcheck/ablation-1.1.2.json)中，11 个必需点各自撤回均有用例失败。5 个实现细节可逐个或同时撤回；单独移除 CP14 辅助函数时将所需舍入运算内联，仍通过 41 项。

## 2. 逐处说明

行号是应用 `golden.patch` 之后的行号。

### CP1  `FixedRateTax.exponent`

- 位置：`src/oscar/apps/partner/strategy.py`，第 282 行
- 改动：单件税额的保留位数由两位改为四位。
- 原因：按两位保留时 0.01 x 20% = 0.002 被舍成 0.00，税额在单件层面就丢失了；含税单价也因此带着舍入误差被数量放大。
- 对应单测：U1、U2、U3、U6、U11

### CP2  `FixedRateTax.pricing_policy`

- 位置：`src/oscar/apps/partner/strategy.py`，第 289 行
- 改动：quantize 显式使用 ROUND_HALF_UP。
- 原因：quantize 不传 rounding 时用的是当前 decimal 上下文的舍入方式，默认 ROUND_HALF_EVEN。£0.03 × 17.5% 的原始税额 £0.00525 必须在策略返回前取为 £0.0053。200 件的总税额是 £1.06，含税总价 £7.06。
- 对应单测：U7

### CP3  `FixedRateTax.parent_pricing_policy`

- 位置：`src/oscar/apps/partner/strategy.py`，第 303 行
- 改动：父商品报价路径上的同一处 quantize 同样显式使用 ROUND_HALF_UP。
- 原因：父商品的价格由另一段几乎相同的代码计算，只改 pricing_policy 会留下这一处。
- 对应单测：U6、U8

### CP4  `AbstractBasket._get_total`

- 位置：`src/oscar/apps/basket/abstract_models.py`，第 444 到 465 行
- 改动：合计改为各行金额先各自四舍五入到分再相加。
- 原因：分项加起来必须等于合计。先把未舍入的行金额加总再舍入一次，两行各 0.036 会得到 0.07，而页面上两行各显示 0.04。整改前单价是两位小数，这个等式天然成立，精度一改就破了。
- 对应单测：U1、U3、U4、U5、U9、U15、U16、U17、U18、U19、U35、U37

英国策略的优惠按含税有效单价计算折扣。默认配置将折扣从不含税行额扣减，3 件 £9.99 的 15% 折扣为 £5.3946，税前行额 £29.97 扣减后取到分为 £24.58（U5）。

### CP5  `AbstractLine.line_price_excl_tax_incl_discounts`

- 位置：`src/oscar/apps/basket/abstract_models.py`，第 968 到 1013 行
- 改动：折后不含税行金额对最终结果舍入一次，不再先把折算出的不含税折扣舍入到分。
- 原因：20.00 - 9.375 = 10.625 应为 10.63。先把 9.375 舍成 9.38 再相减得到 10.62，订单行、税额都跟着差一分。
- 说明：参考实现的写法。行金额在 CP4 里逐行取到分以后，这里再舍入一次不改变任何断言的结果；单独撤掉不影响得分。

### CP6  `AbstractLine.line_price_incl_tax_incl_discounts`

- 位置：`src/oscar/apps/basket/abstract_models.py`，第 1014 到 1032 行
- 改动：折后含税行金额在有折扣的两个分支都舍入到分。
- 原因：含税单价变成四位小数后，行金额减折扣的结果不再天然是两位小数。
- 说明：参考实现的写法，理由同 CP5。

### CP7  `AbstractLine.get_price_breakdown`

- 位置：`src/oscar/apps/basket/abstract_models.py`，第 833 行
- 改动：分摊到单件的不含税折扣按四位小数保留。
- 原因：这是单件层面的中间量。按两位舍入会让拆分出来的单价与行金额对不上，1 件时行是 2.13 而拆分是 2.12。
- 说明：参考实现的写法。价格明细由 CP15 按订单行金额重新分摊，这里的精度不再决定结果；单独撤掉不影响得分。

### CP8  `AbstractBasket.add_product / AbstractLine.get_warning`

- 位置：`src/oscar/apps/basket/abstract_models.py`，第 296、1081 行
- 改动：加入购物车时记录的含税价按分保存；价格变动提示在分的精度上比较现价和记录价。
- 原因：记录价存在两位小数的字段里，现价是四位小数。直接比较时 1.19 != 1.1880，价格没变也会提示“从 £1.19 降到 £1.19”。这是精度改动带来的回归，仓库自带测试不覆盖。
- 对应单测：U27、U28、U40

### CP9  `TaxInclusiveOfferDiscount.calculate_excl_tax`

- 位置：`src/oscar/apps/shipping/methods.py`，第 203 行
- 改动：折后运费的不含税金额改为四舍五入。
- 原因：原来的 quantize(D("0.01")) 是银行家舍入，5.00 x 3.75 / 6.00 = 3.125 得到 3.12。
- 对应单测：U13、U29、U33、U38

### CP10  `ShippingPercentageDiscountBenefit.shipping_discount`

- 位置：`src/oscar/apps/offer/benefits.py`，第 431 行
- 改动：运费百分比折扣改为四舍五入。
- 原因：同样是不带 rounding 的 quantize，2.50 x 25% = 0.625 得到 0.62。
- 对应单测：U14

### CP11  `to_cents / OrderCreator.create_order_model / create_line_models / create_discount_model`

- 位置：`src/oscar/apps/order/utils.py`，第 53、54、71、211、212、213、214、239、240、274、277、280、283、287、288、379 行
- 改动：写入订单、订单行、附加费、折扣记录的金额，在写入前显式四舍五入到分。
- 原因：四位小数的金额写进两位小数的 DecimalField 时，Django 会用 decimal 上下文的默认方式量化，也是银行家舍入：0.7050 落库成 0.70，而购物车合计是 0.71。
- 对应单测：U9、U11、U12、U17、U18、U19、U20、U29

### CP12  `PercentageCharge.calculate / OrderTotalCalculator.calculate`

- 位置：`src/oscar/apps/checkout/surcharges.py, src/oscar/apps/checkout/calculators.py`，第 44、45、22、24、32、34 行
- 改动：百分比附加费舍入到分；订单合计由已舍入到分的购物车合计、运费、各项附加费相加得到。
- 原因：附加费是订单上单独的一项金额。订单合计必须等于订单行、运费、附加费之和，不能把未舍入的分项加总后再舍入。
- 说明：与 CP11 里附加费落库的一段互为冗余：两处任留一处，U12 都通过；两处都撤掉，U12 失败。

### CP13  `currency`

- 位置：`src/oscar/templatetags/currency_filters.py`，第 41 行
- 改动：金额在交给 Babel 格式化之前，先按币种的小数位四舍五入。
- 原因：Babel 用 decimal 上下文的默认方式把金额量化到币种精度，0.7050 显示成 £0.70，而合计是 £0.71。四位小数的金额现在会直接到达模板。
- 对应单测：U10、U15、U16、U34

### CP14  `round_half_up_four_dec（新增），round_half_up（保持）`

- 位置：`src/oscar/core/utils.py`，第 183、168 行
- 改动：新增四位小数的四舍五入函数；已有的 round_half_up 保持原名和原行为。
- 原因：round_half_up 是公开函数，基于这个代码库的项目在使用，不能改名或改语义。
- 说明：辅助函数。等价实现没有它也通过；保留原有的 round_half_up 不变才是必需的，由 U32 把守。

### CP15  `share_in_cents / unit_price_rows / OrderCreator.create_line_price_models`

- 位置：`src/oscar/apps/order/utils.py`，第 28、38、347 行
- 改动：订单行的价格明细不再逐条把单价舍入到分，而是把订单行金额按分摊到每一件上：同组的件拿相同的单价，除不尽的几分钱加在前几件上，各条明细的金额之和恰好等于订单行金额。
- 原因：分批发货的结算金额由 EventHandler.calculate_payment_event_subtotal 按价格明细逐件累加。单价 0.012 落成 0.01 后，100 件结算出 1.00，而订单行是 1.20。结算逻辑本身不动，上线前已有订单的明细和已结算的批次因此不受影响。
- 对应单测：U21、U22、U23、U24、U41

### CP16  `ProductIndex.prepare_price`

- 位置：`src/oscar/apps/search/search_indexes.py`，第 72 行
- 改动：写进搜索索引的商品价格按四舍五入取到分，与商品页显示的价格相同。
- 原因：索引里的价格是价格筛选、价格区间和按价格排序用的数。整改前它就是页面上的价格；单价保留四位以后，索引里是 1.1880，页面显示 1.19，同一个价格在两处成了两个数。这一处与购物车、订单都没有调用关系，仓库自带的测试也不覆盖。
- 对应单测：U39

## 3. 运行证据

### 3.1 参考修复在任务镜像里的判分

1.1.2 每轮从独立的 `linux/amd64` 容器开始，使用 `tests/test.sh` 判分。求解阶段只提供题面和起始仓库，评分阶段单独挂载验证器。起始仓库的 Git 树是上游的 `bdea6eaad6894e6167d11d03ae43019d10127467`。环境标识、三轮逐条结果与奖励见 [当前预检](../../tests/assets/selfcheck/linux-amd64-1.1.2/SUMMARY.json)。旧版日志单独保存在 `tests/assets/selfcheck/linux-amd64/`。

### 3.2 七项反例

以下为较早镜像的观测原文；1.1.2 的运行输出分别见 [参考解](../../tests/assets/selfcheck/linux-amd64-1.1.2/ce2-golden-run1.log) 和 [草稿](../../tests/assets/selfcheck/linux-amd64-1.1.2/ce2-guessed-run1.log)。

```
python 3.12.14 | django 5.1.15 | Linux-5.15.152-amd64-x86_64-with-glibc2.36
repository: /workspace/repo
[ok] warning on an unchanged price: None
[ok] order line / settled in two batches: 1.20 / 0.50 + 0.70 = 1.20
[ok] lines shown / total shown: 0.04 + 0.04 / 0.08
[ok] order lines / order total: 0.04 + 0.04 / 0.08
[ok] unit tax of 0.03 at 17.5%: 0.0053
[ok] 0.7050 in the basket / on the order / on the page: 0.71 / 0.71 / 0.71
[ok] price of a 0.99 product in the search index / on its page: 1.19 / 1.19
defects observed: 0 of 7
exit status: 1
```

同一个程序在只做草稿两处改动的仓库上的输出：

```
python 3.12.14 | django 5.1.15 | Linux-5.15.152-amd64-x86_64-with-glibc2.36
repository: /workspace/repo
[DEFECT] warning on an unchanged price: "The price of 'Item 1' has decreased from £1.19 to £1.19 since you added it to your basket"
[DEFECT] order line / settled in two batches: 1.20 / 0.30 + 0.70 = 1.00
[DEFECT] lines shown / total shown: 0.04 + 0.04 / 0.07
[DEFECT] order lines / order total: 0.04 + 0.04 / 0.07
[DEFECT] unit tax of 0.03 at 17.5%: 0.0052
[DEFECT] 0.7050 in the basket / on the order / on the page: 0.71 / 0.70 / 0.70
[DEFECT] price of a 0.99 product in the search index / on its page: 1.1880 / 1.19
defects observed: 7 of 7
exit status: 0
```

## 4. 不在考察范围内的行为

1. 商品促销的折扣算法保持原样，题面已说明。促销折扣在各行上用精确值还是用取整后的值，两种做法都不判错。
2. 进位点上先保不含税金额还是先保税额，不判。断言只要求含税减不含税等于税额。
3. 多行时合计与各行如何取得一致由实现决定，逐行舍入或把差额分摊到行上都可以。断言只要求页面显示的各行之和等于显示的合计，订单行之和等于订单合计。
4. 分批结算时每一批具体是多少不判，要求每批为非负分位金额，累计金额不超订单行应收且最终结清。上线前已下单的按历史明细结清。
5. 多件商品的价格明细如何拆成若干条不判。无论拆成几组，明细件数和按件数累加的含税、不含税金额都要与订单行一致。
6. 折扣记录的金额与各行折扣之和的一分钱差异，不判，题面已说明。
7. 策略返回的单件税额、含税单价须直接满足规定精度。其他辅助计算可自由选择数值表示。
8. 自定义金额格式、零小数位币种的展示，不判。
9. 是否新增辅助函数、如何命名、是否新增迁移，不判。仓库自带测试是否通过不计分。
