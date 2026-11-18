"""Hidden unit tests for CS-XX-001.

The task changes how precisely unit prices are carried.  Section A checks the
two reported symptoms and the stated direction: four decimal places inside,
cents outside, always half up.  Section B checks what the task text calls the
two lines that must hold: amounts that describe the same money are the same
number and parts add up to their total, and baskets and orders that existed
before the change can finish their course.  Most of section B passes on the
untouched snapshot and is broken by an incomplete change.  Sections C and D
are regression and boundary checks.

Expected numbers are only asserted where the task text or the documented
behaviour of the snapshot fixes them; everything else is asserted as a
relation between two observed values, so that an implementation is free in
how it gets there.
"""
from decimal import Decimal as D

import pytest
from django.test import override_settings

from cs_helpers import (
    Benefit,
    ReducedRate,
    StockRecord,
    apply_offer,
    basket_with,
    basket_with_products,
    cents,
    flat_shipping,
    four_places,
    make_basket,
    make_offer,
    make_parent_with_child,
    make_product,
    only_line,
    place_order,
    record_settlement,
    reload_basket,
    settle,
    shipping_methods,
    shown,
    stored_order,
    strategy,
)

pytestmark = pytest.mark.django_db

INCL_TAX_OFFERS = override_settings(OSCAR_OFFERS_INCL_TAX=True)


# ---------------------------------------------------------------------------
# A. The reported symptoms and the stated direction
# ---------------------------------------------------------------------------


def test_bulk_small_items_keep_their_tax():
    """U1. 100 x 0.01 at 20%: net 1.00, tax 0.20, gross 1.20.

    Rounding the tax of one unit to cents (0.002 -> 0.00) loses all of it.
    """
    basket, _ = basket_with("0.01", 100)
    assert basket.total_excl_tax == D("1.00")
    assert basket.total_tax == D("0.20")
    assert basket.total_incl_tax == D("1.20")


def test_unit_price_is_carried_at_four_places():
    """U2. 0.99 at 20%: unit tax 0.1980, unit gross 1.1880, not 0.20 / 1.19."""
    product = make_product("0.99")
    price = strategy.UK().fetch_for_product(product).price
    assert four_places(price.tax) == D("0.1980")
    assert four_places(price.incl_tax) == D("1.1880")


def test_tax_of_a_multi_unit_line_is_not_unit_tax_times_quantity():
    """U3. 7 x 0.99 at 20%: net 6.93, tax 1.386 -> 1.39, gross 8.316 -> 8.32.

    Unit tax rounded to cents first gives 7 x 0.20 = 1.40 and 8.33.
    """
    basket, _ = basket_with("0.99", 7)
    assert basket.total_excl_tax == D("6.93")
    assert basket.total_tax == D("1.39")
    assert basket.total_incl_tax == D("8.32")


@INCL_TAX_OFFERS
def test_basket_totals_are_cents_with_percentage_offer_on_gross_prices():
    """U4. The second symptom: 3 x 9.99 with 15% off gross prices.

    gross 3 x 11.988 = 35.964 less 5.3946 = 30.5694 -> 30.57.  The net total
    must be an amount in cents and the three totals must agree.
    """
    basket, _ = basket_with("9.99", 3)
    apply_offer(basket, make_offer(Benefit.PERCENTAGE, "15"))
    assert basket.total_incl_tax == D("30.57")
    assert basket.total_excl_tax == cents(basket.total_excl_tax)
    assert basket.total_incl_tax - basket.total_excl_tax == basket.total_tax


def test_basket_totals_are_cents_with_percentage_offer_default_setting():
    """U5. 3 x 9.99, 15% offer applied to net amounts (the default setting).

    The offer takes 5.3946 (or 5.39 if it is cut to cents first) from the net
    line amount 29.97: 24.5754 or 24.58, both 24.58 in cents.
    """
    basket, _ = basket_with("9.99", 3)
    apply_offer(basket, make_offer(Benefit.PERCENTAGE, "15"))
    assert basket.total_excl_tax == D("24.58")
    assert basket.total_incl_tax == cents(basket.total_incl_tax)
    assert basket.total_incl_tax - basket.total_excl_tax == basket.total_tax


