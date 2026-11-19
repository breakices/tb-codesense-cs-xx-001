# 结构化单测清单

共 41 个单测，全部在 `tests/test_money_contract.py`。针对预设 badpattern 的有 14 个。

| 维度 | 数量 | 编号 |
|---|---|---|
| 语义正确性 | 7 | U1、U2、U3、U4、U5、U11、U19 |
| 改一查十完备性 | 17 | U6、U8、U9、U10、U12、U13、U14、U16、U17、U18、U21、U23、U24、U29、U39、U40、U41 |
| 单轮反幻觉 | 4 | U7、U15、U22、U27 |
| 回归安全 | 9 | U20、U25、U26、U28、U30、U31、U32、U33、U34 |
| 边界与异常 | 4 | U35、U36、U37、U38 |

| 编号 | 单测 | 维度 | 必要性 | 针对 badpattern | 改动点 | 判定内容 | 断言证据 |
|---|---|---|---|---|---|---|---|
| U1 | `test_bulk_small_items_keep_their_tax` | 语义正确性 | Explicit | 否 | CP1+CP4 | 题面症状 1：100 件单价 0.01、税率 20% 的购物车，不含税合计 1.00，税额合计 0.20，含税合计 1.20。 | 断言 Basket.total_excl_tax / total_tax / total_incl_tax 的实际值；失败时输出实际 Decimal。 |
| U2 | `test_unit_price_is_carried_at_four_places` | 语义正确性 | Explicit | 否 | CP1 | UK 策略下单价 0.99 的商品：单件税额按四位小数为 0.1980，含税单价为 1.1880。 | 直接比较 fetch_for_product 返回的税额与含税价和预期 Decimal 值。 |
| U3 | `test_tax_of_a_multi_unit_line_is_not_unit_tax_times_quantity` | 语义正确性 | Explicit | 否 | CP1+CP4 | 7 件单价 0.99：税额合计 1.39，含税合计 8.32，而不是单件税额舍入后乘数量得到的 1.40 与 8.33。 | 断言三个购物车合计的实际值。 |
| U4 | `test_basket_totals_are_cents_with_percentage_offer_on_gross_prices` | 语义正确性 | Explicit | 否 | CP4 | 题面症状 2：含税口径促销下 3 件 9.99 打 85 折，含税合计 30.57；不含税合计是分；含税减不含税等于税额合计。 | 断言 total_incl_tax 的值、total_excl_tax 已是分、三个合计的差值关系。 |
| U5 | `test_basket_totals_are_cents_with_percentage_offer_default_setting` | 语义正确性 | Explicit | 否 | CP4 | 默认设置下 3 件 £9.99 打 85 折，沿用英国策略的含税有效单价计算折扣，折扣从不含税行额扣除，税前合计 £24.58。 | 按原促销算法得到 £5.3946 的折扣。检查 £29.97 扣减折扣后的分位合计，并核对含税合计减税前合计等于总税额。 |
| U6 | `test_parent_product_price_is_carried_at_four_places` | 改一查十完备性 | Implicit | 否 | CP1+CP3 | 父商品的报价走策略里的另一条路径：子商品 0.99 时父商品税额 0.1980、含税价 1.1880。 | 直接比较 fetch_for_parent 返回的税额与含税价和预期 Decimal 值。 |
| U7 | `test_unit_tax_rounds_half_up_at_the_fourth_place` | 单轮反幻觉 | Explicit | 否 | CP2 | 税前 £0.03、税率 17.5% 的单件税额取四位为 £0.0053，含税单价 £0.0353。买 200 件时税额 £1.06，含税合计 £7.06。 | 直接比较策略返回的数值，再核对 200 件购物车。保留未经舍入的 £0.00525 会使含税合计成为 £7.05。 |
| U8 | `test_parent_unit_tax_rounds_half_up_at_the_fourth_place` | 改一查十完备性 | Explicit | 否 | CP3 | 同一进位点经父商品报价路径，直接返回的单件税额为 £0.0053，含税单价为 £0.0353。 | 直接比较父商品报价的 tax 和 incl_tax；对比输入为子商品税前 £0.03、税率 17.5%。 |
| U9 | `test_gross_amount_at_a_tie_is_half_up_in_the_basket_and_on_the_order` | 改一查十完备性 | Implicit | 否 | CP4+CP11 | 17.5% 税率、1 件 0.60：含税 0.7050 在分位是进位点。购物车合计、订单合计、订单行金额与含税单价都应为 0.71。 | 断言 Basket.total_incl_tax 以及下单后重读的 Order、Line 金额；交给数据库适配层量化会得到 0.70。 |
| U10 | `test_displayed_amount_is_rounded_half_up` | 改一查十完备性 | Implicit | 是 | CP13 | 模板里展示金额的过滤器：0.7050 显示为 0.71，2.125 显示为 2.13，10.625 显示为 10.63。 | 调用 oscar.templatetags.currency_filters.currency，与分值金额的渲染结果比较；不锁定格式字符串。 |
| U11 | `test_order_without_offers_stores_cents` | 语义正确性 | Explicit | 否 | CP1+CP11 | 3 件 0.99 无促销下单：订单不含税 2.97、含税 3.56；订单行含税单价 1.19，行含税金额折前折后均为 3.56。 | 下单后从数据库重读，断言 Order 与 Line 上的金额。 |
| U12 | `test_order_with_percentage_surcharge_adds_up_in_cents` | 改一查十完备性 | Implicit | 否 | CP11 | 1 件 10.00、免运费、1.875% 附加费下单：附加费含税 0.23、不含税 0.19；订单合计等于购物车合计加落库的附加费。 | 下单后从数据库重读，断言 Surcharge 金额以及 Order 合计与分项的求和关系；交给数据库适配层量化会得到 0.22。 |
| U13 | `test_discounted_shipping_net_charge_rounds_half_up` | 改一查十完备性 | Explicit | 否 | CP9 | 运费不含税 5.00、含税 6.00，优惠后含税 3.75：计算不含税运费的方法得到 3.125，四舍五入为 3.13，quantize 的默认方式得到 3.12。 | 断言 TaxInclusiveOfferDiscount.calculate(...) 的 incl_tax 与 excl_tax（按分比较）。 |
| U14 | `test_percentage_shipping_discount_rounds_half_up` | 改一查十完备性 | Explicit | 是 | CP10 | 运费 2.50 打 75 折：计算折扣的方法得到 0.625，四舍五入为 0.63，quantize 的默认方式得到 0.62。 | 断言 TaxExclusiveOfferDiscount.discount(...)（按分比较）。 |
| U15 | `test_lines_shown_in_the_basket_add_up_to_the_total_shown` | 单轮反幻觉 | Implicit | 是 | CP4+CP13 | 两种单价 0.03 的商品各一件：购物车页面上各行显示的金额之和，等于页面显示的折前合计与合计。 | 对每行金额和两个合计分别取展示过滤器的渲染值再比较；失败时输出两侧数值，例如 0.07 对 0.08，即草稿“在合计处统一舍入”的后果。 |
| U16 | `test_lines_shown_add_up_to_the_total_shown_when_they_tie` | 改一查十完备性 | Implicit | 是 | CP4+CP13 | 17.5% 税率、两种单价 0.60 的商品各一件：每行 0.7050，页面上各行显示的金额之和等于显示的合计。 | 对每行金额和合计分别取展示过滤器的渲染值再比较。 |
| U17 | `test_order_lines_add_up_to_the_order_total` | 改一查十完备性 | Implicit | 是 | CP4+CP11 | U15 的购物车下单、免运费：订单行金额之和等于订单合计，含税不含税都成立；每条订单行等于购物车页面为该行显示的金额。 | 下单后从数据库重读，断言各 Line 金额、Order 合计及其求和关系。 |
| U18 | `test_order_lines_add_up_to_the_order_total_when_they_tie` | 改一查十完备性 | Implicit | 是 | CP4+CP11 | U16 的购物车下单、免运费：订单行金额之和等于订单合计。 | 下单后从数据库重读，断言求和关系。 |
| U19 | `test_discounted_order_lines_add_up_to_the_order_total` | 语义正确性 | Implicit | 否 | CP4+CP11 | 不含税策略、两种单价 1.00 的商品各一件、15.5% 促销下单：订单行金额之和等于订单合计。 | 下单后从数据库重读，断言求和关系；不断言具体数值。 |
| U20 | `test_single_line_order_agrees_with_its_totals` | 回归安全 | Implicit | 否 | CP11 | 含税口径下 5 件 4.00 每件减 2.25、免运费下单：订单含税 12.75；唯一订单行的金额等于订单合计；订单报告的折扣等于折前减折后。 | 下单后从数据库重读，断言 Order 与 Line 金额之间的相等关系。 |
| U21 | `test_price_row_of_single_unit_agrees_with_its_order_line` | 改一查十完备性 | Implicit | 是 | CP15 | 含税口径下 1 件 4.00 减 2.25 下单：订单行只有一条价格明细，明细与订单行的含税、不含税金额分别相同。 | 下单后从数据库重读，断言 LinePrice 与 Line 金额相等。 |
| U22 | `test_batches_settle_to_the_order_line_amount` | 单轮反幻觉 | Implicit | 是 | CP15 | 检验两种非均匀分批：100 件 £0.01 分 30、70 件，30 件 £0.03 分 29、1 件。逐笔结算与存储的订单行及明细对账。 | 按数量核对存储明细的件数、含税与不含税总额；逐批检查非负分位金额、累计不超应收，末批后累计额等于订单行含税金额。 |
| U23 | `test_unit_by_unit_settlement_adds_up_to_the_order_line_amount` | 改一查十完备性 | Implicit | 是 | CP15 | 7 件 £0.99 按件结算。七笔金额均为非负分位数，累计收款不超过订单行，最终结清。 | 按数量核对存储明细的件数、含税与不含税总额；逐批检查非负分位金额、累计不超应收，末批后累计额等于订单行含税金额。 |
| U24 | `test_settlement_of_a_partly_discounted_line_adds_up` | 改一查十完备性 | Implicit | 是 | CP15 | 5 件 £3.33，其中至多三件享九折，分 2、3 件结算。订单行、折扣分组的价格明细与分批收款对账。 | 按数量核对存储明细的件数、含税与不含税总额；逐批检查非负分位金额、累计不超应收，末批后累计额等于订单行含税金额。 |
| U25 | `test_order_placed_before_the_change_settles_its_remaining_units` | 回归安全 | Implicit | 否 | 在途 | 数据库里已有的订单：5 件、行金额 18.80、价格明细 3 件 3.60 加 2 件 4.00，其中前 3 件已按 10.80 结算。结算剩余 2 件应为 8.00。 | 直接用 ORM 建立订单与已发生的结算事件，再取剩余批次的结算金额，断言其值及与行金额的关系。 |
| U26 | `test_order_placed_before_the_change_settles_in_full` | 回归安全 | Implicit | 否 | 在途 | 数据库里已有、尚未发货的订单：7 件、单价明细 1.19、行金额 8.33。分两批结算，合计 8.33。 | 直接用 ORM 建立订单，分批取结算金额，断言合计。 |
| U27 | `test_no_price_change_warning_when_the_price_did_not_change` | 单轮反幻觉 | Implicit | 是 | CP8 | 读取历史购物车行时，若记录价和当前向顾客显示的价格均为 £1.19，购物车不提示价格变化。 | 直接建立旧两位记录价的购物车行，从数据库读回并检查 get_warning() 和原始记录价。 |
| U28 | `test_price_change_warning_is_still_reported_for_a_real_change` | 回归安全 | Implicit | 否 | CP8 | 旧购物车的当前显示价高于历史记录价时给出提示。覆盖库存实际调价，以及存货未调价但旧 £0.70 变为可见 £0.71 的进位点。 | 读回持久化旧行，比较两种涨价路径的价格提示；检查旧记录保持原值。 |
| U29 | `test_discounted_shipping_charge_is_stored_as_shown` | 改一查十完备性 | Implicit | 否 | CP9+CP11 | 1 件 10.00，运费不含税 5.00、含税 6.00，优惠后含税 3.75、不含税 3.125：结算页显示的运费等于订单落库的运费，订单合计等于订单行加运费。 | 对运费取展示过滤器的渲染值，与下单后重读的 Order 运费比较，并断言合计的求和关系。 |
| U30 | `test_untaxed_strategy_totals_unchanged` | 回归安全 | Implicit | 否 | 回归 | 不含税策略下 3 件 9.99：不含税与含税合计都是 29.97，税额 0.00，订单落库相同。 | 断言购物车三个合计与订单两个合计。 |
| U31 | `test_absolute_offer_without_tax_unchanged` | 回归安全 | Implicit | 否 | 回归 | 不含税策略下 2 件 5.00 立减 3.00：两个合计都是 7.00。 | 断言购物车两个合计。 |
| U32 | `test_existing_two_place_helper_keeps_its_behaviour` | 回归安全 | Explicit | 否 | 回归 | 已有的公开函数 oscar.core.utils.round_half_up 仍然四舍五入到两位：1.005 得 1.01，2.125 得 2.13。 | 调用该函数，断言返回值与小数位数。 |
| U33 | `test_discounted_shipping_without_tie_unchanged_in_cents` | 回归安全 | Implicit | 否 | CP9 | 运费不含税 4.99、含税 5.99 减 1.00：含税 4.99，不含税按分为 4.16，与整改前一致。 | 断言 TaxInclusiveOfferDiscount.calculate(...) 的两项金额（按分比较）。 |
| U34 | `test_displayed_amount_format_unchanged_for_ordinary_values` | 回归安全 | Implicit | 否 | CP13 | 不需要舍入的金额展示格式不变：10.00 显示 £10.00，1234.5 显示 £1,234.50，0 显示 £0.00；非数字输入仍渲染为空串。 | 调用 currency 过滤器，断言渲染结果。 |
| U35 | `test_net_total_is_cents_when_tax_is_not_known` | 边界与异常 | Explicit | 否 | CP4 | 税额后置的策略下 3 件 9.99 打九折：税额未知，不含税合计仍是分，为 26.97 或 26.98。 | 断言 Basket.is_tax_known 为 False、total_excl_tax 已是分且落在给定区间。 |
| U36 | `test_fully_discounted_basket_is_zero_not_negative` | 边界与异常 | Implicit | 否 | 回归 | 含税口径下 2 件 0.99 全额折扣：三个合计都是 0.00。 | 断言购物车三个合计。 |
| U37 | `test_empty_basket_totals_are_zero` | 边界与异常 | Implicit | 否 | CP4 | 空购物车的含税与不含税合计都是 0。 | 断言购物车两个合计。 |
| U38 | `test_free_shipping_after_discount_has_no_net_charge` | 边界与异常 | Implicit | 否 | CP9 | 运费优惠到含税 0.00 时，不含税也是 0.00。 | 断言 TaxInclusiveOfferDiscount.calculate(...) 的两项金额。 |
| U39 | `test_indexed_price_is_the_price_shown` | 改一查十完备性 | Explicit | 是 | CP16 | 搜索索引里的商品价格等于商品页显示的价格：0.99 按 20% 是 1.19，0.60 按 17.5% 是 0.71；父商品相同。价格筛选、价格区间和按价格排序都以索引里的数为准。 | 调用 ProductIndex.prepare_price，与同一价格经展示过滤器渲染的值比较；整改前两者一致，只改精度以后索引里是 1.188。 |
| U40 | `test_no_price_change_warning_at_a_tie` | 改一查十完备性 | Implicit | 是 | CP8 | 新建购物车在分位进位点按当前口径保存记录价，同价重新读取时不发出价格变动提示。 | 对六个单价分别断言 Line.get_warning() 为 None；记录价交给数据库适配层量化时，0.7050 存成 0.70，与四舍五入后的现价 0.71 不等。 |
| U41 | `test_batches_settle_to_the_order_line_amount_at_a_tie` | 改一查十完备性 | Implicit | 是 | CP15 | 3 件 £0.60 按 17.5% 计税，按 1、2 件分两批；含税单价在分位进位点时，分批收款和存储明细仍满足订单行约束。 | 按数量核对存储明细的件数、含税与不含税总额；逐批检查非负分位金额、累计不超应收，末批后累计额等于订单行含税金额。 |
