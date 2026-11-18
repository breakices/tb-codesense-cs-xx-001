# 缺陷样例：defective.patch

在参考修复上埋入三处缺陷。

## 判定

- 整题得分：0（预期 0）
- 通过单测：31 / 41（仅作诊断）
- 连跑三次逐条结果一致：是
- 运行方式：从任务镜像新起容器，把补丁应用到 /workspace/repo，以 root 执行 /tests/test.sh
- 证据：tests/assets/selfcheck/linux-amd64/defective-run{1,2,3}.json 与同名 .log

## 每处问题对应的失败单测

### 缺陷 1：价格变动提示的比较保持快照原样，直接比较四位小数的现价和两位小数的记录价。

- U27 `test_no_price_change_warning_when_the_price_did_not_change`：商品价格没有变化时，从数据库读出的购物车行不得提示价格变动。
  - 实际输出：`assert "The price of 'Item 69' has decreased from £1.19 to £1.19 since you added it to your basket" is None | +  where "The price of 'Item 69' has decreased from £1.19 to £1.19 since you added it to your basket" = get_warning() | +    where get_warning = <Line: Basket #1, Product #1, quantity 1>.get`
- U40 `test_no_price_change_warning_at_a_tie`：含税单价在分位是进位点或多于两位小数时，价格没有变化的购物车行同样不得提示价格变动。
  - 实际输出：`AssertionError: 0.60 | assert "The price of 'Item 108' has decreased from £0.71 to £0.71 since you added it to your basket" is None | +  where "The price of 'Item 108' has decreased from £0.71 to £0.71 since you added it to your basket" = get_warning() | +    where get_warning = <Line: Basket #1, Pr`

### 缺陷 2：价格明细逐条把单价舍入到分，不保证各条之和等于订单行金额。

- U22 `test_batches_settle_to_the_order_line_amount`：100 件 0.01 下单后按 30 件、70 件两批发货结算：两笔结算金额都是分，合计等于订单行金额。
  - 实际输出：`AssertionError: assert Decimal('1.00') == Decimal('1.20') | +  where Decimal('1.00') = sum([Decimal('0.30'), Decimal('0.70')]) | +  and   Decimal('1.20') = <Line: Product 'Item 60', quantity '100'>.line_price_incl_tax @ test_money_contract.py:331: in test_batches_settle_to_the_order_line_amount`
- U23 `test_unit_by_unit_settlement_adds_up_to_the_order_line_amount`：7 件 0.99 下单后逐件结算：七笔金额都是分，合计等于订单行金额。
  - 实际输出：`AssertionError: assert Decimal('8.33') == Decimal('8.32') | +  where Decimal('8.33') = sum([Decimal('1.19'), Decimal('1.19'), Decimal('1.19'), Decimal('1.19'), Decimal('1.19'), Decimal('1.19'), ...]) | +  and   Decimal('8.32') = <Line: Product 'Item 62', quantity '7'>.line_price_incl_tax @ test_mone`
- U24 `test_settlement_of_a_partly_discounted_line_adds_up`：含税口径下 5 件 3.33、最多 3 件享受九折，下单后按 2 件、3 件结算：结算金额之和等于订单行金额。
  - 实际输出：`AssertionError: assert Decimal('18.80') == Decimal('18.78') | +  where Decimal('18.80') = sum([Decimal('7.20'), Decimal('11.60')]) | +  and   Decimal('18.78') = <Line: Product 'Item 64', quantity '5'>.line_price_incl_tax @ test_money_contract.py:355: in test_settlement_of_a_partly_discounted_line_ad`
- U41 `test_batches_settle_to_the_order_line_amount_at_a_tie`：17.5% 税率、3 件 0.60 下单后按 1 件、2 件两批结算：两笔金额都是分，合计等于订单行金额。
  - 实际输出：`AssertionError: assert Decimal('2.13') == Decimal('2.12') | +  where Decimal('2.13') = sum([Decimal('0.71'), Decimal('1.42')]) | +  and   Decimal('2.12') = <Line: Product 'Item 110', quantity '3'>.line_price_incl_tax @ test_money_contract.py:568: in test_batches_settle_to_the_order_line_amount_at_a_`

