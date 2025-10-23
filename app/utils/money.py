from decimal import Decimal, InvalidOperation

class MoneyParseError(ValueError):
    pass

MAX_AMOUNT = Decimal("1000000000.00")  # limită „rezonabilă”

def parse_amount(value) -> Decimal:
    try:
        amt = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise MoneyParseError("amount must be a number")
    if amt <= 0:
        raise MoneyParseError("amount must be > 0")
    if amt > MAX_AMOUNT:
        raise MoneyParseError(f"amount must be <= {MAX_AMOUNT}")
    return amt.quantize(Decimal("0.01"))
