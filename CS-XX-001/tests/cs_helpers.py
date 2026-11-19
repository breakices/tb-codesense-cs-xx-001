"""Fixture builders for the hidden unit tests.

They go through the ORM and the public classes only, and do their own
rounding, so that nothing here depends on helper code a submission may have
changed.
"""
import datetime
import itertools
import re
from decimal import ROUND_HALF_UP
from decimal import Decimal as D

from django.utils import timezone

from oscar.core.loading import get_class, get_model

Basket = get_model("basket", "Basket")
Product = get_model("catalogue", "Product")
ProductClass = get_model("catalogue", "ProductClass")
Partner = get_model("partner", "Partner")
StockRecord = get_model("partner", "StockRecord")
Range = get_model("offer", "Range")
Condition = get_model("offer", "Condition")
Benefit = get_model("offer", "Benefit")
ConditionalOffer = get_model("offer", "ConditionalOffer")

Applicator = get_class("offer.applicator", "Applicator")
OrderCreator = get_class("order.utils", "OrderCreator")
OrderTotalCalculator = get_class("checkout.calculators", "OrderTotalCalculator")
EventHandler = get_class("order.processing", "EventHandler")
Order = get_model("order", "Order")
OrderLine = get_model("order", "Line")
PaymentEventType = get_model("order", "PaymentEventType")
PercentageCharge = get_class("checkout.surcharges", "PercentageCharge")
SurchargeList = get_class("checkout.applicator", "SurchargeList")
SurchargePrice = get_class("checkout.applicator", "SurchargePrice")

strategy = __import__("oscar.apps.partner.strategy", fromlist=["x"])
shipping_methods = __import__("oscar.apps.shipping.methods", fromlist=["x"])

_seq = itertools.count(1)


def cents(value):
    """Half-up to two places, computed here rather than by the code under test."""
    return D(value).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def four_places(value):
    """Half-up to four places, computed here rather than by the code under test."""
    return D(value).quantize(D("0.0001"), rounding=ROUND_HALF_UP)


class ReducedRate(
    strategy.UseFirstStockRecord,
    strategy.StockRequired,
    strategy.FixedRateTax,
    strategy.Structured,
):
    """A fixed-rate strategy with a 17.5% rate, built the documented way: by
    subclassing and setting ``rate``."""

    rate = D("0.175")


def _stock(product, price):
    partner, _ = Partner.objects.get_or_create(name="CS partner")
    return StockRecord.objects.create(
        product=product,
        partner=partner,
        partner_sku="cs-sku-%d" % next(_seq),
        price_currency="GBP",
        price=D(price),
        num_in_stock=100000,
    )


def make_product(price, title=None):
    product_class, _ = ProductClass.objects.get_or_create(name="CS goods")
    product = Product.objects.create(
        product_class=product_class, title=title or "Item %d" % next(_seq)
    )
    _stock(product, price)
    return product


def make_parent_with_child(price):
    product_class, _ = ProductClass.objects.get_or_create(name="CS goods")
    parent = Product.objects.create(
        product_class=product_class, structure="parent", title="Parent %d" % next(_seq)
    )
    child = Product.objects.create(
        parent=parent, structure="child", title="Child %d" % next(_seq)
    )
    _stock(child, price)
    return parent, child


def make_basket(strat=None):
    basket = Basket.objects.create()
    basket.strategy = strat or strategy.UK()
    return basket


def reload_basket(basket, strat=None):
    fresh = Basket.objects.get(pk=basket.pk)
    fresh.strategy = strat or strategy.UK()
    return fresh


def basket_with(price, quantity, strat=None):
    basket = make_basket(strat)
    product = make_product(price)
    basket.add_product(product, quantity)
    return basket, product


def stored_basket(net, gross):
    """Persist the historical basket line without invoking current add_product."""
    basket = make_basket()
    product = make_product(net)
    record = StockRecord.objects.get(product=product)
    basket.lines.create(
        line_reference="%s_%s" % (product.pk, record.pk),
        product=product, stockrecord=record, quantity=1, price_currency="GBP",
        price_excl_tax=D(net), price_incl_tax=D(gross),
    )
    return basket, product


def basket_with_products(prices, strat=None):
    """A basket with one line of quantity one for each given price."""
    basket = make_basket(strat)
    for price in prices:
        basket.add_product(make_product(price), 1)
    return basket