### 缺陷 3：购物车合计改回先加总再舍入一次。

- U15 `test_lines_shown_in_the_basket_add_up_to_the_total_shown`：两种单价 0.03 的商品各一件：购物车页面上各行显示的金额之和，等于页面显示的折前合计与合计。
  - 实际输出：`AssertionError: assert Decimal('0.07') == Decimal('0.08') | +  where Decimal('0.07') = shown(Decimal('0.07')) | +    where Decimal('0.07') = <Basket: Open basket (owner: None, lines: 2)>.total_incl_tax_excl_discounts @ test_money_contract.py:236: in test_lines_shown_in_the_basket_add_up_to_the_total`
- U16 `test_lines_shown_add_up_to_the_total_shown_when_they_tie`：17.5% 税率、两种单价 0.60 的商品各一件：每行 0.7050，页面上各行显示的金额之和等于显示的合计。
  - 实际输出：`AssertionError: assert Decimal('1.41') == Decimal('1.42') | +  where Decimal('1.41') = shown(Decimal('1.41')) | +    where Decimal('1.41') = <Basket: Open basket (owner: None, lines: 2)>.total_incl_tax @ test_money_contract.py:246: in test_lines_shown_add_up_to_the_total_shown_when_they_tie`
- U17 `test_order_lines_add_up_to_the_order_total`：U15 的购物车下单、免运费：订单行金额之和等于订单合计，含税不含税都成立；每条订单行等于购物车页面为该行显示的金额。
  - 实际输出：`AssertionError: assert Decimal('0.07') == Decimal('0.08') | +  where Decimal('0.07') = <Order: #100001>.total_incl_tax | +  and   Decimal('0.08') = sum(<generator object test_order_lines_add_up_to_the_order_total.<locals>.<genexpr> at 0x7fd1ce03fa00>) @ test_money_contract.py:258: in test_order_line`
- U18 `test_order_lines_add_up_to_the_order_total_when_they_tie`：U16 的购物车下单、免运费：订单行金额之和等于订单合计。
  - 实际输出：`AssertionError: assert Decimal('1.41') == Decimal('1.42') | +  where Decimal('1.41') = <Order: #100001>.total_incl_tax | +  and   Decimal('1.42') = sum(<generator object test_order_lines_add_up_to_the_order_total_when_they_tie.<locals>.<genexpr> at 0x7fd1cde2ed40>) @ test_money_contract.py:268: in t`

## 逐条结果

