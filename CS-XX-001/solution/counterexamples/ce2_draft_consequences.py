#!/usr/bin/env python3
"""Counterexample 2: what a repository does after only the two changes of the draft.

    python ce2_draft_consequences.py --repo <repository tree>

Run it on the snapshot with tests/calibration/guessed.patch applied (the two
changes of the draft and nothing else) and on the snapshot with the reference
fix.  It makes seven observations and counts how many of them show a defect.
Exit status 0 means at least one defect was observed.

The first four are things that were right before the change and are broken by
it; the fifth and sixth are places where the default rounding is not half up; the
seventh is one more thing that was right before the change, in a part of the
code base that neither the basket nor the order code calls.
"""
import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True)
args = parser.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.abspath(os.path.join(HERE, "..", "..", "tests"))
sys.path.insert(0, TESTS)
sys.path.insert(0, os.path.join(os.path.abspath(args.repo), "src"))
os.environ["DJANGO_SETTINGS_MODULE"] = "cs_settings"

import platform  # noqa: E402
from decimal import Decimal as D  # noqa: E402

import django  # noqa: E402

django.setup()

from django.test.runner import DiscoverRunner  # noqa: E402

runner = DiscoverRunner(verbosity=0, interactive=False)
runner.setup_test_environment()
databases = runner.setup_databases()

import cs_helpers as h  # noqa: E402

print("python", sys.version.split()[0], "| django", django.get_version(), "|", platform.platform())
print("repository:", os.path.abspath(args.repo))
defects = 0


def report(label, observed, defect):
    global defects
    defects += bool(defect)
    print("[%s] %s: %s" % ("DEFECT" if defect else "ok", label, observed))


# 1. price-change warning for a product whose price did not change
basket, _ = h.basket_with("0.99", 1)
warning = h.reload_basket(basket).all_lines()[0].get_warning()
report("warning on an unchanged price", repr(warning), warning is not None)

# 2. 100 x 0.01 at 20%, settled as 30 and then 70 units
basket, _ = h.basket_with("0.01", 100)
order = h.place_order(basket)
line = h.only_line(order)
batches = h.settle(order, line, [30, 70])
report("order line / settled in two batches", "%s / %s = %s" % (
    line.line_price_incl_tax, " + ".join(str(b) for b in batches), sum(batches)),
    sum(batches) != line.line_price_incl_tax)

# 3. two lines of 0.036 each: what the page shows for the lines and for the total
basket = h.basket_with_products(["0.03", "0.03"])
lines = [h.shown(line.line_price_incl_tax) for line in basket.all_lines()]
total = h.shown(basket.total_incl_tax)
report("lines shown / total shown", "%s / %s" % (" + ".join(str(x) for x in lines), total), sum(lines) != total)

# 4. the same basket as an order: stored lines and stored total
order = h.place_order(basket)
stored = [line.line_price_incl_tax for line in order.lines.all()]
report("order lines / order total", "%s / %s" % (" + ".join(str(x) for x in stored), order.total_incl_tax),
       sum(stored) != order.total_incl_tax)

# 5. unit tax at a tie in the fourth place (17.5% of 0.03 = 0.00525)
tax = h.ReducedRate().fetch_for_product(h.make_product("0.03")).price.tax
report("unit tax of 0.03 at 17.5%", tax, h.four_places(tax) != D("0.0053"))

# 6. gross price at a tie in the cent (0.60 at 17.5% = 0.7050): basket, stored line, page
basket, _ = h.basket_with("0.60", 1, h.ReducedRate())
in_basket = basket.total_incl_tax
on_page = h.shown(D("0.7050"))
on_order = h.only_line(h.place_order(basket)).line_price_incl_tax
report("0.7050 in the basket / on the order / on the page", "%s / %s / %s" % (in_basket, on_order, on_page),
       not (in_basket == on_order == on_page == D("0.71")))

# 7. the price the search index holds for a product against the price its page shows
from oscar.apps.search import search_indexes  # noqa: E402

search_indexes.Selector.strategy = lambda self, *args, **kwargs: h.strategy.UK()
product = h.make_product("0.99")
indexed = D(str(search_indexes.ProductIndex().prepare_price(product)))
on_page = h.shown(h.strategy.UK().fetch_for_product(product).price.incl_tax)
report("price of a 0.99 product in the search index / on its page", "%s / %s" % (indexed, on_page),
       indexed != on_page)

runner.teardown_databases(databases)
runner.teardown_test_environment()
print("defects observed: %d of 7" % defects)
sys.exit(0 if defects else 1)