def test_parent_product_price_is_carried_at_four_places():
    """U6. The price shown for a parent product comes from a second code path
    of the same strategy: child at 0.99 -> tax 0.1980, gross 1.1880."""
    parent, _ = make_parent_with_child("0.99")
    price = strategy.UK().fetch_for_parent(parent).price
    assert four_places(price.tax) == D("0.1980")
    assert four_places(price.incl_tax) == D("1.1880")


def test_unit_tax_rounds_half_up_at_the_fourth_place():
    """U7. 0.03 at 17.5% = 0.00525, a tie at the fourth place: half up gives
    0.0053, banker's rounding gives 0.0052."""
    product = make_product("0.03")
    price = ReducedRate().fetch_for_product(product).price
    assert four_places(price.tax) == D("0.0053")


def test_parent_unit_tax_rounds_half_up_at_the_fourth_place():
    """U8. Same tie as U7 through the parent-product path."""
    parent, _ = make_parent_with_child("0.03")
    price = ReducedRate().fetch_for_parent(parent).price
    assert four_places(price.tax) == D("0.0053")


def test_gross_amount_at_a_tie_is_half_up_in_the_basket_and_on_the_order():
    """U9. 1 x 0.60 at 17.5%: tax 0.105, gross 0.7050, a tie at the cent.

    Half up gives 0.71 in the basket.  The order and its line must carry the
    same 0.71; left to the database adapter the stored value is quantized
    with banker's rounding and becomes 0.70.
    """
    basket, _ = basket_with("0.60", 1, ReducedRate())
    assert basket.total_incl_tax == D("0.71")
    order = place_order(basket)
    line = only_line(order)
    assert order.total_incl_tax == D("0.71")
    assert line.line_price_incl_tax == D("0.71")
    assert line.line_price_before_discounts_incl_tax == D("0.71")
    assert line.unit_price_incl_tax == D("0.71")


def test_displayed_amount_is_rounded_half_up():
    """U10. The filter every template uses to show an amount: 0.7050 is shown
    as 0.71, 2.125 as 2.13 and 10.625 as 10.63.  Each is compared with the
    rendering of the cent amount, so the format itself is not pinned here."""
    from oscar.templatetags.currency_filters import currency

    assert currency(D("0.7050")) == currency(D("0.71"))
    assert currency(D("2.125")) == currency(D("2.13"))
    assert currency(D("10.625")) == currency(D("10.63"))


def test_order_without_offers_stores_cents():
    """U11. 3 x 0.99 at 20%: order 2.97 net, 3.564 -> 3.56 gross; the line
    stores unit gross 1.188 -> 1.19 and line gross 3.56 before and after
    discounts."""
    basket, _ = basket_with("0.99", 3)
    order = place_order(basket)
    line = only_line(order)
    assert order.total_excl_tax == D("2.97")
    assert order.total_incl_tax == D("3.56")
    assert line.unit_price_incl_tax == D("1.19")
    assert line.line_price_incl_tax == D("3.56")
    assert line.line_price_before_discounts_incl_tax == D("3.56")


def test_order_with_percentage_surcharge_adds_up_in_cents():
    """U12. 1 x 10.00 (12.00 gross), free shipping, 1.875% surcharge.

    Surcharge 0.225 gross, a tie at the cent: 0.23 half up, 0.22 with
    banker's rounding; 0.1875 -> 0.19 net.  The order total is the basket
    total plus the stored surcharge: 12.23 and 10.19.
    """
    basket, _ = basket_with("10.00", 1)
    order = place_order(basket, surcharge_percentage="1.875")
    surcharge = order.surcharges.get()
    assert surcharge.incl_tax == D("0.23")
    assert surcharge.excl_tax == D("0.19")
    assert order.total_incl_tax == D("12.00") + surcharge.incl_tax
    assert order.total_excl_tax == D("10.00") + surcharge.excl_tax


def test_discounted_shipping_net_charge_rounds_half_up():
    """U13. Shipping 5.00 net / 6.00 gross, an offer sets it to 3.75 gross.

    The method that works out the net charge gets 5.00 x 3.75 / 6.00 = 3.125
    and rounds it: half up gives 3.13, the default of ``quantize`` gives 3.12.
    """
    basket, _ = basket_with("10.00", 1)
    offer = make_offer(Benefit.SHIPPING_FIXED_PRICE, "3.75")
    method = shipping_methods.TaxInclusiveOfferDiscount(flat_shipping("5.00", "6.00"), offer)
    charge = method.calculate(basket)
    assert cents(charge.incl_tax) == D("3.75")
    assert cents(charge.excl_tax) == D("3.13")


