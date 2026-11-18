#!/usr/bin/env python3
"""Counterexample 1: what Decimal.quantize and Django's decimal field do by default.

Needs only Python and Django.  It shows the language and framework behaviour
the draft in the task relies on: quantize without a rounding argument uses the
rounding of the current decimal context, which is ROUND_HALF_EVEN (banker's
rounding), and a DecimalField quantizes a value that has too many places the
same way when it is written.
"""
import decimal
import platform
import sys
from decimal import ROUND_HALF_UP, Decimal as D

print("python", sys.version.split()[0], "|", platform.platform())
print("default context rounding:", decimal.getcontext().rounding)

cases = [
    ("unit tax 0.03 x 17.5%", D("0.03") * D("0.175"), D("0.0001")),
    ("shipping net 5.00 x 3.75 / 6.00", D("5.00") * D("3.75") / D("6.00"), D("0.01")),
    ("shipping discount 2.50 x 25%", D("2.50") * D("25") / D("100"), D("0.01")),
    ("line net 20.00 - 11.25 / 1.2", D("20.00") - D("11.25") / D("1.2"), D("0.01")),
    ("gross 0.60 x 1.175", D("0.60") * D("1.175"), D("0.01")),
]
triggered = 0
for label, value, exponent in cases:
    default = value.quantize(exponent)
    half_up = value.quantize(exponent, rounding=ROUND_HALF_UP)
    differs = default != half_up
    triggered += differs
    print("%-34s exact %-8s quantize() %-7s ROUND_HALF_UP %-7s %s" % (
        label, value.normalize(), default, half_up, "DIFFERENT" if differs else "same"))

try:
    from django.db.backends.utils import format_number
    import django
    stored = format_number(D("0.7050"), 12, 2)
    print("django", django.get_version(), "format_number(0.7050, max_digits=12, decimal_places=2) ->", stored)
    triggered += stored != "0.71"
except ImportError:
    print("django not installed, field adaptation not shown")

print("cases where the default differs from half up: %d" % triggered)
sys.exit(0 if triggered else 1)