| 编号 | 单测 | 维度 | 结果 |
|---|---|---|---|
| U1 | `test_bulk_small_items_keep_their_tax` | 语义正确性 | 通过 |
| U2 | `test_unit_price_is_carried_at_four_places` | 语义正确性 | 通过 |
| U3 | `test_tax_of_a_multi_unit_line_is_not_unit_tax_times_quantity` | 语义正确性 | 通过 |
| U4 | `test_basket_totals_are_cents_with_percentage_offer_on_gross_prices` | 语义正确性 | 通过 |
| U5 | `test_basket_totals_are_cents_with_percentage_offer_default_setting` | 语义正确性 | 通过 |
| U6 | `test_parent_product_price_is_carried_at_four_places` | 改一查十完备性 | 通过 |
| U7 | `test_unit_tax_rounds_half_up_at_the_fourth_place` | 单轮反幻觉 | 通过 |
| U8 | `test_parent_unit_tax_rounds_half_up_at_the_fourth_place` | 改一查十完备性 | 通过 |
| U9 | `test_gross_amount_at_a_tie_is_half_up_in_the_basket_and_on_the_order` | 改一查十完备性 | 通过 |
| U10 | `test_displayed_amount_is_rounded_half_up` | 改一查十完备性 | 通过 |
| U11 | `test_order_without_offers_stores_cents` | 语义正确性 | 通过 |
| U12 | `test_order_with_percentage_surcharge_adds_up_in_cents` | 改一查十完备性 | 通过 |
| U13 | `test_discounted_shipping_net_charge_rounds_half_up` | 改一查十完备性 | 通过 |
| U14 | `test_percentage_shipping_discount_rounds_half_up` | 改一查十完备性 | 通过 |
| U15 | `test_lines_shown_in_the_basket_add_up_to_the_total_shown` | 单轮反幻觉 | 失败 |
| U16 | `test_lines_shown_add_up_to_the_total_shown_when_they_tie` | 改一查十完备性 | 失败 |
| U17 | `test_order_lines_add_up_to_the_order_total` | 改一查十完备性 | 失败 |
| U18 | `test_order_lines_add_up_to_the_order_total_when_they_tie` | 改一查十完备性 | 失败 |
| U19 | `test_discounted_order_lines_add_up_to_the_order_total` | 语义正确性 | 通过 |
| U20 | `test_single_line_order_agrees_with_its_totals` | 回归安全 | 通过 |
| U21 | `test_price_row_of_single_unit_agrees_with_its_order_line` | 改一查十完备性 | 通过 |
| U22 | `test_batches_settle_to_the_order_line_amount` | 单轮反幻觉 | 失败 |
| U23 | `test_unit_by_unit_settlement_adds_up_to_the_order_line_amount` | 改一查十完备性 | 失败 |
| U24 | `test_settlement_of_a_partly_discounted_line_adds_up` | 改一查十完备性 | 失败 |
| U25 | `test_order_placed_before_the_change_settles_its_remaining_units` | 回归安全 | 通过 |
| U26 | `test_order_placed_before_the_change_settles_in_full` | 回归安全 | 通过 |
| U27 | `test_no_price_change_warning_when_the_price_did_not_change` | 单轮反幻觉 | 失败 |
| U28 | `test_price_change_warning_is_still_reported_for_a_real_change` | 回归安全 | 通过 |
| U29 | `test_discounted_shipping_charge_is_stored_as_shown` | 改一查十完备性 | 通过 |
| U30 | `test_untaxed_strategy_totals_unchanged` | 回归安全 | 通过 |
| U31 | `test_absolute_offer_without_tax_unchanged` | 回归安全 | 通过 |
| U32 | `test_existing_two_place_helper_keeps_its_behaviour` | 回归安全 | 通过 |
| U33 | `test_discounted_shipping_without_tie_unchanged_in_cents` | 回归安全 | 通过 |
| U34 | `test_displayed_amount_format_unchanged_for_ordinary_values` | 回归安全 | 通过 |
| U35 | `test_net_total_is_cents_when_tax_is_not_known` | 边界与异常 | 通过 |
| U36 | `test_fully_discounted_basket_is_zero_not_negative` | 边界与异常 | 通过 |
| U37 | `test_empty_basket_totals_are_zero` | 边界与异常 | 通过 |
| U38 | `test_free_shipping_after_discount_has_no_net_charge` | 边界与异常 | 通过 |
| U39 | `test_indexed_price_is_the_price_shown` | 改一查十完备性 | 通过 |
| U40 | `test_no_price_change_warning_at_a_tie` | 改一查十完备性 | 失败 |
| U41 | `test_batches_settle_to_the_order_line_amount_at_a_tie` | 改一查十完备性 | 失败 |

## 运行环境

```
date_utc: 2026-11-18T15:33:02Z
host_kernel: Linux 5.15.152-amd64 x86_64
docker: 28.5.2
image: cs-xx-001:1.0.0 sha256:375ed9bd8ee332d897b3ddf743d2f3799c4c3132e961ef8878379444c6456d78
image_platform: linux/amd64
interpreter: 3.12.14 Linux-5.15.152-amd64-x86_64-with-glibc2.36 django 5.1.15 pytest 8.4.2
snapshot_commit_in_image: d34ac017e72423af0e99980377d8ef441a2f6c6b
snapshot_tree_in_image: bdea6eaad6894e6167d11d03ae43019d10127467
```