def test_percentage_shipping_discount_rounds_half_up():
    """U14. 25% off a 2.50 shipping charge: the method that works out the
    discount gets 0.625 and rounds it: half up gives 0.63, the default of
    ``quantize`` gives 0.62."""
    basket, _ = basket_with("10.00", 1)
    offer = make_offer(Benefit.SHIPPING_PERCENTAGE, "25")
    method = shipping_methods.TaxExclusiveOfferDiscount(flat_shipping("2.50", "3.00"), offer)
    assert cents(method.discount(basket)) == D("0.63")


# ---------------------------------------------------------------------------
# B. The same money is the same number, parts add up, and what was already
#    in the system finishes its course
# ---------------------------------------------------------------------------


def test_lines_shown_in_the_basket_add_up_to_the_total_shown():
    """U15. Two different products at 0.03, 20%: each line is 0.036.

    The basket page shows every line and the total through the same filter.
    Whatever it shows for the two lines must add up to what it shows as the
    total, before and after discounts (there are none here).  Rounding the
    sum once gives 0.07 next to two lines of 0.04.
    """
    basket = basket_with_products(["0.03", "0.03"])
    lines_shown = sum(shown(line.line_price_incl_tax) for line in basket.all_lines())
    assert shown(basket.total_incl_tax_excl_discounts) == lines_shown
    assert shown(basket.total_incl_tax) == lines_shown


def test_lines_shown_add_up_to_the_total_shown_when_they_tie():
    """U16. Two different products at 0.60, 17.5%: each line is 0.7050, a tie
    at the cent.  Lines and total go through the same filter and must agree,
    which they only do if the filter and the total round the same way."""
    basket = basket_with_products(["0.60", "0.60"], ReducedRate())
    lines_shown = sum(shown(line.line_price_incl_tax) for line in basket.all_lines())
    assert shown(basket.total_incl_tax) == lines_shown


def test_order_lines_add_up_to_the_order_total():
    """U17. Order of U15, free shipping: the stored lines add up to the stored
    order total, gross and net, and each stored line is what the basket
    showed for it."""
    basket = basket_with_products(["0.03", "0.03"])
    shown_lines = [shown(line.line_price_incl_tax) for line in basket.all_lines()]
    order = place_order(basket)
    lines = list(order.lines.all())
    assert [line.line_price_incl_tax for line in lines] == shown_lines
    assert order.total_incl_tax == sum(line.line_price_incl_tax for line in lines)
    assert order.total_excl_tax == sum(line.line_price_excl_tax for line in lines)


def test_order_lines_add_up_to_the_order_total_when_they_tie():
    """U18. Order of U16, free shipping: the stored lines add up to the stored
    order total."""
    basket = basket_with_products(["0.60", "0.60"], ReducedRate())
    order = place_order(basket)
    lines = list(order.lines.all())
    assert order.total_incl_tax == sum(line.line_price_incl_tax for line in lines)
    assert order.total_excl_tax == sum(line.line_price_excl_tax for line in lines)


def test_discounted_order_lines_add_up_to_the_order_total():
    """U19. Default strategy (no tax), two different products at 1.00 with a
    15.5% offer, free shipping.  Each line comes to 0.845 (or to 0.85 and
    0.84 if the offer's total is cut to cents and spread).  Either way the
    stored lines must add up to the stored order total."""
    basket = basket_with_products(["1.00", "1.00"], strategy.Default())
    apply_offer(basket, make_offer(Benefit.PERCENTAGE, "15.5"))
    order = place_order(basket)
    lines = list(order.lines.all())
    assert order.total_incl_tax == sum(line.line_price_incl_tax for line in lines)
    assert order.total_excl_tax == sum(line.line_price_excl_tax for line in lines)


@INCL_TAX_OFFERS
def test_single_line_order_agrees_with_its_totals():
    """U20. 5 x 4.00 with 2.25 off each unit on gross prices, free shipping.

    Gross 24.00 - 11.25 = 12.75.  With one line and no shipping the stored
    line amounts are the order totals, and the discount the order reports is
    the stored amount before discounts less the stored amount after.
    """
    basket, _ = basket_with("4.00", 5)
    apply_offer(basket, make_offer(Benefit.FIXED_UNIT, "2.25"))
    order = place_order(basket)
    line = only_line(order)
    assert order.total_incl_tax == D("12.75")
    assert line.line_price_incl_tax == order.total_incl_tax
    assert line.line_price_excl_tax == order.total_excl_tax
    assert order.total_discount_incl_tax == D("24.00") - order.total_incl_tax
    assert order.total_discount_excl_tax == D("20.00") - order.total_excl_tax