def make_offer(benefit_type, value, max_affected_items=None):
    n = next(_seq)
    product_range = Range.objects.create(
        name="CS range %d" % n, includes_all_products=True
    )
    condition = Condition.objects.create(
        range=product_range, type=Condition.COUNT, value=1
    )
    benefit = Benefit.objects.create(
        range=product_range,
        type=benefit_type,
        value=D(value),
        max_affected_items=max_affected_items,
    )
    now = timezone.now()
    return ConditionalOffer.objects.create(
        name="CS offer %d" % n,
        start_datetime=now - datetime.timedelta(days=1),
        end_datetime=now + datetime.timedelta(days=30),
        status=ConditionalOffer.OPEN,
        offer_type=ConditionalOffer.SITE,
        condition=condition,
        benefit=benefit,
    )


def apply_offer(basket, offer):
    Applicator().apply_offers(basket, [offer])
    return basket


def flat_shipping(excl_tax, incl_tax):
    return shipping_methods.FixedPrice(
        charge_excl_tax=D(excl_tax), charge_incl_tax=D(incl_tax)
    )


def place_order(basket, shipping_method=None, surcharge_percentage=None):
    """Place an order the way the checkout does and return it re-read from the
    database, so that the assertions see what was actually stored."""
    method = shipping_method or shipping_methods.Free()
    charge = method.calculate(basket)
    surcharges = None
    if surcharge_percentage is not None:
        surcharge = PercentageCharge(percentage=D(surcharge_percentage))
        surcharges = SurchargeList(
            [
                SurchargePrice(
                    surcharge, surcharge.calculate(basket=basket, shipping_charge=charge)
                )
            ]
        )
    total = OrderTotalCalculator().calculate(
        basket=basket, shipping_charge=charge, surcharges=surcharges
    )
    order = OrderCreator().place_order(
        basket=basket,
        total=total,
        shipping_method=method,
        shipping_charge=charge,
        surcharges=surcharges,
    )
    order.refresh_from_db()
    return order


def only_line(order):
    lines = list(order.lines.all())
    assert len(lines) == 1, "expected a single order line, got %d" % len(lines)
    return lines[0]


def shown(amount):
    """The amount as a customer reads it on a page: what the template filter
    renders for it, read back as a number."""
    from oscar.templatetags.currency_filters import currency

    return D(re.sub(r"[^0-9.]", "", str(currency(amount))))


def settle(order, line, quantities):
    """Settle a line in batches the way a shipment-by-shipment process does:
    ask the event handler what to charge for each batch and record the
    batch.  Returns the amount of each batch."""
    handler = EventHandler()
    kind, _ = PaymentEventType.objects.get_or_create(code="settle", defaults={"name": "Settle"})
    amounts = []
    for quantity in quantities:
        amount = handler.calculate_payment_event_subtotal(kind, [line], [quantity])
        handler.create_payment_event(order, kind, amount, [line], [quantity])
        amounts.append(amount)
    return amounts


def stored_order(quantity, line_incl, line_excl, before_incl, before_excl, rows):
    """An order as it sits in the database from before the change: written
    directly, not through the code under test.  ``rows`` are the unit price
    rows ``(quantity, price_incl_tax, price_excl_tax)``."""
    n = next(_seq)
    partner, _ = Partner.objects.get_or_create(name="CS partner")
    order = Order.objects.create(
        number="OLD%d" % n, currency="GBP", total_incl_tax=D(line_incl), total_excl_tax=D(line_excl)
    )
    line = OrderLine.objects.create(
        order=order, partner=partner, partner_name=partner.name, partner_sku="old-%d" % n,
        title="Stored item %d" % n, quantity=quantity, num_allocated=quantity,
        line_price_incl_tax=D(line_incl), line_price_excl_tax=D(line_excl),
        line_price_before_discounts_incl_tax=D(before_incl),
        line_price_before_discounts_excl_tax=D(before_excl),
    )
    for row_quantity, incl, excl in rows:
        line.prices.create(order=order, quantity=row_quantity, price_incl_tax=D(incl), price_excl_tax=D(excl))
    return order, line


def record_settlement(order, line, quantity, amount):
    """A settlement that already happened before the change."""
    kind, _ = PaymentEventType.objects.get_or_create(code="settle", defaults={"name": "Settle"})
    EventHandler().create_payment_event(order, kind, D(amount), [line], [quantity])
