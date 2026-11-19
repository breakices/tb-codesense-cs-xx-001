# 蒙对样例 `guessed.patch`

该补丁只把固定税率策略的指数改为四位，并对购物车合计做两位舍入。两项报障症状得以修复，默认舍入、明细对账和其他使用价格的业务路径仍触发断言。

1.1.2 的三次 Linux 验证均得到 0 分，符合预期 0 分。每次通过 21/41 项，每个单测的结果在三次运行中一致。测试数量只用于诊断。

同一任务镜像上每次新建断网容器，以 `sh /tests/test.sh` 评分。[第 1 次](../assets/selfcheck/linux-amd64-1.1.2/guessed-run1.json) · [第 2 次](../assets/selfcheck/linux-amd64-1.1.2/guessed-run2.json) · [第 3 次](../assets/selfcheck/linux-amd64-1.1.2/guessed-run3.json) · [运行环境](../assets/selfcheck/linux-amd64-1.1.2/ENVIRONMENT.txt)

## 缺陷与失败单测

| 缺陷 | 实际失败的单测 |
|---|---|
| 默认舍入与展示/持久化 | U7、U8、U9、U10、U12、U13、U14 |
| 购物车与订单行逐项对账 | U15、U16、U17、U18、U19 |
| 分批结算与价格明细 | U22、U23、U24、U41 |
| 购物车提示与搜索价格 | U27、U28、U39、U40 |

## 逐条结果

完整断言输出见上方三份 JSON 的 `results`。

| 编号 | 单测 | 维度 | 结果 | 第一次运行的失败断言摘录 |
|---|---|---|---|---|
| U1 | `test_bulk_small_items_keep_their_tax` | 语义正确性 | 通过 | — |
| U2 | `test_unit_price_is_carried_at_four_places` | 语义正确性 | 通过 | — |
| U3 | `test_tax_of_a_multi_unit_line_is_not_unit_tax_times_quantity` | 语义正确性 | 通过 | — |
| U4 | `test_basket_totals_are_cents_with_percentage_offer_on_gross_prices` | 语义正确性 | 通过 | — |
| U5 | `test_basket_totals_are_cents_with_percentage_offer_default_setting` | 语义正确性 | 通过 | — |
| U6 | `test_parent_product_price_is_carried_at_four_places` | 改一查十完备性 | 通过 | — |
| U7 | `test_unit_tax_rounds_half_up_at_the_fourth_place` | 单轮反幻觉 | 失败 | `assert Decimal('0.0052') == Decimal('0.0053')` |
| U8 | `test_parent_unit_tax_rounds_half_up_at_the_fourth_place` | 改一查十完备性 | 失败 | `assert Decimal('0.0052') == Decimal('0.0053')` |
| U9 | `test_gross_amount_at_a_tie_is_half_up_in_the_basket_and_on_the_order` | 改一查十完备性 | 失败 | `assert Decimal('0.70') == Decimal('0.71')` |
| U10 | `test_displayed_amount_is_rounded_half_up` | 改一查十完备性 | 失败 | `assert '£0.70' == '£0.71'` |
| U11 | `test_order_without_offers_stores_cents` | 语义正确性 | 通过 | — |
| U12 | `test_order_with_percentage_surcharge_adds_up_in_cents` | 改一查十完备性 | 失败 | `assert Decimal('0.22') == Decimal('0.23')` |
| U13 | `test_discounted_shipping_net_charge_rounds_half_up` | 改一查十完备性 | 失败 | `assert Decimal('3.12') == Decimal('3.13')` |
| U14 | `test_percentage_shipping_discount_rounds_half_up` | 改一查十完备性 | 失败 | `assert Decimal('0.62') == Decimal('0.63')` |
| U15 | `test_lines_shown_in_the_basket_add_up_to_the_total_shown` | 单轮反幻觉 | 失败 | `assert Decimal('0.07') == Decimal('0.08')` |
| U16 | `test_lines_shown_add_up_to_the_total_shown_when_they_tie` | 改一查十完备性 | 失败 | `assert Decimal('1.41') == Decimal('1.40')` |
| U17 | `test_order_lines_add_up_to_the_order_total` | 改一查十完备性 | 失败 | `assert Decimal('0.07') == Decimal('0.08')` |
| U18 | `test_order_lines_add_up_to_the_order_total_when_they_tie` | 改一查十完备性 | 失败 | `assert Decimal('1.41') == Decimal('1.40')` |
| U19 | `test_discounted_order_lines_add_up_to_the_order_total` | 语义正确性 | 失败 | `assert Decimal('1.69') == Decimal('1.68')` |
| U20 | `test_single_line_order_agrees_with_its_totals` | 回归安全 | 通过 | — |
| U21 | `test_price_row_of_single_unit_agrees_with_its_order_line` | 改一查十完备性 | 通过 | — |
| U22 | `test_batches_settle_to_the_order_line_amount` | 单轮反幻觉 | 失败 | `assert Decimal('1.00') == Decimal('1.20')` |
| U23 | `test_unit_by_unit_settlement_adds_up_to_the_order_line_amount` | 改一查十完备性 | 失败 | `assert Decimal('8.33') <= Decimal('8.32')` |
| U24 | `test_settlement_of_a_partly_discounted_line_adds_up` | 改一查十完备性 | 失败 | `assert Decimal('18.80') <= Decimal('18.78')` |
| U25 | `test_order_placed_before_the_change_settles_its_remaining_units` | 回归安全 | 通过 | — |
| U26 | `test_order_placed_before_the_change_settles_in_full` | 回归安全 | 通过 | — |
| U27 | `test_no_price_change_warning_when_the_price_did_not_change` | 单轮反幻觉 | 失败 | `assert "The price of 'Item 69' has decreased from £1.19 to £1.19 since you added it to your basket" is None` |
| U28 | `test_price_change_warning_is_still_reported_for_a_real_change` | 回归安全 | 失败 | `assert Decimal('0.70') == Decimal('0.71')` |
| U29 | `test_discounted_shipping_charge_is_stored_as_shown` | 改一查十完备性 | 通过 | — |
| U30 | `test_untaxed_strategy_totals_unchanged` | 回归安全 | 通过 | — |
| U31 | `test_absolute_offer_without_tax_unchanged` | 回归安全 | 通过 | — |
| U32 | `test_existing_two_place_helper_keeps_its_behaviour` | 回归安全 | 通过 | — |
| U33 | `test_discounted_shipping_without_tie_unchanged_in_cents` | 回归安全 | 通过 | — |
| U34 | `test_displayed_amount_format_unchanged_for_ordinary_values` | 回归安全 | 通过 | — |
| U35 | `test_net_total_is_cents_when_tax_is_not_known` | 边界与异常 | 通过 | — |
| U36 | `test_fully_discounted_basket_is_zero_not_negative` | 边界与异常 | 通过 | — |
| U37 | `test_empty_basket_totals_are_zero` | 边界与异常 | 通过 | — |
| U38 | `test_free_shipping_after_discount_has_no_net_charge` | 边界与异常 | 通过 | — |
| U39 | `test_indexed_price_is_the_price_shown` | 改一查十完备性 | 失败 | `assert Decimal('1.1880') == Decimal('1.19')` |
| U40 | `test_no_price_change_warning_at_a_tie` | 改一查十完备性 | 失败 | `assert "The price of 'Item 97' has increased from £0.70 to £0.70 since you added it to your basket" is None` |
| U41 | `test_batches_settle_to_the_order_line_amount_at_a_tie` | 改一查十完备性 | 失败 | `assert Decimal('2.10') == Decimal('2.12')` |