@INCL_TAX_OFFERS
def test_price_row_of_single_unit_agrees_with_its_order_line():
    """U21. 1 x 4.00 with 2.25 off on gross prices.  The order line has one
    price row for its single unit: row and line describe the same unit and
    must carry the same gross and the same net amount."""
    basket, _ = basket_with("4.00", 1)
    apply_offer(basket, make_offer(Benefit.FIXED_UNIT, "2.25"))
    line = only_line(place_order(basket))
    rows = list(line.prices.all())
    assert len(rows) == 1
    assert rows[0].price_incl_tax == line.line_price_incl_tax
    assert rows[0].price_excl_tax == line.line_price_excl_tax


def test_batches_settle_to_the_order_line_amount():
    """U22. 100 x 0.01 at 20%, shipped and settled as 30 and then 70 units.

    The two settlements are amounts in cents and together they are the
    amount stored on the order line, which is what the customer was told at
    checkout.  With unit prices of 0.012 stored as 0.01 they come to 1.00
    against a line of 1.20.
    """
    basket, _ = basket_with("0.01", 100)
    order = place_order(basket)
    line = only_line(order)
    amounts = settle(order, line, [30, 70])
    assert all(amount == cents(amount) for amount in amounts)
    assert sum(amounts) == line.line_price_incl_tax


def test_unit_by_unit_settlement_adds_up_to_the_order_line_amount():
    """U23. 7 x 0.99 at 20%, settled one unit at a time: seven amounts in
    cents that add up to the stored line amount (8.32)."""
    basket, _ = basket_with("0.99", 7)
    order = place_order(basket)
    line = only_line(order)
    amounts = settle(order, line, [1] * 7)
    assert all(amount == cents(amount) for amount in amounts)
    assert sum(amounts) == line.line_price_incl_tax


@INCL_TAX_OFFERS
def test_settlement_of_a_partly_discounted_line_adds_up():
    """U24. 5 x 3.33 with 10% off gross prices on at most three units, settled
    as 2 and then 3 units: the settlements add up to the stored line amount."""
    basket, _ = basket_with("3.33", 5)
    apply_offer(basket, make_offer(Benefit.PERCENTAGE, "10", max_affected_items=3))
    order = place_order(basket)
    line = only_line(order)
    amounts = settle(order, line, [2, 3])
    assert all(amount == cents(amount) for amount in amounts)
    assert sum(amounts) == line.line_price_incl_tax


def test_order_placed_before_the_change_settles_its_remaining_units():
    """U25. An order that is already in the database: 5 units, line amount
    18.80, unit price rows 3 x 3.60 and 2 x 4.00, of which the first three
    units were settled for 10.80 before the change.

    Settling the remaining two units must charge 8.00, so that the order ends
    at its stored 18.80.
    """
    order, line = stored_order(5, "18.80", "15.65", "20.00", "16.65",
                               [(3, "3.60", "3.00"), (2, "4.00", "3.33")])
    record_settlement(order, line, 3, "10.80")
    (rest,) = settle(order, line, [2])
    assert rest == D("8.00")
    assert D("10.80") + rest == line.line_price_incl_tax


def test_order_placed_before_the_change_settles_in_full():
    """U26. An order that is already in the database and not yet shipped:
    7 units at a stored unit price of 1.19, line amount 8.33.  Settling it in
    two batches charges 8.33 in total."""
    order, line = stored_order(7, "8.33", "6.93", "8.33", "6.93", [(7, "1.19", "0.99")])
    amounts = settle(order, line, [3, 4])
    assert sum(amounts) == D("8.33")


def test_no_price_change_warning_when_the_price_did_not_change():
    """U27. A pre-existing basket row stores a two-place price.

    The current strategy carries the same unit price at four places, but an
    old row must compare at the persisted cent precision and must not report a
    change merely because the representation gained two extra places.
    """
    basket, _ = basket_with("0.99", 1)
    line = basket.all_lines()[0]
    line.price_incl_tax = D("1.19")
    line.price_excl_tax = D("0.99")
    line.save(update_fields=["price_incl_tax", "price_excl_tax"])
    line = reload_basket(basket).all_lines()[0]
    assert line.get_warning() is None


