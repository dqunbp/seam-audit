"""Prices of paid operations, in credits."""
import math

BASE_PRICES = {
    "image": 2,
    "video": 20,
}

# Pro subscribers pay half price (rounded up) for every paid operation.
PRO_DISCOUNT = 0.5


def price_for(kind: str, plan: str) -> int:
    base = BASE_PRICES[kind]
    if plan == "pro":
        return max(1, math.ceil(base * PRO_DISCOUNT))
    return base