def test_price_change_warning_is_still_reported_for_a_real_change():
    """U28. A pre-existing cent-priced row still warns for a real change."""
    basket, product = basket_with("0.99", 1)
    line = basket.all_lines()[0]
    line.price_incl_tax = D("1.19")
    line.price_excl_tax = D("0.99")
    line.save(update_fields=["price_incl_tax", "price_excl_tax"])
    StockRecord.objects.filter(product=product).update(price=D("1.09"))
    line = reload_basket(basket).all_lines()[0]
    assert line.get_warning()


def test_discounted_shipping_charge_is_stored_as_shown():
    """U29. Basket 1 x 10.00 with shipping of 5.00 net / 6.00 gross that an
    offer brings to 3.75 gross; the net charge is 3.125, a tie at the cent.

    What checkout shows as the shipping charge is what the order stores, and
    the order total is the stored line plus the stored shipping charge.
    """
    basket, _ = basket_with("10.00", 1)
    offer = make_offer(Benefit.SHIPPING_FIXED_PRICE, "3.75")
    method = shipping_methods.TaxInclusiveOfferDiscount(flat_shipping("5.00", "6.00"), offer)
    charge = method.calculate(basket)
    order = place_order(basket, method)
    line = only_line(order)
    assert order.shipping_incl_tax == shown(charge.incl_tax) == D("3.75")
    assert order.shipping_excl_tax == shown(charge.excl_tax)
    assert order.total_incl_tax == line.line_price_incl_tax + order.shipping_incl_tax
    assert order.total_excl_tax == line.line_price_excl_tax + order.shipping_excl_tax


# ---------------------------------------------------------------------------
# C. Regression safety: behaviour that must stay as it was
# ---------------------------------------------------------------------------


def test_untaxed_strategy_totals_unchanged():
    """U30. Default strategy (no tax), 3 x 9.99: 29.97 net and gross, no tax,
    and the order stores the same."""
    basket, _ = basket_with("9.99", 3, strategy.Default())
    assert basket.total_excl_tax == D("29.97")
    assert basket.total_incl_tax == D("29.97")
    assert basket.total_tax == D("0.00")
    order = place_order(basket)
    assert order.total_excl_tax == D("29.97")
    assert order.total_incl_tax == D("29.97")


def test_absolute_offer_without_tax_unchanged():
    """U31. Default strategy, 2 x 5.00 with 3.00 off: 7.00."""
    basket, _ = basket_with("5.00", 2, strategy.Default())
    apply_offer(basket, make_offer(Benefit.FIXED, "3.00"))
    assert basket.total_excl_tax == D("7.00")
    assert basket.total_incl_tax == D("7.00")


def test_existing_two_place_helper_keeps_its_behaviour():
    """U32. ``oscar.core.utils.round_half_up`` is public and used by projects
    built on this code base: it must still round half up to two places."""
    from oscar.core.utils import round_half_up

    assert round_half_up(D("1.005")) == D("1.01")
    assert round_half_up(D("2.125")) == D("2.13")
    assert round_half_up(D("2.125")).as_tuple().exponent == -2


def test_discounted_shipping_without_tie_unchanged_in_cents():
    """U33. Shipping 4.99 net / 5.99 gross with 1.00 off: 4.99 gross and
    4.99 x 4.99 / 5.99 = 4.1569 -> 4.16 net, as before."""
    basket, _ = basket_with("10.00", 1)
    offer = make_offer(Benefit.SHIPPING_ABSOLUTE, "1.00")
    method = shipping_methods.TaxInclusiveOfferDiscount(flat_shipping("4.99", "5.99"), offer)
    charge = method.calculate(basket)
    assert cents(charge.incl_tax) == D("4.99")
    assert cents(charge.excl_tax) == D("4.16")


def test_displayed_amount_format_unchanged_for_ordinary_values():
    """U34. Amounts that need no rounding are shown as before, and input that
    is not a number still renders as an empty string."""
    from oscar.templatetags.currency_filters import currency

    assert currency(D("10.00")) == "£10.00"
    assert currency(D("1234.5")) == "£1,234.50"
    assert currency(D("0")) == "£0.00"
    assert currency("") == ""
    assert currency(None) == ""


# ---------------------------------------------------------------------------
# D. Boundaries
# ---------------------------------------------------------------------------


def test_net_total_is_cents_when_tax_is_not_known():
    """U35. US strategy (tax decided later), 3 x 9.99 with 10% off the net
    price: 29.97 less 2.997 (or 2.99 if the offer is cut to cents) is 26.97
    or 26.98 in cents, and tax stays unknown."""
    basket, _ = basket_with("9.99", 3, strategy.US())
    apply_offer(basket, make_offer(Benefit.PERCENTAGE, "10"))
    assert basket.is_tax_known is False
    assert basket.total_excl_tax == cents(basket.total_excl_tax)
    assert D("26.97") <= basket.total_excl_tax <= D("26.98")


@INCL_TAX_OFFERS
def test_fully_discounted_basket_is_zero_not_negative():
    """U36. 2 x 0.99 with 100% off on gross prices: every total is 0.00."""
    basket, _ = basket_with("0.99", 2)
    apply_offer(basket, make_offer(Benefit.PERCENTAGE, "100"))
    assert basket.total_incl_tax == D("0.00")
    assert basket.total_excl_tax == D("0.00")
    assert basket.total_tax == D("0.00")


def test_empty_basket_totals_are_zero():
    """U37. An empty basket has totals of zero."""
    basket = make_basket()
    assert basket.total_incl_tax == D("0.00")
    assert basket.total_excl_tax == D("0.00")


def test_free_shipping_after_discount_has_no_net_charge():
    """U38. A shipping offer that brings the charge to 0.00 gross leaves
    0.00 net."""
    basket, _ = basket_with("10.00", 1)
    offer = make_offer(Benefit.SHIPPING_FIXED_PRICE, "0.00")
    method = shipping_methods.TaxInclusiveOfferDiscount(flat_shipping("5.00", "6.00"), offer)
    charge = method.calculate(basket)
    assert charge.incl_tax == D("0.00")
    assert charge.excl_tax == D("0.00")


# ---------------------------------------------------------------------------
# E. Further places that speak of the same money
# ---------------------------------------------------------------------------


def test_indexed_price_is_the_price_shown(monkeypatch):
    """U39. The search index holds a price per product; price ranges, price
    filters and sorting by price work on it.  It was the price shown on the
    product page before the change and has to be that price after it.

    0.99 at 20% is 1.1880 gross, shown as 1.19.  0.60 at 17.5% is 0.7050
    gross, a tie, shown as 0.71.  The same holds for a parent product.
    """
    from oscar.apps.search import search_indexes

    for chosen, net in ((strategy.UK(), "0.99"), (ReducedRate(), "0.60"), (ReducedRate(), "13.70")):
        monkeypatch.setattr(
            search_indexes.Selector, "strategy", lambda self, *args, _chosen=chosen, **kwargs: _chosen
        )
        product = make_product(net)
        price = chosen.fetch_for_product(product).price
        indexed = search_indexes.ProductIndex().prepare_price(product)
        assert D(str(indexed)) == shown(price.incl_tax), net

        parent, _ = make_parent_with_child(net)
        price = chosen.fetch_for_parent(parent).price
        indexed = search_indexes.ProductIndex().prepare_price(parent)
        assert D(str(indexed)) == shown(price.incl_tax), net


def test_no_price_change_warning_at_a_tie():
    """U40. Like U27, with prices whose gross amount is a tie at the cent or
    carries more than two places: nothing changed, so nothing is reported."""
    for net in ("0.60", "0.03", "1.00", "4.20", "0.45", "13.70"):
        basket, _ = basket_with(net, 2, ReducedRate())
        line = reload_basket(basket, ReducedRate()).all_lines()[0]
        assert line.get_warning() is None, net


def test_batches_settle_to_the_order_line_amount_at_a_tie():
    """U41. 3 x 0.60 at 17.5%: the unit gross is 0.7050.  Settled as one unit
    and then two, the amounts are cents and add up to the order line."""
    basket, _ = basket_with("0.60", 3, ReducedRate())
    order = place_order(basket)
    line = only_line(order)
    amounts = settle(order, line, [1, 2])
    assert all(amount == cents(amount) for amount in amounts)
    assert sum(amounts) == line.line_price_incl_tax
